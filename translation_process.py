#!/usr/bin/env python3
"""
プレースホルダー対応翻訳ワークフロー
技術用語を保持しながら翻訳を支援
"""

import ollama
import json
import re
from typing import Dict, List, Optional


class PlaceholderTranslationHelper:
    def __init__(self, model_name: str = "translation-helper"):
        self.model_name = model_name
        self.client = ollama.Client()
    
    def analyze_text(self, text: str) -> Dict:
        """テキストを分析してプレースホルダー形式で出力"""
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": f"Analyze this text: {text}"}
                ],
                options={"temperature": 0.1}
            )
            
            content = response['message']['content']
            
            # JSON部分を抽出
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                # JSONブロックがない場合、直接JSON構造を探す
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    result = json.loads(content[start:end])
                else:
                    raise ValueError("JSON形式が見つかりません")
            
            return {
                "success": True,
                "analysis": result,
                "raw_response": content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "raw_response": content if 'content' in locals() else None
            }
    
    def translate_with_placeholders(self, analysis: Dict, target_language: str = "Japanese") -> Dict:
        """プレースホルダーを含む文章を翻訳"""
        if not analysis.get("success"):
            return {"error": "分析結果が無効です"}
        
        analysis_data = analysis["analysis"]
        translate_texts = analysis_data.get("translate", [])
        keep_mapping = analysis_data.get("keep", {})
        
        translated_texts = []
        
        for text in translate_texts:
            # ここで実際の翻訳を行う（Google Translate API、DeepL API等を使用）
            # この例では簡単な置換として日本語訳を想定
            translated = self.mock_translate(text, target_language)
            translated_texts.append(translated)
        
        return {
            "original_analysis": analysis_data,
            "translated": translated_texts,
            "placeholders": keep_mapping,
            "final_texts": self.restore_placeholders(translated_texts, keep_mapping)
        }
    
    def mock_translate(self, text: str, target_language: str) -> str:
        """モック翻訳（実際の翻訳APIに置き換える）"""
        # 簡単な英日翻訳の例
        translations = {
            "Hello world!": "こんにちは世界！",
            "The {word1} function returns a {word2}": "{word1} 関数は {word2} を返します",
            "The {word1} function returns a {word2} object containing user data.": "{word1} 関数はユーザーデータを含む {word2} オブジェクトを返します。",
            "To install the package, run {word1} {word2}": "パッケージをインストールするには、{word1} {word2} を実行してください",
            "The {word1} endpoint {word2} returns user details in {word3} format.": "{word1} エンドポイント {word2} は {word3} 形式でユーザー詳細を返します。"
        }
        
        return translations.get(text, f"[翻訳: {text}]")
    
    def restore_placeholders(self, translated_texts: List[str], placeholders: Dict[str, str]) -> List[str]:
        """翻訳されたテキストにプレースホルダーから技術用語を復元"""
        restored = []
        
        for text in translated_texts:
            restored_text = text
            for placeholder, technical_term in placeholders.items():
                restored_text = restored_text.replace(f"{{{placeholder}}}", technical_term)
            restored.append(restored_text)
        
        return restored
    
    def process_file(self, file_path: str, output_path: str = None) -> Dict:
        """ファイル全体を処理"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # テキストを段落やセクションに分割
            paragraphs = self.split_into_paragraphs(content)
            
            results = []
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    print(f"処理中: 段落 {i+1}/{len(paragraphs)}")
                    analysis = self.analyze_text(paragraph)
                    
                    if analysis["success"]:
                        translation = self.translate_with_placeholders(analysis)
                        results.append({
                            "paragraph_id": i + 1,
                            "original": paragraph,
                            "analysis": analysis,
                            "translation": translation
                        })
                    else:
                        results.append({
                            "paragraph_id": i + 1,
                            "original": paragraph,
                            "error": analysis["error"]
                        })
            
            # 結果を保存
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            return {"success": True, "results": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """テキストを段落に分割"""
        # 改行で分割し、空行で段落を区切る
        lines = text.split('\n')
        paragraphs = []
        current_paragraph = []
        
        for line in lines:
            if line.strip():
                current_paragraph.append(line)
            else:
                if current_paragraph:
                    paragraphs.append('\n'.join(current_paragraph))
                    current_paragraph = []
        
        if current_paragraph:
            paragraphs.append('\n'.join(current_paragraph))
        
        return paragraphs
    
    def print_analysis_result(self, result: Dict):
        """分析結果の整形表示"""
        if not result["success"]:
            print(f"❌ 分析失敗: {result['error']}")
            return
        
        analysis = result["analysis"]
        
        print("\n" + "="*60)
        print("📊 翻訳分析結果（プレースホルダー形式）")
        print("="*60)
        
        # 翻訳対象文章（プレースホルダー付き）
        translate_texts = analysis.get("translate", [])
        if translate_texts:
            print(f"\n🌐 翻訳対象文章:")
            for i, text in enumerate(translate_texts, 1):
                print(f"   {i}. {text}")
        
        # 技術用語マッピング
        keep_mapping = analysis.get("keep", {})
        if keep_mapping:
            print(f"\n🔒 技術用語マッピング:")
            for placeholder, term in keep_mapping.items():
                print(f"   {placeholder}: {term}")
        
        # 文書情報
        context = analysis.get("context", {})
        if context:
            print(f"\n📄 文書情報:")
            print(f"   種別: {context.get('type', 'N/A')}")
            print(f"   信頼度: {context.get('confidence', 'N/A')}")


def main():
    """メイン実行関数"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="プレースホルダー翻訳支援ツール - テキストファイルを処理します",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        help='処理するテキストファイルのパス'
    )
    
    parser.add_argument(
        '--output',
        help='出力ファイルのパス（指定しない場合は標準出力）'
    )
    
    args = parser.parse_args()
    
    helper = PlaceholderTranslationHelper()
    
    try:
        result = helper.process_file(args.input_file, args.output)
        if result["success"]:
            if args.output:
                print(f"✅ ファイル処理完了: {len(result['results'])}段落処理 -> {args.output}", file=sys.stderr)
            else:
                # 標準出力に結果を出力
                import json
                print(json.dumps(result['results'], ensure_ascii=False, indent=2))
        else:
            print(f"❌ ファイル処理失敗: {result['error']}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
