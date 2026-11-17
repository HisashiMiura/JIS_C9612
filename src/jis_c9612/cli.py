"""コマンドライン (ドキュメント 2 章「実行方法」)。"""

import argparse
import sys
import tomllib
from pathlib import Path

from .apf import compute_apf
from .files import format_summary, load_input, write_csv


def _parser() -> argparse.ArgumentParser:
    """コマンドラインの引数の定義を作る。

    Returns:
        引数の定義
    """
    # 入力ファイルと、2 章「実行方法」のオプションを定義する
    parser = argparse.ArgumentParser(
        prog="jis-c9612",
        description="JIS C 9612:2013 附属書 B による回転数制御形ルームエアコンの APF を計算する。",
    )
    parser.add_argument("input", type=Path, help="入力ファイル (TOML)")
    parser.add_argument("-o", "--output-dir", type=Path, default=None,
                        help="CSV ファイルを保存するディレクトリ (省略すると入力ファイルと同じディレクトリ)")
    parser.add_argument("--no-csv", action="store_true", help="CSV ファイルを保存しない")
    return parser


def main(argv: list[str] | None = None) -> int:
    """入力ファイルを読み込んで APF を計算し、結果を表示・保存する。

    Args:
        argv: コマンドラインの引数。省略するとプログラムの引数を用いる

    Returns:
        終了コード。正常に終われば 0、入力や計算に誤りがあれば 1

    Note:
        2 章「実行方法」「出力」による。
    """
    args = _parser().parse_args(argv)

    # 入力ファイルを読み込んで計算する。誤りがあれば、内容を表示して終了コード 1 で終わる
    try:

        model = load_input(args.input)
        result = compute_apf(model.cooling, model.heating, model.n_c_j, model.n_h_j)

    except (OSError, tomllib.TOMLDecodeError, ValueError) as e:

        print(f"エラー: {args.input}: {e}", file=sys.stderr)
        return 1

    # 要約を画面に表示する
    print(format_summary(model.name, result))

    # CSV ファイルを保存する (保存先を省略したら入力ファイルと同じディレクトリ)
    if not args.no_csv:

        output_dir = args.output_dir if args.output_dir is not None else args.input.parent
        paths = write_csv(result, model.name, output_dir, args.input.stem)
        print("CSV ファイル: " + ", ".join(str(p) for p in paths))

    return 0
