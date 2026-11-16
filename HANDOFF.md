# 作業引き継ぎメモ

このリポジトリの作業状況・決定事項・次の作業を記録するファイルです。
別の PC で作業を再開するとき、または他の方が作業を分担するときは、最初にこのファイルを読んでください。
作業の区切りごとに「現在の状況」「次の作業」「作業ログ」を更新します。

## プロジェクトの目的

JIS C 9612:2013(ルームエアコンディショナ)に基づき、通年エネルギー消費効率(APF)を計算するプログラムを作成し、
その使い方・評価方法・根拠を Sphinx ドキュメントとしてまとめる。

## 環境構築

```sh
conda env create -f environment.yml   # 初回のみ
conda activate JIS_C9612
cd docs && make html                  # ドキュメントのビルド → docs/_build/html/index.html
```

- Python 3.12
- ドキュメント: Sphinx 8 以上 / MyST Parser / sphinx-book-theme(`docs/requirements.txt`)

## JIS 原本の扱い

- JIS 規格本文は著作物のため **リポジトリには含めない**(`docs/reference/` は `.gitignore` で除外)。
- 作業者は各自で入手したものを `docs/reference/` に置く。
  現在使用しているファイル名: `docs/reference/JIS C9612 2013 ルームエアコンディショナ.pdf`

## リポジトリ構成

| パス | 内容 |
|---|---|
| `src/` | 計算プログラム(未着手) |
| `tests/` | テスト(未着手) |
| `examples/` | 入力例・実行例(未着手) |
| `docs/` | Sphinx ドキュメント |
| `docs/01_introduction.md` | 1. はじめに(目的、対象範囲、用語・記号) |
| `docs/02_usage.md` | 2. プログラムの使い方 |
| `docs/03_method.md` | 3. 評価方法(実装する計算方法) |
| `docs/04_rationale.md` | 4. 評価方法の根拠(JIS の該当条項、独自の解釈とその理由) |
| `environment.yml` | conda 環境定義 |

## 決定事項

- ドキュメントは Sphinx + MyST(Markdown)で書く。テーマは sphinx-book-theme。
- ドキュメントは 4 章構成(上表)。JIS にない独自の追加・解釈は「4. 評価方法の根拠」に内容と理由を記録する。
- コミットは担当者が指示・確認してから行う(Claude に自動でコミットさせない)。

## 現在の状況(2026-11-17 時点)

- ディレクトリ構成、`.gitignore`、Sphinx の骨組み、conda 環境定義まで完了。
- ドキュメント各章は見出しのみで本文は未記入。
- 計算プログラムは未着手。

## 次の作業(候補)

- [ ] 計算プログラムの設計: JIS C 9612:2013 の附属書を読み、冷房期間・暖房期間の計算から APF 算出までの流れを `src/` のモジュール構成に落とし込む
- [ ] 「1. はじめに」の執筆(目的、対象範囲、用語・記号)

## 作業ログ

新しいものを上に追記する。

### 2026-11-17

- `environment.yml`(conda 環境定義)を追加
- Sphinx ドキュメントの骨組みを追加(MyST、sphinx-book-theme、4 章のスタブ)
- `.gitignore` を追加(JIS 原本、`.DS_Store`、ビルド出力、Python キャッシュ)
- `docs/`、`src/`、`tests/`、`examples/` ディレクトリを作成
- 本ファイル `HANDOFF.md` を作成
