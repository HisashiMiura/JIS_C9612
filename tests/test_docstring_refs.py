"""ソースに書いた 3 章の式番号が、3 章の今の式の並びと一致するかを確かめる。

ソース (docstring とコメント) には、印刷したドキュメントでも対応が分かるように、
3 章「評価方法」の式を「式 (n)」の番号で書いている。番号は 3 章に式を追加・削除すると
ずれるため、各ファイルが参照する式を、ドキュメントの式のラベル (docs/03_method.md の
`$$ (eq-...)`) で下の EXPECTED に記録しておき、番号と照合する。

ソースの式の参照を追加・変更・削除したときは、EXPECTED も同じ順に直すこと。
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
METHOD = ROOT / "docs" / "03_method.md"
SRC = ROOT / "src" / "jis_c9612"

#: ファイルごとに、ソース中に式番号が現れる順に、その式のラベルを並べたもの。
#: 「式 (2), (3)」はそれぞれの番号 (改行をまたいでもよい)、「式 (65)〜(76)」は両端の番号を数える。
EXPECTED: dict[str, list[str]] = {
    "apf.py": [
        "eq-apf", "eq-apf",
    ],
    "cooling.py": [
        "eq-c-p", "eq-c-cap-ful", "eq-c-pow-ful", "eq-c-cap-haf",
        "eq-c-pow-haf", "eq-c-cap29-ful", "eq-c-pow29-ful", "eq-c-cap29-haf",
        "eq-c-pow29-haf", "eq-c-cap-ful", "eq-c-pow-ful", "eq-c-cap-haf",
        "eq-c-pow-haf", "eq-c-cap29-ful", "eq-c-pow29-ful", "eq-c-cap29-haf",
        "eq-c-pow29-haf", "eq-c-cap-ful", "eq-c-pow-ful", "eq-c-cap-haf",
        "eq-c-pow-haf", "eq-c-load", "eq-c-load", "eq-c-tb",
        "eq-c-tc", "eq-c-tb-def", "eq-c-tc-def", "eq-c-tb",
        "eq-c-tc", "eq-c-l", "eq-c-p", "eq-cspf",
        "eq-cstl", "eq-csec", "eq-c-l", "eq-c-p",
        "eq-c-plf", "eq-c-x", "eq-c-phf", "eq-c-eer-hf",
        "eq-c-eer-haf", "eq-c-eer-ful", "eq-c-cap-ful", "eq-c-pow29-haf",
        "eq-c-tb", "eq-c-tc", "eq-c-eer-haf", "eq-c-eer-ful",
        "eq-c-l", "eq-c-p", "eq-c-load", "eq-c-cap-ful",
        "eq-c-cap-haf", "eq-c-x", "eq-c-plf", "eq-c-p",
        "eq-c-eer-hf", "eq-c-phf", "eq-c-l", "eq-c-p",
        "eq-cstl", "eq-csec", "eq-cspf",
    ],
    "heating.py": [
        "eq-h-p", "eq-h-p-f", "eq-h-cap-ful", "eq-h-pow-ext-f",
        "eq-h-cap2f-ful", "eq-h-pow2-ext", "eq-h-cap-ful", "eq-h-pow-ext-f",
        "eq-h-cap2f-ful", "eq-h-pow2f-ful", "eq-h-capm7-ful", "eq-h-powm7-haf",
        "eq-h-cap2-ful", "eq-h-pow2-haf", "eq-h-cap-ful", "eq-h-pow-haf",
        "eq-h-cap2f-haf", "eq-h-pow2f-haf", "eq-h-cap-haf-f", "eq-h-pow-haf-f",
        "eq-h-cap2f-ful", "eq-h-pow2f-ful", "eq-h-cap-ful-f", "eq-h-pow-ful-f",
        "eq-h-cap2-ext", "eq-h-pow2-ext", "eq-h-capm7-ext", "eq-h-powm7-ext",
        "eq-h-cap-ext", "eq-h-pow-ext", "eq-h-cap-ext-f", "eq-h-pow-ext-f",
        "eq-h-load", "eq-h-load", "eq-h-d", "eq-h-f",
        "eq-h-d", "eq-h-a", "eq-h-h", "eq-h-e",
        "eq-h-g", "eq-h-f", "eq-h-d-def", "eq-h-f-def",
        "eq-h-d", "eq-h-f", "eq-h-cop-ful", "eq-h-cop-ext-f",
        "eq-h-cop-ful", "eq-h-cop-haf", "eq-h-cop-ext", "eq-h-cop-ful-f",
        "eq-h-cop-haf-f", "eq-h-cop-ext-f", "eq-h-cop-ful", "eq-h-cop-ext-f",
        "eq-h-cop-ful", "eq-h-cop-ext-f", "eq-h-cop-hf", "eq-h-cop-hf-f",
        "eq-h-cop-hf", "eq-h-cop-hf-f", "eq-h-cop-fe", "eq-h-cop-fe-f",
        "eq-h-cop-fe", "eq-h-cop-fe-f", "eq-h-p", "eq-h-p-f",
        "eq-h-q", "eq-h-q", "eq-hspf", "eq-hstl",
        "eq-hsec", "eq-h-q", "eq-h-p", "eq-h-p-f",
        "eq-h-plf", "eq-h-plf-f", "eq-h-x", "eq-h-x-f",
        "eq-h-phf", "eq-h-phf-f", "eq-h-pfe", "eq-h-pfe-f",
        "eq-h-prh", "eq-h-prh-f", "eq-h-cap-ful", "eq-h-pow2-ext",
        "eq-h-cop-ful", "eq-h-f", "eq-h-p", "eq-h-p-f",
        "eq-h-load", "eq-h-x", "eq-h-x-f", "eq-h-plf",
        "eq-h-plf-f", "eq-h-p", "eq-h-p-f", "eq-h-phf",
        "eq-h-phf-f", "eq-h-pfe", "eq-h-pfe-f", "eq-h-prh",
        "eq-h-prh-f", "eq-h-p", "eq-h-p-f", "eq-hstl",
        "eq-hsec", "eq-hspf",
    ],
    "lines.py": [
        "eq-c-cap-ful", "eq-c-pow-haf", "eq-h-cap-ful", "eq-h-pow-ext-f",
    ],
}


def _equation_numbers() -> dict[str, int]:
    labels = re.findall(r"^\$\$ \((eq-[\w-]+)\)$", METHOD.read_text(), flags=re.M)
    return {label: i for i, label in enumerate(labels, start=1)}


def _written_numbers(text: str) -> list[int]:
    """ソース中の「式 (2), (3)」「式 (65)〜(76)」などから番号を順に取り出す。"""
    refs = re.finditer(r"式 (\(\d+\)(?:(?:,\s+|〜)\(\d+\))*)", text)
    return [int(n) for m in refs for n in re.findall(r"\d+", m.group(1))]


def test_expected_labels_exist_in_chapter3():
    numbers = _equation_numbers()
    unknown = [(f, lab) for f, labs in EXPECTED.items() for lab in labs if lab not in numbers]
    assert not unknown, f"3 章にないラベル: {unknown}"


def test_source_equation_numbers_match_chapter3():
    numbers = _equation_numbers()
    for path in sorted(SRC.glob("*.py")):
        written = _written_numbers(path.read_text())
        expected = [numbers.get(lab) for lab in EXPECTED.get(path.name, [])]
        assert written == expected, (
            f"{path.name}: ソースの式番号が 3 章と一致しない。\n"
            f"  ソース: {written}\n  3 章  : {expected}"
        )
