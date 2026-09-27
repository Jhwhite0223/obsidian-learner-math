import unittest
from pathlib import Path


SKILL_TEXT = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")


class TestEveningStudyContract(unittest.TestCase):
    def test_evening_study_contract_covers_historical_failures(self):
        required = (
            "\u5148\u8bfb\u53d6\u5df2\u6709\u665a\u81ea\u4e60\u6c47\u603b",
            "\u540c\u4e00\u76ee\u5f55",
            "\u6c47\u603b1",
            "\u56fe\u7247\u5fc5\u987b\u6309\u539f\u6587\u4f4d\u7f6e\u5bf9\u5e94",
            "\u89e3\u91ca\u4e0d\u53d7\u4e94\u6b65\u9650\u5236",
            "\u6bcf\u4e00\u884c\u90fd\u5fc5\u987b\u4ee5 `>` \u5f00\u5934",
            "\u7981\u6b62\u6539\u7528 HTML `<details>`",
            "UTF-8 \u65e0 BOM",
            "\u5199\u5165\u540e\u7acb\u5373\u56de\u8bfb",
            "\u7f16\u7801\u635f\u574f\u4ea7\u751f\u7684 `?`",
            "\u5b8c\u6574 Obsidian \u8def\u5f84",
        )
        for phrase in required:
            self.assertIn(phrase, SKILL_TEXT)


if __name__ == "__main__":
    unittest.main()
