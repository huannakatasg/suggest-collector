import re
import unittest

import classify


class ClassifierVersionTest(unittest.TestCase):
    def test_version_is_exact_classifier_git_revision(self):
        self.assertRegex(classify.CLASSIFIER_VERSION, r"^classify-[0-9a-f]{7,40}$")
        self.assertEqual(classify.CLASSIFIER_VERSION, "classify-dbda6c6")


if __name__ == "__main__":
    unittest.main()
