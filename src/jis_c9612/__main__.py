"""`python -m jis_c9612` で実行したときの入口 (ドキュメント 2 章「実行方法」)。"""

import sys

from .cli import main

# コマンドラインの処理を呼び出し、その終了コードでプログラムを終える
sys.exit(main())
