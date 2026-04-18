# godot-audit

**言語**:
[English](README.md) ·
[Français](README.fr.md) ·
[Deutsch](README.de.md) ·
[中文](README.zh.md) ·
[日本語](README.ja.md) ·
[Italiano](README.it.md) ·
[Español](README.es.md)

[![Python versions](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml)

あなたの規約に対して Godot プロジェクトのレイアウトを監査します。読み取り専用:ファイルを変更することはありません。

`godot-audit` は、あなたの `.tscn` および `.gd` ファイルが一貫して整理されているか(split または colocated)、アセットのファイル名が snake_case であるか、古い `_old`/`_bak` バージョンが残っていないか、`.uid` / `.import` のコンパニオンファイルが孤立していないかを確認します。ほぼ同一のファイル名(`skeleton` 対 `skeletton` のようなタイプミス)はフラグが立てられますが、番号付きのバリアント(`v1`、`v2` など)は正しく認識されて無視されます。

## 機能

- **2 つのプロジェクトレイアウトをサポート**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd`(Godot のデフォルト文書化された規約)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd`(機能グループ化、デフォルト)
- **6 つのチェックカテゴリ**: mirroring、naming、stale names、near-duplicates、backups、orphan companions。
- **Rich ターミナル出力**、プレーン ANSI へのフォールバック付き。
- **`-h` / `--help` の分離**: 経験豊富なユーザー向けの短いメモ、発見のための例付き完全ドキュメント。
- **CI フレンドリー**: 非ゼロ終了コード、`--no-color`、`--no-rich`、JSON 出力。
- **複数の出力形式**: テキスト(Rich テーブル)、JSON、Markdown。
- **レイアウト対応の提案**: 各警告には具体的な移動提案が付属します。
- **調整可能な命名チェック**: デフォルトで `-` を区切り文字として受け入れ（アセットパックやフォントファミリーでよく使われる）、`--no-dashes` で厳密な snake_case を強制。`--suggested-no-ext` は `Suggested` 列から拡張子を取り除き、Godot の F2 リネームフローに合わせる。
- **反意語を認識する近似重複フィルター**: `--accept-pair` で `checked:unchecked` や `up:down` のような UI トグルペアを宣言し、類似度比だけではタイポと区別できない誤検出を抑制する。

## インストール

GitHub から直接インストール:

```bash
# 最新バージョン
pip install git+https://github.com/olivierpons/godot-audit.git

# 特定のリリースに固定
pip install git+https://github.com/olivierpons/godot-audit.git@v1.2.0
```

これにより `cli-toolkit[rich]` が GitHub リポジトリから自動的に取得されます。

Python 3.14 以上が必要です。

## クイックスタート

```bash
# 現在のディレクトリを監査(デフォルトで colocated レイアウト)
godot-audit

# 特定の Godot プロジェクトを監査
godot-audit ~/godotprojects/my_game

# 代わりに split レイアウトを使用
godot-audit ~/godotprojects/my_game --layout split

# 長いレポートのためサマリーを下部に
godot-audit . --summary-position bottom

# 厳格な CI モード: INFO 問題でもビルドを失敗させる
godot-audit . --strict --no-color --no-rich --quiet

# さらなる処理のために JSON にエクスポート
godot-audit . --format json --output audit.json

# GitHub PR コメント用の Markdown レポート
godot-audit . --format markdown > audit.md

# UI トグルの近似重複の誤検出を抑制
godot-audit . --accept-pair checked:unchecked

# 単一の引数で複数の許可ペアを指定
godot-audit . --accept-pair "(checked:unchecked)(up:down)(open:closed)"

# 厳密な snake_case（ハイフンを拒否）と 'Suggested' での拡張子除去
godot-audit . --no-dashes --suggested-no-ext
```

## オプション

各オプションには短い形式と長い形式があります。`-h` はコンパクトなメモを出力し、`--help` は例付きの完全ドキュメントを出力します。

| 短 | 長 | 説明 |
| --- | --- | --- |
| | `PATH` | Godot プロジェクトルートへのパス(デフォルト:現在のディレクトリ) |
| `-y` | `--layout` | `split` または `colocated`(デフォルト:`colocated`) |
| `-f` | `--format` | `text`、`json`、または `markdown`(デフォルト:`text`) |
| `-o` | `--output` | stdout の代わりにファイルに書き込む |
| `-c` | `--category` | このカテゴリのみ報告(繰り返し可) |
| `-s` | `--severity` | 最低重要度:`INFO`、`WARN`、`ERROR`(デフォルト:`INFO`) |
| `-t` | `--threshold` | 近似重複検出の類似度閾値(デフォルト:`0.88`) |
| `-i` | `--ignore-dir` | 無視リストにディレクトリを追加(繰り返し可) |
| `-k` | `--no-dashes` | ステムで `-` を区切り文字として拒否（デフォルト：受け入れる） |
| `-x` | `--suggested-no-ext` | naming チェックの `Suggested` 列からファイル拡張子を削除 |
| `-A` | `--accept-pair` | 2 つの単語が意味的に異なると宣言（`checked:unchecked`）；繰り返し可能；`/` または `()` で複数ペアをパック可 |
| `-p` | `--summary-position` | `top`、`bottom`、または `none`(デフォルト:`top`) |
| `-S` | `--strict` | INFO 問題でも非ゼロ終了 |
| `-q` | `--quiet` | サマリーパネルを非表示(`-p none` のエイリアス) |
| `-R` | `--no-rich` | プレーンテキスト出力を強制 |
| `-n` | `--no-color` | ANSI カラーを無効化 |
| `-v` | `--verbosity` | 0=silent、1=normal、2=verbose、3=debug |
| `-l` | `--list-categories` | すべてのチェックカテゴリをリストして終了 |
| `-L` | `--list-ignored-dirs` | デフォルトで無視されるディレクトリをリストして終了 |
| `-V` | `--version` | バージョンを表示して終了 |
| `-h` | | 短いヘルプメモ |
| | `--help` | 例付きの完全ヘルプ |

## チェックカテゴリ

| カテゴリ | 検出対象 |
| --- | --- |
| `mirroring` | レイアウト依存。`split`: スクリプトが `scripts/` ルートにあり、シーンが `scenes/<subdir>/` にある。`colocated`: 一致するシーンが異なるディレクトリに存在するスクリプト。 |
| `naming` | snake_case ではないファイル名(スペース、ダッシュ、大文字、特殊文字)。snake_case の代替案を提案。重要度:INFO。 |
| `stale_name` | `_old`、`_bak`、`_backup`、`_copy`、`_tmp`、`_temp`、`_new`、`_todelete`、または `_deprecated` で終わるファイル。昇格または削除。 |
| `near_duplicate` | 同じディレクトリ内でほぼ同一のステムを持つファイルのペア(`skeleton` 対 `skeletton` のようなタイプミスをキャッチ)。番号付きバリアント(`v1`/`v2`、`01`/`02`、`Bird Call 1` / `Bird Call 3`)は自動的にスキップされます。 |
| `backup` | エディタバックアップ: `*.bak`、`*.bak.*`、`*.orig`、`~` で終わる名前。 |
| `orphan_companion` | ソースファイル(`foo.gd`、`bar.mp3`)が欠落している `.uid` または `.import` ファイル。安全に削除可能。 |

## 終了コード

| コード | 意味 |
| --- | --- |
| `0` | 現在の重要度フィルタ以上の問題なし |
| `1` | 少なくとも 1 つの `WARN` または `ERROR` が報告された(または `--strict` が設定されている場合は任意の `INFO`) |
| `2` | 無効な入力: `PATH` が存在しないか、Godot プロジェクトではない |

## レイアウト規約

### Split レイアウト(Godot のデフォルト文書化)

```
res://
├── scenes/
│   ├── entities/
│   │   └── slime.tscn
│   └── levels/
│       └── level_01.tscn
└── scripts/
    ├── entities/
    │   └── slime.gd
    └── levels/
        └── level_01.gd
```

シーンとスクリプトは互いにミラーリングする別々のトップレベルディレクトリに存在します。監査:

```bash
godot-audit . --layout split
```

### Colocated レイアウト(デフォルト、推奨)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # シングルトン、.tscn なし
├── components/       # 再利用可能なロジック、.tscn なし
└── addons/
```

シーンと付属スクリプトが並んで存在します。`autoload/`、`components/`、`addons/` 下のスクリプトは、正当にスクリプトのみなのでコロケーションチェックから免除されます。監査:

```bash
godot-audit .
```

## ファイルを安全に移動する

問題がスクリプトまたはシーンを移動するよう提案するとき、**常に Godot の FileSystem パネルを使用してください**(エディタ内でドラッグ&ドロップ)、コマンドラインでの `mv` は決して使わないでください。Godot は移動時にすべての `.tscn` 参照を書き換えます。OS の `mv` はそうしないため、シーンは存在しないスクリプトを指すことになります。

## 環境変数

| 変数 | 効果 |
| --- | --- |
| `NO_COLOR` | 設定されると、すべての ANSI カラーと Rich スタイリングを無効化します。[no-color.org](https://no-color.org/) を参照。 |

## 開発

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# テスト
pytest

# Lint + フォーマット
ruff check .
ruff format .

# 実際の Godot プロジェクトに対して実行
python -m godot_audit.cli ~/my_godot_project
```

## ライセンス

MIT — [LICENSE](LICENSE) を参照。
