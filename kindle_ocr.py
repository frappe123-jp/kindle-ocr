#!/usr/bin/env python3
"""
Kindleアプリの自動ページめくりとスクリーンショット取得＋PDF化アプリ

macOSでKindleアプリを開き、ページを一枚ずつめくりながら
スクリーンショットを取得し、PDFファイルにまとめます。
"""

import os
import sys
import time
import subprocess
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

# .envファイルの読み込み
try:
    from dotenv import load_dotenv
    # プロジェクトルートの.envファイルを読み込む
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenvがインストールされていない場合はスキップ
    pass

try:
    import pyautogui
    from PIL import Image
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ 必要なパッケージがインストールされていません: {e}")
    print("以下のコマンドでインストールしてください:")
    print("pip install pyautogui pillow google-generativeai")
    sys.exit(1)


class KindlePDF:
    """Kindleアプリの自動ページめくりとスクリーンショット取得＋PDF化・LLM文字起こし処理クラス"""
    
    def __init__(self, output_dir: str = "kindle_pdf_output", api_key: Optional[str] = None, enable_ocr: bool = False):
        """
        初期化
        
        Args:
            output_dir: 出力ディレクトリ
            api_key: Gemini APIキー（LLM文字起こしを使用する場合）
            enable_ocr: LLM文字起こしを有効にするかどうか
        """
        # LLM文字起こしの設定
        self.enable_ocr = enable_ocr
        if self.enable_ocr:
            # APIキーの設定
            self.api_key = api_key or os.getenv('GEMINI_API_KEY')
            if not self.api_key:
                raise ValueError(
                    "LLM文字起こしを有効にするには、Gemini APIキーが必要です。\n"
                    "環境変数 GEMINI_API_KEY を設定するか、--api-key オプションで指定してください。"
                )
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
            print(f"✅ LLM文字起こし機能を有効にしました")
        
        # 出力ディレクトリの設定
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # スクリーンショット保存用ディレクトリ
        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # LLM文字起こし結果保存用ディレクトリ（有効な場合のみ）
        if self.enable_ocr:
            self.texts_dir = self.output_dir / "texts"
            self.texts_dir.mkdir(exist_ok=True)
        
        # pyautoguiの設定
        pyautogui.FAILSAFE = True  # マウスを左上に移動すると緊急停止
        pyautogui.PAUSE = 0.5  # 各操作の間に0.5秒待機
        
        mode_text = "PDF化" if not self.enable_ocr else "PDF化＋LLM文字起こし"
        print(f"✅ Kindle {mode_text}アプリを初期化しました")
        print(f"   出力ディレクトリ: {self.output_dir.absolute()}")
    
    def open_kindle_app(self) -> bool:
        """
        Kindleアプリを開く
        
        Returns:
            成功した場合True
        """
        print("\n📚 Kindleアプリを開いています...")
        
        try:
            # AppleScriptでKindleアプリを開く（複数のアプリ名を試す）
            app_names = ["Kindle", "Amazon Kindle"]
            opened = False
            
            for app_name in app_names:
                try:
                    script = f'''
                    tell application "{app_name}"
                        activate
                    end tell
                    '''
                    subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
                    print(f"✅ Kindleアプリ（{app_name}）を開きました")
                    opened = True
                    break
                except subprocess.CalledProcessError:
                    continue
            
            if not opened:
                # アプリが既に実行中の場合はactivateのみ試す
                try:
                    subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of process "Kindle" to true'], 
                                 check=True, capture_output=True)
                    print("✅ Kindleアプリを前面に表示しました")
                    opened = True
                except:
                    pass
            
            if opened:
                # アプリが起動するまで待機
                time.sleep(3)
                return True
            else:
                print("❌ Kindleアプリを開けませんでした")
                print("   Kindleアプリがインストールされているか確認してください")
                print("   または、--skip-open オプションを使用して手動でKindleアプリを開いてください")
                return False
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            print("   --skip-open オプションを使用して手動でKindleアプリを開いてください")
            return False
        except Exception as e:
            print(f"❌ エラー: {e}")
            return False
    
    def activate_kindle_app(self) -> bool:
        """
        Kindleアプリを前面に表示する
        
        Returns:
            成功した場合True
        """
        try:
            # 複数の方法でKindleアプリを前面に表示
            app_names = ["Kindle", "Amazon Kindle"]
            activated = False
            
            for app_name in app_names:
                try:
                    # 方法1: AppleScriptでactivate
                    script = f'''
                    tell application "{app_name}"
                        activate
                    end tell
                    '''
                    result = subprocess.run(['osascript', '-e', script], check=True, capture_output=True, timeout=5)
                    print(f"  ✅ {app_name}をactivateしました")
                    activated = True
                    break
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    print(f"  ⚠️ {app_name}のactivateに失敗: {e}")
                    continue
            
            # 方法2: System Eventsでプロセスを前面に
            try:
                result = subprocess.run(
                    ['osascript', '-e', 'tell application "System Events" to set frontmost of process "Kindle" to true'],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
                print(f"  ✅ System EventsでKindleを前面に表示しました")
                activated = True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"  ⚠️ System Eventsでの前面表示に失敗: {e}")
            
            # アプリが前面に来るまで少し待機
            time.sleep(1.5)
            
            # 現在アクティブなアプリを確認
            try:
                result = subprocess.run(
                    ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
                    check=True,
                    capture_output=True,
                    timeout=3
                )
                active_app = result.stdout.decode('utf-8').strip()
                print(f"  📱 現在アクティブなアプリ: {active_app}")
                if 'Kindle' in active_app:
                    print(f"  ✅ Kindleアプリがアクティブです")
                else:
                    print(f"  ⚠️ 警告: Kindleアプリがアクティブではありません")
            except Exception as e:
                print(f"  ⚠️ アクティブアプリの確認に失敗: {e}")
            
            return activated
            
        except Exception as e:
            print(f"  ⚠️ Kindleアプリを前面に表示できませんでした: {e}")
            return False
    
    def take_screenshot(self, page_number: int) -> Optional[Path]:
        """
        スクリーンショットを取得
        
        Args:
            page_number: ページ番号
            
        Returns:
            保存されたスクリーンショットのパス
        """
        # スクリーンショット取得前にKindleアプリを前面に表示
        self.activate_kindle_app()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"page_{page_number:04d}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / filename
        
        try:
            # macOSのscreencaptureコマンドを使用
            subprocess.run(
                ['screencapture', '-x', str(screenshot_path)],
                check=True,
                capture_output=True
            )
            print(f"  📸 スクリーンショット保存: {filename}")
            return screenshot_path
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ スクリーンショット取得エラー: {e}")
            return None
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return None
    
    def extract_text_from_image(self, image_path: Path) -> Optional[str]:
        """
        LLM（Gemini）を使って画像からテキストを文字起こし
        
        OCRではなく、LLMの文脈理解能力を使って自然な文章として文字起こしします。
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            文字起こしされたテキスト
        """
        if not self.enable_ocr:
            return None
        
        print(f"  🤖 LLMで文字起こし中...")
        
        try:
            # 画像を読み込んで準備
            with open(image_path, 'rb') as f:
                img = Image.open(f)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 画像サイズが大きい場合はリサイズ（LLMの処理能力を考慮）
                if max(img.size) > 2048:
                    img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                image_data = buffer.getvalue()
            
            # LLMによる文字起こしプロンプト
            prompt_text = """
この画像はKindleアプリのページです。画像内のテキストを、LLMの文脈理解能力を使って自然な文章として文字起こししてください。

【重要な指示】
1. 単純なOCR（文字認識）ではなく、文脈を理解した自然な文章として出力してください
2. 段落構造、見出し、リスト、引用などを適切に認識し、読みやすい形式で出力してください
3. 日本語と英語の両方に対応し、言語の特性を考慮してください
4. タイトルや見出しは適切に識別し、必要に応じてMarkdown形式（#、##、-など）を使用してください
5. ページ番号やフッター情報は除外してください（本文のみ）
6. 誤字脱字があっても、文脈から推測して正しい文章として出力してください
7. 改行や段落の区切りを適切に保持してください

【出力形式】
- 見出しがある場合は「## 見出し」のようにMarkdown形式で出力
- 段落は空行で区切る
- リストは「- 項目」のようにMarkdown形式で出力
- 引用は「> 引用文」のようにMarkdown形式で出力
- 本文のみを出力し、追加の説明やコメントは不要です

テキストのみを出力してください。
            """
            
            response = self.model.generate_content(
                [prompt_text, {"mime_type": "image/jpeg", "data": image_data}]
            )
            
            transcribed_text = response.text.strip()
            print(f"  ✅ 文字起こし完了（{len(transcribed_text)}文字）")
            return transcribed_text
            
        except Exception as e:
            print(f"  ❌ 文字起こしエラー: {e}")
            return None
    
    def save_text(self, text: str, page_number: int) -> Optional[Path]:
        """
        抽出したテキストをファイルに保存
        
        Args:
            text: 抽出されたテキスト
            page_number: ページ番号
            
        Returns:
            保存されたファイルのパス
        """
        if not self.enable_ocr:
            return None
        
        filename = f"page_{page_number:04d}.txt"
        text_path = self.texts_dir / filename
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return text_path
    
    def turn_page(self, direction: str = "next") -> bool:
        """
        ページをめくる（シンプルにスペースキーを使用）
        
        Args:
            direction: "next"（次へ）または "prev"（前へ）
            
        Returns:
            成功した場合True
        """
        # ページめくる前にKindleアプリを前面に表示
        self.activate_kindle_app()
        time.sleep(0.5)  # アプリが前面に来るまで少し待機
        
        try:
            if direction == "next":
                # スペースキーで次ページへ
                print(f"  🔄 スペースキーでページをめくります...")
                pyautogui.press('space')
                print(f"  ✅ スペースキーを送信しました")
                time.sleep(2.0)  # ページが読み込まれるまで待機
                return True
            else:
                # 左矢印キーで前ページへ
                print(f"  🔄 左矢印キーで前ページへ...")
                pyautogui.press('left')
                print(f"  ✅ 左矢印キーを送信しました")
                time.sleep(2.0)
                return True
            
        except Exception as e:
            print(f"  ❌ ページめくりエラー: {e}")
            return False
    
    def create_pdf_from_images(self, image_paths: List[Path], output_filename: str = None) -> Optional[Path]:
        """
        スクリーンショット画像をPDFファイルにまとめる
        
        Args:
            image_paths: 画像ファイルのパスのリスト
            output_filename: 出力PDFファイル名（指定しない場合は自動生成）
            
        Returns:
            生成されたPDFファイルのパス
        """
        if not image_paths:
            print("  ⚠️ PDF化する画像がありません")
            return None
        
        print(f"  📄 {len(image_paths)}枚の画像をPDF化中...")
        
        try:
            # 画像を読み込んでPDFに変換
            images = []
            for img_path in sorted(image_paths):
                try:
                    img = Image.open(img_path)
                    # RGBAモードの場合はRGBに変換（PDFはRGBのみ対応）
                    if img.mode in ('RGBA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            rgb_img.paste(img, mask=img.split()[3])  # アルファチャンネルをマスクとして使用
                        else:
                            rgb_img.paste(img)
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    print(f"  ⚠️ 画像読み込みエラー ({img_path.name}): {e}")
                    continue
            
            if not images:
                print("  ❌ PDF化できる画像がありません")
                return None
            
            # 出力ファイル名を決定
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"kindle_pages_{timestamp}.pdf"
            
            pdf_path = self.output_dir / output_filename
            
            # 最初の画像をベースにしてPDFを作成
            if images:
                images[0].save(
                    pdf_path,
                    "PDF",
                    resolution=100.0,
                    save_all=True,
                    append_images=images[1:] if len(images) > 1 else []
                )
            
            print(f"  ✅ PDF作成完了: {pdf_path.name}")
            print(f"     ページ数: {len(images)}")
            return pdf_path
            
        except Exception as e:
            print(f"  ❌ PDF作成エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_pages(self, num_pages: int, start_page: int = 1, delay_between_pages: float = 3.0):
        """
        複数ページを処理
        
        Args:
            num_pages: 処理するページ数
            start_page: 開始ページ番号（デフォルト: 1）
            delay_between_pages: ページ間の待機時間（秒）
        """
        print(f"\n📖 {num_pages}ページを処理します")
        print(f"   開始ページ: {start_page}")
        print(f"   ページ間の待機時間: {delay_between_pages}秒")
        print(f"\n⚠️  注意: マウスを画面の左上隅に移動すると緊急停止します\n")
        
        # 処理開始前にKindleアプリを前面に表示
        print("📚 Kindleアプリを前面に表示しています...")
        self.activate_kindle_app()
        time.sleep(2)
        
        # 処理開始前のカウントダウン
        print("5秒後に処理を開始します...")
        for i in range(5, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        
        screenshot_paths = []
        
        for i in range(num_pages):
            page_number = start_page + i
            print(f"\n{'='*60}")
            print(f"📄 ページ {page_number}/{start_page + num_pages - 1} を処理中...")
            print(f"{'='*60}")
            
            # スクリーンショット取得
            screenshot_path = self.take_screenshot(page_number)
            if not screenshot_path:
                print(f"  ⚠️ ページ {page_number} のスクリーンショット取得をスキップします")
                continue
            
            screenshot_paths.append(screenshot_path)
            
            # LLM文字起こし処理（有効な場合）
            if self.enable_ocr:
                transcribed_text = self.extract_text_from_image(screenshot_path)
                if transcribed_text:
                    text_path = self.save_text(transcribed_text, page_number)
                    if text_path:
                        print(f"  💾 テキスト保存: {text_path.name}")
            
            # 最後のページでない場合、次のページへ
            if i < num_pages - 1:
                print(f"\n  ⏳ {delay_between_pages}秒待機してから次のページへ...")
                time.sleep(delay_between_pages)
                
                # ページをめくる
                print(f"\n  📖 ページをめくります...")
                if not self.turn_page("next"):
                    print(f"  ⚠️ ページめくりに失敗しました。処理を中断します")
                    break
                
                # ページが完全に読み込まれるまで追加で待機
                print(f"  ⏳ ページの読み込みを待機中...")
                time.sleep(2.0)
                
                # Kindleアプリが確実に前面にあることを確認
                self.activate_kindle_app()
                time.sleep(1.0)
        
        # すべてのスクリーンショットをPDFにまとめる
        print(f"\n{'='*60}")
        print(f"📄 PDFファイルを作成中...")
        print(f"{'='*60}")
        
        pdf_path = self.create_pdf_from_images(screenshot_paths)
        
        # 結果をJSONファイルに保存
        results = {
            'total_pages': len(screenshot_paths),
            'screenshots': [str(p) for p in screenshot_paths],
            'pdf_file': str(pdf_path) if pdf_path else None,
            'ocr_enabled': self.enable_ocr
        }
        
        # LLM文字起こしが有効な場合、テキストファイルの情報も追加
        if self.enable_ocr:
            text_files = []
            for i in range(len(screenshot_paths)):
                page_number = start_page + i
                text_file = self.texts_dir / f"page_{page_number:04d}.txt"
                if text_file.exists():
                    text_files.append(str(text_file))
            results['text_files'] = text_files
        
        results_path = self.output_dir / "results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 処理完了！")
        print(f"{'='*60}")
        print(f"   処理したページ数: {len(screenshot_paths)}/{num_pages}")
        if pdf_path:
            print(f"   PDFファイル: {pdf_path}")
        if self.enable_ocr:
            print(f"   テキストファイル: {self.texts_dir}")
        print(f"   スクリーンショット: {self.screenshots_dir}")
        print(f"   結果ファイル: {results_path}")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Kindleアプリの自動ページめくりとスクリーンショット取得＋PDF化処理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 5ページを処理してPDF化
  python kindle_ocr.py --pages 5
  
  # 10ページを処理、ページ間の待機時間を5秒に設定
  python kindle_ocr.py --pages 10 --delay 5
  
  # カスタム出力ディレクトリを指定
  python kindle_ocr.py --pages 5 --output my_output
        """
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        required=True,
        help='処理するページ数'
    )
    
    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='開始ページ番号（デフォルト: 1）'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=3.0,
        help='ページ間の待機時間（秒、デフォルト: 3.0）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='kindle_pdf_output',
        help='出力ディレクトリ（デフォルト: kindle_pdf_output）'
    )
    
    parser.add_argument(
        '--skip-open',
        action='store_true',
        help='Kindleアプリを開かない（既に開いている場合）'
    )
    
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='LLM文字起こしを有効にする（Gemini APIキーが必要）'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Gemini APIキー（--ocrオプション使用時、環境変数GEMINI_API_KEYからも取得可能）'
    )
    
    args = parser.parse_args()
    
    try:
        # KindlePDFインスタンスを作成
        kindle_pdf = KindlePDF(
            output_dir=args.output,
            api_key=args.api_key,
            enable_ocr=args.ocr
        )
        
        # Kindleアプリを開く（スキップしない場合）
        if not args.skip_open:
            if not kindle_pdf.open_kindle_app():
                print("\n❌ Kindleアプリを開けませんでした。処理を終了します。")
                sys.exit(1)
        
        # ページ処理を実行
        kindle_pdf.process_pages(
            num_pages=args.pages,
            start_page=args.start_page,
            delay_between_pages=args.delay
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって処理が中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
