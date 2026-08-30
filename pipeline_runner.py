# -*- coding: utf-8 -*-
"""GitHub Actions runner for Suggest, GSC and SERP with one retry and arrival proof."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
RUNNER_TOKEN = os.environ.get("PIPELINE_RUNNER_TOKEN", "")
TGD_BASE_URL = os.environ.get("TGD_BASE_URL", "https://tgd-suggest.vercel.app").rstrip("/")
ALERT_URL = os.environ.get("PIPELINE_ALERT_URL", f"{TGD_BASE_URL}/api/pipeline/alert")


class PipelineFailure(Exception):
    def __init__(self, status: str, code: str, detail: str, *, http_status: int | None = None, rows_written: int | None = None):
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail
        self.http_status = http_status
        self.rows_written = rows_written


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: object | None = None, timeout: int = 120):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8") or "null")
            return response.status, payload
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"ok": False, "error": raw[:500]}
        return error.code, payload


def supabase_headers(prefer: str | None = None) -> dict[str, str]:
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def require_env() -> None:
    missing = [name for name, value in {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SERVICE_KEY,
        "PIPELINE_RUNNER_TOKEN": RUNNER_TOKEN,
    }.items() if not value]
    if missing:
        raise PipelineFailure("FAILED", "MISSING_SECRET", f"Missing GitHub Secrets: {', '.join(missing)}")


def upsert_run(record: dict) -> str:
    status, rows = request_json(
        f"{SUPABASE_URL}/rest/v1/pipeline_runs?on_conflict=run_key",
        method="POST",
        headers=supabase_headers("resolution=merge-duplicates,return=representation"),
        body=record,
    )
    if status not in range(200, 300) or not isinstance(rows, list) or not rows:
        raise RuntimeError(f"pipeline_runs upsert failed: HTTP {status}")
    return str(rows[0]["id"])


def detect_alerts() -> None:
    status, _ = request_json(
        f"{SUPABASE_URL}/rest/v1/rpc/pipeline_detect_alerts",
        method="POST",
        headers=supabase_headers(),
        body={},
    )
    if status not in range(200, 300):
        raise RuntimeError(f"pipeline detector failed: HTTP {status}")


def try_detect_alerts() -> None:
    try:
        detect_alerts()
    except Exception as error:
        print(f"PIPELINE_DETECTOR_DEGRADED: {error}", file=sys.stderr)


def insert_run_alert(pipeline_run_id: str, source: str, status_name: str, run_key: str, detail: str, http_status: int | None) -> None:
    if http_status is not None and not 200 <= http_status <= 299:
        alert_type = "HTTP_FAILURE"
    elif status_name == "NO_DATA":
        alert_type = "NO_DATA"
    elif status_name == "STALE":
        alert_type = "STALE"
    else:
        alert_type = "FAILED"
    record = {
        "dedupe_key": f"run:{pipeline_run_id}:{alert_type}",
        "pipeline_run_id": pipeline_run_id,
        "source": source,
        "alert_type": alert_type,
        "severity": "WARNING" if status_name == "DEGRADED" else "CRITICAL",
        "message": f"{source.upper()} pipeline {status_name}: {detail}"[:1500],
        "metadata": {"run_key": run_key, "http_status": http_status},
    }
    status, _ = request_json(
        f"{SUPABASE_URL}/rest/v1/pipeline_alerts?on_conflict=dedupe_key",
        method="POST",
        headers=supabase_headers("resolution=merge-duplicates,return=minimal"),
        body=record,
    )
    if status not in range(200, 300):
        raise RuntimeError(f"pipeline alert insert failed: HTTP {status}")


def send_alert(source: str, status_name: str, run_key: str, detail: str) -> None:
    status, payload = request_json(
        ALERT_URL,
        method="POST",
        headers={"Authorization": f"Bearer {RUNNER_TOKEN}", "Content-Type": "application/json"},
        body={"source": source, "status": status_name, "run_key": run_key, "detail": detail},
    )
    if status not in range(200, 300) or not isinstance(payload, dict) or payload.get("ok") is not True:
        raise RuntimeError(f"pipeline alert delivery failed: HTTP {status}")


def mark_source_alerts_delivered(source: str) -> None:
    query = urllib.parse.urlencode({"source": f"eq.{source}", "delivery_status": "eq.PENDING"})
    status, _ = request_json(
        f"{SUPABASE_URL}/rest/v1/pipeline_alerts?{query}",
        method="PATCH",
        headers=supabase_headers("return=minimal"),
        body={"delivery_status": "DELIVERED", "delivered_at": utc_now(), "delivery_error": None},
    )
    if status not in range(200, 300):
        raise RuntimeError(f"pipeline alert acknowledgement failed: HTTP {status}")


def latest_value(table: str, column: str) -> str | None:
    query = urllib.parse.urlencode({"select": column, "order": f"{column}.desc", "limit": "1"})
    status, rows = request_json(f"{SUPABASE_URL}/rest/v1/{table}?{query}", headers=supabase_headers())
    if status not in range(200, 300):
        raise PipelineFailure("FAILED", "DESTINATION_QUERY_FAILED", f"Destination {table} returned HTTP {status}", http_status=status)
    if not rows:
        return None
    return rows[0].get(column)


def suggest_latest() -> str | None:
    status, rows = request_json(
        f"{SUPABASE_URL}/rest/v1/rpc/pipeline_health",
        method="POST",
        headers=supabase_headers(),
        body={},
    )
    if status not in range(200, 300) or not isinstance(rows, list):
        raise PipelineFailure("FAILED", "DESTINATION_QUERY_FAILED", f"pipeline_health returned HTTP {status}", http_status=status)
    match = next((row for row in rows if row.get("key") == "suggest"), None)
    return match.get("latest") if match else None


def run_suggest() -> dict:
    before = suggest_latest()
    process = subprocess.Popen(
        [sys.executable, "collector.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    result = None
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
        if line.startswith("PIPELINE_RESULT="):
            result = json.loads(line.split("=", 1)[1])
    return_code = process.wait()
    if return_code != 0:
        raise PipelineFailure("FAILED", "COLLECTOR_EXIT", f"collector.py exited {return_code}")
    if not isinstance(result, dict):
        raise PipelineFailure("FAILED", "MISSING_RESULT", "collector.py emitted no PIPELINE_RESULT")
    written = int(result.get("rows_written") or 0)
    after = suggest_latest()
    if written <= 0:
        raise PipelineFailure("NO_DATA", "UNEXPECTED_ZERO", "Suggest collector wrote zero new observations", rows_written=0)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if not after or after < today:
        raise PipelineFailure("STALE", "ARRIVAL_NOT_ADVANCED", f"Suggest destination latest={after}, expected at least {today}", rows_written=written)
    status = "SUCCESS" if result.get("rollup_ok") and result.get("prune_ok") else "DEGRADED"
    return {"status": status, "rows_written": written, "before": before, "after": after, "http_status": None, "result": result}


def run_http_pipeline(source: str) -> dict:
    if source == "gsc":
        endpoint, table, column = "/api/gsc/sync", "gsc_queries", "ngay"
    else:
        endpoint, table, column = "/api/competitors/scan", "competitor_serp", "week"
    before = latest_value(table, column)
    if source == "gsc":
        http_status, payload = request_json(
            f"{TGD_BASE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
            timeout=180,
        )
        if http_status not in range(200, 300) or not isinstance(payload, dict) or payload.get("ok") is not True:
            detail = payload.get("error", "HTTP request failed") if isinstance(payload, dict) else "HTTP request failed"
            raise PipelineFailure("FAILED", f"HTTP_{http_status}", str(detail), http_status=http_status)
        written = int(payload.get("written") or 0)
        expected = (payload.get("window") or {}).get("from")
        result_payload = payload
    else:
        written = 0
        expected = None
        summaries = []
        http_status = 200
        for industry in ("hotel", "food", "water", "realestate"):
            query = urllib.parse.urlencode({"industry": industry})
            part_status, payload = request_json(
                f"{TGD_BASE_URL}{endpoint}?{query}",
                headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
                timeout=90,
            )
            if part_status not in range(200, 300) or not isinstance(payload, dict) or payload.get("ok") is not True:
                detail = payload.get("error", "HTTP request failed") if isinstance(payload, dict) else "HTTP request failed"
                raise PipelineFailure(
                    "FAILED",
                    f"HTTP_{part_status}",
                    f"SERP {industry}: {detail}",
                    http_status=part_status,
                    rows_written=written,
                )
            data = payload.get("data") or {}
            part_written = int(data.get("saved") or 0)
            written += part_written
            expected = expected or data.get("week")
            summaries.append({"industry": industry, "rows": int(data.get("rows") or 0), "saved": part_written})
        result_payload = {"week": expected, "industries": summaries}
    after = latest_value(table, column)
    if written <= 0:
        raise PipelineFailure("NO_DATA", "UNEXPECTED_ZERO", f"{source.upper()} endpoint wrote zero rows", http_status=http_status, rows_written=0)
    if not after or (expected and after < expected):
        raise PipelineFailure("STALE", "ARRIVAL_NOT_ADVANCED", f"{source.upper()} destination latest={after}, expected at least {expected}", http_status=http_status, rows_written=written)
    return {"status": "SUCCESS", "rows_written": written, "before": before, "after": after, "http_status": http_status, "result": result_payload}


def as_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    return value if "T" in value else f"{value}T00:00:00Z"


def execute(source: str) -> int:
    started_at = utc_now()
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    run_key = f"{source}:github:{run_id}:{run_attempt}"
    base = {
        "run_key": run_key,
        "source": source,
        "scheduler": "github_actions",
        "status": "RUNNING",
        "attempt_count": 1,
        "started_at": started_at,
        "metadata": {"github_run_id": run_id, "github_run_attempt": run_attempt, "github_job": os.environ.get("GITHUB_JOB")},
        "updated_at": utc_now(),
    }
    pipeline_run_id = upsert_run(base)
    last_error = None
    for attempt in (1, 2):
        try:
            result = run_suggest() if source == "suggest" else run_http_pipeline(source)
            final_status = result["status"]
            final = {
                **base,
                "status": final_status,
                "attempt_count": attempt,
                "finished_at": utc_now(),
                "rows_written": result["rows_written"],
                "destination_latest_before": as_timestamp(result["before"]),
                "destination_latest_after": as_timestamp(result["after"]),
                "http_status": result["http_status"],
                "metadata": {**base["metadata"], "result": result["result"]},
                "updated_at": utc_now(),
            }
            pipeline_run_id = upsert_run(final)
            try_detect_alerts()
            if final_status == "DEGRADED":
                detail = "Data arrived, but a post-write maintenance step failed"
                insert_run_alert(pipeline_run_id, source, final_status, run_key, detail, result["http_status"])
                send_alert(source, final_status, run_key, detail)
                mark_source_alerts_delivered(source)
            print(json.dumps({"run_key": run_key, "pipeline_run_id": pipeline_run_id, "status": final_status, "attempts": attempt, "rows_written": result["rows_written"]}))
            return 0
        except PipelineFailure as error:
            last_error = error
            print(f"[{source}] attempt {attempt}/2: {error.code}: {error.detail}", file=sys.stderr, flush=True)
            if attempt == 1:
                upsert_run({**base, "attempt_count": 2, "updated_at": utc_now()})
                time.sleep(20)

    assert last_error is not None
    final = {
        **base,
        "status": last_error.status,
        "attempt_count": 2,
        "finished_at": utc_now(),
        "rows_written": last_error.rows_written,
        "http_status": last_error.http_status,
        "error_code": last_error.code,
        "error_message": last_error.detail[:1000],
        "updated_at": utc_now(),
    }
    pipeline_run_id = upsert_run(final)
    insert_run_alert(
        pipeline_run_id,
        source,
        last_error.status,
        run_key,
        f"{last_error.code}: {last_error.detail}",
        last_error.http_status,
    )
    try_detect_alerts()
    try:
        send_alert(source, last_error.status, run_key, f"{last_error.code}: {last_error.detail}")
        mark_source_alerts_delivered(source)
    except Exception as alert_error:
        print(f"[{source}] ALERT_DELIVERY_FAILED: {alert_error}", file=sys.stderr)
    print(json.dumps({"run_key": run_key, "pipeline_run_id": pipeline_run_id, "status": last_error.status, "attempts": 2, "error_code": last_error.code}))
    return 1


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"suggest", "gsc", "serp"}:
        print("Usage: python pipeline_runner.py {suggest|gsc|serp}", file=sys.stderr)
        return 2
    require_env()
    return execute(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
