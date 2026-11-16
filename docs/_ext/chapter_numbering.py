"""図・表・コードブロックの番号から章番号を取り除く Sphinx 拡張。

Sphinx の numfig は、numfig_secnum_depth = 1 のとき、番号を
(章番号, 章内の通し番号) の組で振る(例: 表 3.1)。章内の通し番号は
章ごとに 1 から振り直される。この拡張は、番号が決まった直後に
章番号の部分を取り除き、「表 1」「図 1」のように表示させる。

式番号は conf.py の math_numfig = False によって、すでに章ごとに
(1), (2), ... と振られているので、この拡張の対象外である。

注意: 章番号を表示しないため、別の章の図・表を参照すると
「図 1」のように章が分からない表示になる。別の章を参照するときは、
本文で章名も書くこと。
"""

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment


def _strip_chapter_number(app: Sphinx, env: BuildEnvironment) -> list[str]:
    for fignumbers in env.toc_fignumbers.values():
        for figtype_numbers in fignumbers.values():
            for figure_id, number in figtype_numbers.items():
                if len(number) > 1:
                    figtype_numbers[figure_id] = number[-1:]
    return []


def setup(app: Sphinx) -> dict:
    # Sphinx の TocTreeCollector が番号を振った後に実行するため、
    # 既定 (500) より大きい priority で登録する。
    app.connect("env-get-updated", _strip_chapter_number, priority=900)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
