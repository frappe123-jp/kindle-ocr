# Kindle PDF化・LLM文字起こしアプリ

macOSでKindleアプリを開き、ページを自動的にめくりながらスクリーンショットを取得し、PDFファイルにまとめるアプリです。  
**オプションでLLM（Gemini API）による高精度な文字起こしも可能です。**

## 🎯 機能

### 基本機能（PDF化）
- ✅ Kindleアプリの自動起動・前面表示
- ✅ スペースキーによる自動ページめくり
- ✅ スクリーンショットの自動取得
- ✅ 複数ページを1つのPDFファイルにまとめる
- ✅ 処理結果のJSON出力

### オプション機能（LLM文字起こし）
- ✅ LLM（Gemini API）による文脈理解を活用した文字起こし
- ✅ 段落構造、見出し、リストなどを適切に認識
- ✅ Markdown形式での構造化された出力
- ✅ 文字起こししたテキストの自動保存

## 📋 必要な環境

- **macOS**（macOS 10.14以降推奨）
- **Python 3.8以降**
- **Kindleアプリ**（App Storeからインストール）
- **Gemini APIキー**（LLM文字起こし機能を使用する場合のみ）

## 🚀 クイックスタート

### ステップ1: 依存パッケージのインストール

```bash
cd app/kindle_ocr
pip install -r requirements.txt
```

### ステップ2: APIキーの設定（LLM文字起こしを使用する場合のみ）

LLM文字起こし機能を使用する場合は、Gemini APIキーが必要です。

**方法1: 環境変数に設定（推奨）**

```bash
export GEMINI_API_KEY=your_api_key_here
```

**方法2: 実行時にオプションで指定**

```bash
python3 kindle_ocr.py --pages 5 --ocr --api-key YOUR_API_KEY --skip-open
```

