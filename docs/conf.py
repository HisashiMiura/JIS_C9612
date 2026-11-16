# Sphinx configuration for the JIS C 9612 APF evaluation documents.

import sys
from pathlib import Path

# 自作の拡張 (_ext/) を読み込めるようにする
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

project = "JIS C 9612 APF 評価方法"
author = "Hisashi Miura"
copyright = "2026, Hisashi Miura"
release = "0.1"

language = "ja"

extensions = [
    "myst_parser",
    "sphinx.ext.mathjax",
    "chapter_numbering",  # 図・表の番号を章ごとに 1 から、章番号なしで振る
]

source_suffix = {
    ".md": "markdown",
}

# MyST: $...$ / $$...$$ 数式、amsmath 環境、::: フェンスなどを有効化
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

# 式・図・表に番号を振る
numfig = True
# 式番号は章(ページ)ごとに 1 から振り直し、章番号を付けない: (1), (2), ...
math_numfig = False
# 図・表は章ごとに 1 から振り直し、章番号を付けない: 表 1, 図 1, ...
# (numfig_secnum_depth = 1 で章ごとに振り直し、_ext/chapter_numbering.py で章番号を取り除く)
numfig_secnum_depth = 1
math_eqref_format = "式 ({number})"

# reference/ は JIS 原本(著作物)の置き場なのでビルド対象外
exclude_patterns = [
    "_build",
    "reference",
    "Thumbs.db",
    ".DS_Store",
    "requirements.txt",
]

html_theme = "sphinx_rtd_theme"
html_title = project
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "navigation_depth": 3,
}
