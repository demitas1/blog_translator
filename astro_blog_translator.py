"""
Astro Blog Japanese Translator

This script translates English Astro blog markdown files to Japanese using Claude API.
"""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any

import requests


class ClaudeTranslator:
    """Claude API client for translation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    def translate_markdown(self, content: str) -> str:
        """Translate markdown content to Japanese"""
        
        prompt = f"""あなたはAstroブログの英語コンテンツを日本語に翻訳する専門家です。

以下の英語のマークダウンファイルを日本語に翻訳してください：

翻訳の際の注意点：
1. frontmatter（---で囲まれた部分）のキーは英語のまま保持し、値のみを翻訳する
2. マークダウンの構造（見出し、リンク、画像など）は保持する
3. 技術用語は適切な日本語に翻訳するか、必要に応じてカタカナ表記にする
4. 自然で読みやすい日本語に翻訳する
5. HTMLタグやマークダウン記法は変更しない
6. URLやファイルパスはそのまま保持する

翻訳対象の英語マークダウン：

{content}

翻訳された日本語マークダウンのみを出力してください："""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            translated_content = result["content"][0]["text"]
            
            return translated_content.strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid response format from Claude API: {e}")


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api_key' not in config:
            raise ValueError("api_key not found in config file")
        
        return config
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def read_markdown_file(file_path: str) -> str:
    """Read markdown file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"Unable to decode file as UTF-8: {file_path}")


def write_output(content: str, output_path: Optional[str] = None):
    """Write translated content to file or stdout"""
    if output_path:
        try:
            # Create directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Translation saved to: {output_path}", file=sys.stderr)
        except Exception as e:
            raise Exception(f"Failed to write output file: {e}")
    else:
        print(content)


def validate_markdown_frontmatter(content: str) -> bool:
    """Check if content contains valid frontmatter"""
    frontmatter_pattern = r'^---\s*\n.*?\n---\s*\n'
    return bool(re.match(frontmatter_pattern, content, re.DOTALL))


def main():
    parser = argparse.ArgumentParser(
        description="Translate Astro blog markdown files from English to Japanese using Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md --config config.json --output output.md
  %(prog)s input.md --config config.json > output.md
  
Config file format (JSON):
  {
    "api_key": "your-claude-api-key-here"
  }
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input markdown file to translate'
    )
    
    parser.add_argument(
        '--config',
        required=True,
        help='JSON config file containing API keys'
    )
    
    parser.add_argument(
        '--output',
        help='Output markdown file (default: stdout)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.verbose:
            print(f"Loading config from: {args.config}", file=sys.stderr)
        config = load_config(args.config)
        
        # Read input file
        if args.verbose:
            print(f"Reading input file: {args.input_file}", file=sys.stderr)
        content = read_markdown_file(args.input_file)
        
        # Validate frontmatter
        if not validate_markdown_frontmatter(content):
            print("Warning: No frontmatter detected in input file", file=sys.stderr)
        
        # Initialize translator
        translator = ClaudeTranslator(config['api_key'])
        
        # Translate content
        if args.verbose:
            print("Translating content...", file=sys.stderr)
        translated_content = translator.translate_markdown(content)
        
        # Write output
        write_output(translated_content, args.output)
        
        if args.verbose:
            print("Translation completed successfully!", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
