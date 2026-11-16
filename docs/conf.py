# Sphinx configuration for the JIS C 9612 APF evaluation documents.

project = "JIS C 9612 APF 評価方法"
author = "Hisashi Miura"
copyright = "2026, Hisashi Miura"
release = "0.1"

language = "ja"

extensions = [
    "myst_parser",
    "sphinx.ext.mathjax",
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
math_numfig = True
math_eqref_format = "式({number})"

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
html_theme_options = {
    "navigation_depth": 3,
}
