# AIChatBot

AIChatBot は、ユーザーの OpenAI API キーを使って Discord 上で ChatGPT を利用できる Bot です。
構成は「UI層」「AI層」「共通層」に分かれており、将来的な多プラットフォーム対応も可能です。

## 環境変数の設定

1. `.env.example` を `.env` にコピーしてください。
2. 必要なトークン・キーを `.env` に記入してください：
   ### 🔹 Discord Bot Token の取得手順
   1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
   2. 「New Application」からアプリケーションを作成
   3. 左メニュー「Bot」→「Add Bot」でBotを追加
   4. 「Token」→「Reset Token」→ 表示されたトークンをコピー
   5. `.env` の DISCORD_BOT_TOKEN= に貼り付け
   🔒 注意：このトークンは絶対に外部に公開しないでください。
             Gitに含めないよう `.gitignore` で保護します。
   ### 🔹 OpenAI API Key の取得手順
   1. [OpenAI Platform](https://platform.openai.com/account/api-keys) にログイン
   2. 「+ Create new secret key」でAPIキーを生成
   3. 表示された `sk-xxxxx...` 形式のキーをコピー
   4. `.env` の OPENAI_API_KEY= に貼り付け
   🔒 注意：このAPIキーは絶対に外部に公開しないでください。
             Gitに含めないよう `.gitignore` で保護します。

## 起動方法（Discord）

\`\`\`bash
pip install -r requirements.txt
python ui/discord/Discord_AIChatBot.py
\`\`\`
