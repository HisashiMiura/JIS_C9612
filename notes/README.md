# notes

計算プログラム `jis_c9612` を用いた試算と分析の Jupyter Notebook を置く。

| ファイル | 内容 |
|---|---|
| `case_studies.ipynb` | 例の機種について、基準ケースの内訳、入力値の感度、能力の規模、外気温度の分布、最大モードの有無を試算する。結果の図と表を `docs/case_studies/` に保存し、ドキュメント 6 章「試算例」で用いる |

## 実行のしかた

VS Code や Jupyter で開き、カーネルに conda 環境 `JIS_C9612` を選んで、上から順にすべてのセルを実行する。
コマンドで実行する場合は、リポジトリのルートで次のようにする (environment.yml の nbclient を用いる)。

```sh
conda run -n JIS_C9612 python -c "import nbformat; from nbclient import NotebookClient; p='notes/case_studies.ipynb'; nb=nbformat.read(p, 4); NotebookClient(nb, resources={'metadata': {'path': 'notes'}}).execute(); nbformat.write(nb, p)"
```

Notebook を実行し直すと `docs/case_studies/` の図と表が更新される。6 章の本文の数値は手で書いているので、結果が変わったときは本文も直すこと。