**Gemini APIキーの取得方法**:
1. [Google AI Studio](https://aistudio.google.com) にアクセス
2. 「Get API key」をクリック
3. APIキーをコピー

### ステップ3: アクセス許可の設定

macOSでスクリーンショットとキーボード操作を行うため、以下のアクセス許可が必要です：

1. **システム環境設定** → **セキュリティとプライバシー** → **プライバシー**
2. **画面収録** にターミナルまたはPythonを追加
3. **アクセシビリティ** にターミナルまたはPythonを追加

**重要**: 初回実行時にアクセス許可を求められる場合があります。許可してください。

### ステップ4: Kindleアプリの準備

1. Kindleアプリを開く
2. 読みたい本を開く
3. 開始したいページに移動する

### ステップ5: 実行

#### PDF化のみ（LLM文字起こしなし）

```bash
# 5ページを処理してPDF化
python3 kindle_ocr.py --pages 5 --skip-open
```

#### PDF化＋LLM文字起こし

```bash
# 5ページを処理してPDF化＋LLM文字起こし
python3 kindle_ocr.py --pages 5 --ocr --skip-open
```

**`--skip-open`オプション**: Kindleアプリが既に開いている場合は、このオプションを付けると自動起動をスキップします。  
**`--ocr`オプション**: LLM文字起こし機能を有効にします（Gemini APIキーが必要）。

## 📖 使い方

### 基本的な使い方

#### PDF化のみ

```bash
# 5ページを処理してPDF化
python3 kindle_ocr.py --pages 5 --skip-open
```

#### PDF化＋LLM文字起こし

```bash
# 5ページを処理してPDF化＋LLM文字起こし
python3 kindle_ocr.py --pages 5 --ocr --skip-open
```

### オプション一覧

| オプション | 説明 | デフォルト | 例 |
|-----------|------|-----------|-----|
| `--pages` | 処理するページ数（**必須**） | - | `--pages 10` |
| `--start-page` | 開始ページ番号 | 1 | `--start-page 5` |
| `--delay` | ページ間の待機時間（秒） | 3.0 | `--delay 5` |
| `--output` | 出力ディレクトリ名 | `kindle_pdf_output` | `--output my_book` |
| `--skip-open` | Kindleアプリを開かない | False | `--skip-open` |
| `--ocr` | LLM文字起こしを有効にする | False | `--ocr` |
| `--api-key` | Gemini APIキー | 環境変数から取得 | `--api-key YOUR_KEY` |

### 使用例

#### 例1: 基本的な使用（5ページ、PDF化のみ）

```bash
python3 kindle_ocr.py --pages 5 --skip-open
```

#### 例2: PDF化＋LLM文字起こし（5ページ）

```bash
python3 kindle_ocr.py --pages 5 --ocr --skip-open
```

#### 例3: APIキーを指定してLLM文字起こし

```bash
python3 kindle_ocr.py --pages 5 --ocr --api-key YOUR_API_KEY --skip-open
```

#### 例4: 長い本を処理（100ページ、待機時間5秒、LLM文字起こしあり）

```bash
python3 kindle_ocr.py --pages 100 --delay 5 --ocr --skip-open
```

#### 例5: 途中から処理を開始（10ページ目から20ページ）

```bash
python3 kindle_ocr.py --pages 20 --start-page 10 --skip-open
```

#### 例6: カスタム出力ディレクトリ

```bash
python3 kindle_ocr.py --pages 10 --output my_book_pdf --skip-open
```

## 📁 出力ファイル

処理が完了すると、以下のディレクトリ構造でファイルが保存されます：

```
kindle_pdf_output/
├── screenshots/                    # 個別のスクリーンショット画像
│   ├── page_0001_20251229_214750.png
│   ├── page_0002_20251229_214806.png
│   └── ...
├── texts/                          # LLM文字起こし結果（--ocrオプション使用時）
│   ├── page_0001.txt
│   ├── page_0002.txt
│   └── ...
├── kindle_pages_20251229_214822.pdf  # まとめたPDFファイル
└── results.json                      # 処理結果のJSONファイル
```

### results.json の構造

#### PDF化のみの場合

```json
{
  "total_pages": 5,
  "screenshots": [
    "kindle_pdf_output/screenshots/page_0001_20251229_214750.png",
    "kindle_pdf_output/screenshots/page_0002_20251229_214806.png",
    ...
  ],
  "pdf_file": "kindle_pdf_output/kindle_pages_20251229_214822.pdf",
  "ocr_enabled": false
}
```

#### PDF化＋LLM文字起こしの場合

```json
{
  "total_pages": 5,
  "screenshots": [
    "kindle_pdf_output/screenshots/page_0001_20251229_214750.png",
    "kindle_pdf_output/screenshots/page_0002_20251229_214806.png",
    ...
  ],
  "pdf_file": "kindle_pdf_output/kindle_pages_20251229_214822.pdf",
  "ocr_enabled": true,
  "text_files": [
    "kindle_pdf_output/texts/page_0001.txt",
    "kindle_pdf_output/texts/page_0002.txt",
    ...
  ]
}
```

## ⚙️ 処理の流れ

1. **Kindleアプリを前面に表示**
   - AppleScriptでKindleアプリをアクティブ化

2. **スクリーンショット取得**
   - macOSの`screencapture`コマンドでスクリーンショットを取得
   - `screenshots/`ディレクトリに保存

3. **LLM文字起こし（`--ocr`オプション使用時）**
   - Gemini APIでスクリーンショットからテキストを抽出
   - 文脈を理解した自然な文章として文字起こし
   - `texts/`ディレクトリに保存

4. **ページをめくる**
   - スペースキーを送信して次ページへ
   - ページが読み込まれるまで待機（約2秒）

5. **繰り返し**
   - 指定したページ数まで繰り返し

6. **PDF化**
   - すべてのスクリーンショットを1つのPDFファイルにまとめる

## ⚠️ 注意事項

### 1. 緊急停止機能

マウスを画面の**左上隅**に移動すると処理が緊急停止します（pyautoguiのフェイルセーフ機能）。

### 2. Kindleアプリの準備

- 処理を開始する前に、Kindleアプリで読みたい本を開いておいてください
- 開始ページが正しい位置にあることを確認してください
- Kindleアプリが前面に表示されていることを確認してください

### 3. ページめくりのタイミング

- デフォルトでは、各ページの間に3秒の待機時間があります
- ページが完全に読み込まれるまで追加で2秒待機します
- LLM文字起こしを使用する場合、追加で数秒かかります（APIの応答時間による）
- 合計で約6秒/ページ（PDF化のみ）または10-15秒/ページ（LLM文字起こしあり）の処理時間がかかります

### 4. LLM文字起こし機能について

- **APIキーが必要**: `--ocr`オプションを使用する場合は、Gemini APIキーが必要です
- **API使用量**: Gemini APIの使用量に注意してください
- **処理時間**: LLM文字起こしは追加の処理時間がかかります
- **精度**: OCRよりも高精度で、文脈を理解した自然な文章として出力されます

### 5. アクセス許可

macOSのセキュリティ設定で、以下のアクセス許可が必要です：
- **画面収録**: スクリーンショット取得のため
- **アクセシビリティ**: キーボード操作（スペースキー）のため

初回実行時にアクセス許可を求められる場合があります。

## 🔧 トラブルシューティング

### Kindleアプリが開かない

**症状**: `❌ Kindleアプリを開けませんでした` というエラーが表示される

**解決方法**:
1. Kindleアプリがインストールされているか確認
2. App StoreからKindleアプリをインストール
3. `--skip-open`オプションを使用して、手動でKindleアプリを開いてから実行

```bash
# 手動でKindleアプリを開いてから実行
python3 kindle_ocr.py --pages 5 --skip-open
```

### スクリーンショットが取得できない

**症状**: `❌ スクリーンショット取得エラー` というエラーが表示される

**解決方法**:
1. システム環境設定 → セキュリティとプライバシー → プライバシー
2. **画面収録**にターミナルまたはPythonを追加
3. ターミナルを再起動してから再度実行

### ページがめくれない

**症状**: ページが変わらない、同じページのスクリーンショットが取得される

**解決方法**:
1. Kindleアプリがアクティブ（前面）になっているか確認
2. システム環境設定 → セキュリティとプライバシー → プライバシー
3. **アクセシビリティ**にターミナルまたはPythonを追加
4. `--delay`オプションで待機時間を長くする

```bash
# 待機時間を5秒に延長
python3 kindle_ocr.py --pages 5 --delay 5 --skip-open
```

### 処理が途中で止まる

**症状**: 指定したページ数より少ないページで処理が終了する

**確認事項**:
1. ログに「⚠️ ページめくりに失敗しました。処理を中断します」と表示されていないか確認
2. Kindleアプリが前面に表示されているか確認
3. マウスが左上隅に移動していないか確認（フェイルセーフ機能）

### LLM文字起こしが失敗する

**症状**: `❌ 文字起こしエラー` というエラーが表示される

**解決方法**:
1. Gemini APIキーが正しく設定されているか確認
2. 環境変数 `GEMINI_API_KEY` が設定されているか確認
3. `--api-key` オプションでAPIキーを指定
4. APIのレート制限に達していないか確認
5. インターネット接続を確認

## 💡 ヒント

### 効率的な使い方

1. **待機時間の調整**: ページが読み込まれるのに時間がかかる場合は、`--delay`を長くする
   ```bash
   python3 kindle_ocr.py --pages 10 --delay 5 --skip-open
   ```

2. **大量のページを処理**: 100ページ以上を処理する場合は、待機時間を長めに設定
   ```bash
   python3 kindle_ocr.py --pages 100 --delay 5 --skip-open
   ```

3. **途中から再開**: 処理が途中で止まった場合、`--start-page`で続きから再開
   ```bash
   # 10ページ目から20ページ処理
   python3 kindle_ocr.py --pages 20 --start-page 10 --skip-open
   ```

### 出力ファイルの確認

処理が完了したら、以下のコマンドでPDFファイルを確認できます：

```bash
# PDFファイルを開く（macOS）
open kindle_pdf_output/kindle_pages_*.pdf

# または、最新のPDFファイルを開く
open $(ls -t kindle_pdf_output/*.pdf | head -1)
```

## 📝 使用例（完全版）

### 初めて使う場合の手順（PDF化のみ）

1. **依存パッケージをインストール**
   ```bash
   cd app/kindle_ocr
   pip install -r requirements.txt
   ```

2. **アクセス許可を設定**
   - システム環境設定 → セキュリティとプライバシー → プライバシー
   - 「画面収録」と「アクセシビリティ」にターミナルを追加

3. **Kindleアプリを開く**
   - Kindleアプリを起動
   - 読みたい本を開く
   - 開始したいページに移動

4. **実行**
   ```bash
   python3 kindle_ocr.py --pages 5 --skip-open
   ```

5. **結果を確認**
   ```bash
   # PDFファイルを開く
   open kindle_pdf_output/kindle_pages_*.pdf
   ```

### LLM文字起こし機能を使う場合の手順

1. **依存パッケージをインストール**（上記と同じ）

2. **APIキーを設定**
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

3. **アクセス許可を設定**（上記と同じ）

4. **Kindleアプリを開く**（上記と同じ）

5. **実行（LLM文字起こしあり）**
   ```bash
   python3 kindle_ocr.py --pages 5 --ocr --skip-open
   ```

6. **結果を確認**
   ```bash
   # PDFファイルを開く
   open kindle_pdf_output/kindle_pages_*.pdf
   
   # 文字起こし結果を確認
   cat kindle_pdf_output/texts/page_0001.txt
   ```

## 🔗 関連リンク

- [pyautogui ドキュメント](https://pyautogui.readthedocs.io/)
- [Pillow ドキュメント](https://pillow.readthedocs.io/)
- [Kindleアプリ（App Store）](https://apps.apple.com/jp/app/kindle/id405399194)

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
