import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
CONTRACT_TEXT = (SKILL_ROOT / "references" / "vault-contract.md").read_text(encoding="utf-8")


class TestFormulaContract(unittest.TestCase):
    def test_skill_defines_compact_mathjax_rendering_contract(self):
        required = (
            "数学公式显示契约",
            "短公式才使用行内",
            "复杂公式一律使用独立公式块",
            "像素级布局不保证",
            "![[高数公式库#^",
            "块引用必须使用 `#^`",
        )
        for phrase in required:
            self.assertIn(phrase, SKILL_TEXT)

    def test_vault_reference_defines_formula_library_and_fallback(self):
        required = (
            "公式库",
            "UTF-8",
            "MathJax",
            "\u6e32\u67d3\u5931\u8d25",
            "\u8868\u683c",
        )
        for phrase in required:
            self.assertIn(phrase, CONTRACT_TEXT)


if __name__ == "__main__":
    unittest.main()
