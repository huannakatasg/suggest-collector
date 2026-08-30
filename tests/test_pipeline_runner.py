import unittest
from unittest import mock

import pipeline_runner


class PipelineRunnerTest(unittest.TestCase):
    def test_date_is_promoted_to_timestamp(self):
        self.assertEqual(pipeline_runner.as_timestamp("2026-08-31"), "2026-08-31T00:00:00Z")

    @mock.patch.object(pipeline_runner, "time")
    @mock.patch.object(pipeline_runner, "mark_source_alerts_delivered")
    @mock.patch.object(pipeline_runner, "send_alert")
    @mock.patch.object(pipeline_runner, "detect_alerts")
    @mock.patch.object(pipeline_runner, "upsert_run", return_value="run-id")
    @mock.patch.object(pipeline_runner, "run_http_pipeline")
    def test_failure_retries_once_and_records_final_status(
        self, run_http, upsert, _detect, _send, _mark, _time
    ):
        run_http.side_effect = pipeline_runner.PipelineFailure(
            "FAILED", "HTTP_503", "source is not configured", http_status=503
        )
        with mock.patch.dict(pipeline_runner.os.environ, {"GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}):
            self.assertEqual(pipeline_runner.execute("gsc"), 1)
        self.assertEqual(run_http.call_count, 2)
        final_record = upsert.call_args_list[-1].args[0]
        self.assertEqual(final_record["status"], "FAILED")
        self.assertEqual(final_record["attempt_count"], 2)
        self.assertEqual(final_record["http_status"], 503)


if __name__ == "__main__":
    unittest.main()
