# RCGS to MAdB Converter

RCGSコレクションのダンプデータをrdflibでインポートして、rdflibのAPIで取得、メディア芸術データベース（MAdB）に登録するための原データに変換するツールです。

## 概要

このツールは、[RCGSコレクション](https://collection.rcgs.jp/dumps/)から提供されるRDFダンプデータを読み込み、メディア芸術データベース（MAdB）で利用可能なCSV形式に変換します。

## データソース

- **データ提供元**: [RCGSコレクション](https://collection.rcgs.jp/dumps/)
- **データ形式**: RDF/XML (.xml)
- **利用可能なダンプファイル**:
  - rcgs-all-20200330.xml.zip (9.1M)
  - rcgs-all-20200403.xml.zip (9.3M)
  - rcgs-all-20210218.xml.zip (8.7M)
  - rcgs-all-20220209.xml.zip (12M)
  - rcgs-all-20230207.xml.zip (10M)

## 機能

### 抽出されるデータタイプ

1. **ゲームパッケージ（Package）**
   - ゲームソフトウェアの基本情報
   - プラットフォーム、価格、識別子など

2. **個別資料（Item）**
   - 図書館所蔵の個別資料情報
   - 所蔵機関、識別子、空間情報など

3. **個人（Person）**
   - ゲーム開発者、制作者の情報
   - 名前、識別子、経歴など

4. **団体（Organization）**
   - ゲーム会社、開発スタジオの情報
   - 組織名、識別子、所在地など

5. **バリエーション（Variation）**
   - ゲームのバリエーション情報
   - プラットフォーム別、地域別の違いなど

6. **作品（Work）**
   - ゲーム作品の基本情報
   - タイトル、ジャンル、シリーズ情報など

7. **関連資料（Related Item）**
   - ゲームに関連する資料情報
   - マニュアル、ガイドブックなど

### 技術的特徴

- **軽量アプローチ**: 重いSPARQLクエリの代わりにrdflibのAPIを使用
- **効率的な処理**: 大量データでも安定動作
- **複雑な構造対応**: ネストしたRDF構造も適切に処理
- **言語対応**: 日本語・英語の言語別データを適切に分離

## 必要な環境

### Python パッケージ

```bash
pip install rdflib pandas
```

### ディレクトリ構造

```
rcgs_to_madb/
├── convert.py          # メイン変換スクリプト
├── README.md           # このファイル
├── source/             # RDFファイル配置ディレクトリ
│   ├── rcgs-all-20230207.xml
│   └── ...
└── output/             # 出力CSVファイルディレクトリ（自動作成）
    ├── game_packages.csv
    ├── items.csv
    ├── persons.csv
    ├── organizations.csv
    ├── variations.csv
    ├── works.csv
    └── related_items.csv
```

## 使用方法

### 1. データの準備

1. [RCGSコレクション](https://collection.rcgs.jp/dumps/)からダンプファイルをダウンロード
2. ファイルを解凍して`./source`ディレクトリに配置

```bash
# ディレクトリ作成
mkdir -p rcgs_to_madb/source

# ダンプファイルを配置（例）
cp rcgs-all-20230207.xml rcgs_to_madb/source/
```

### 2. 変換の実行

```bash
cd rcgs_to_madb
python convert.py
```

### 3. 出力ファイル

実行後、以下のCSVファイルが`./output`ディレクトリに生成されます：

- **`game_packages.csv`** - ゲームパッケージデータ
- **`items.csv`** - 個別資料データ
- **`persons.csv`** - 個人データ
- **`organizations.csv`** - 団体データ
- **`variations.csv`** - バリエーションデータ
- **`works.csv`** - 作品データ
- **`related_items.csv`** - 関連資料データ

## 出力例

```
RDFファイルの読み込みを開始: ./source
読み込み中: ./source/rcgs-all-20230207.xml
  成功: 150000 トリプルを読み込み

=== データ統計 ===
BibResource数: 0
Item数: 20120
Package数: 5000
Person数: 2146
Organization数: 1500
Variation数: 3000
Work数: 8000

=== CSV出力開始 ===
=== ゲームパッケージデータの抽出開始 ===
ゲームパッケージ数: 5000
抽出完了: 5000 件のゲームパッケージデータ
CSVファイルを保存: ./output/game_packages.csv
  行数: 5000
  列数: 65

=== 個別資料データの抽出開始 ===
個別資料数: 20120
抽出完了: 20120 件の個別資料データ
CSVファイルを保存: ./output/items.csv
  行数: 20120
  列数: 6

処理が完了しました。
```

## データ構造

### 主要な名前空間

- **rcgs**: `https://collection.rcgs.jp/terms/` - RCGS固有の語彙
- **schema**: `http://schema.org/` - Schema.org語彙
- **dcterms**: `http://purl.org/dc/terms/` - Dublin Core語彙
- **foaf**: `http://xmlns.com/foaf/0.1/` - FOAF語彙
- **skos**: `http://www.w3.org/2004/02/skos/core#` - SKOS語彙
- **dcndl**: `http://ndl.go.jp/dcndl/terms/` - NDL固有の語彙

### 複雑な構造の処理

- **複数値**: `|`で区切って格納
- **言語別データ**: 日本語（ja-Hrkt, ja-Latn）、英語（en）を適切に分離
- **ネスト構造**: `dcterms:format`、`rcgs:provisionActivity`などの複雑な構造を適切に展開

## 注意事項

- 大量データの処理には時間がかかる場合があります
- メモリ使用量に注意してください（推奨: 8GB以上）
- 出力ファイルはUTF-8エンコーディングで保存されます

## ライセンス

このツールは、RCGSコレクションのデータを適切に変換するためのものです。データの利用については、[RCGSコレクション](https://collection.rcgs.jp/)の利用規約に従ってください。

## 更新履歴

- **2024年6月17日**: 初版リリース
  - 7つのデータタイプの抽出機能を実装
  - rdflib APIを使用した軽量アプローチを採用
  - 複雑なRDF構造の適切な処理を実装 