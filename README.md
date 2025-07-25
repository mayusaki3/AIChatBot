# AIChatBot

AIChatBot は、ユーザーの OpenAI API キーを使って Discord 上で ChatGPT を利用できる Bot です。  
構成は「UI層」「AI層」「共通層」に分かれており、将来的な多プラットフォーム対応を想定しています。

## 環境変数の設定（Discord用）

1. `.env.example` を `.env` にコピーしてください。
2. 必要な トークン・ID を `.env` に記入してください：
   ### 🔹 Discord Bot Token の取得手順
   1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
   2. 「New Application」からアプリケーションを作成
   3. 左メニュー「Bot」→「Add Bot」でBotを追加
   4. 「Token」→「Reset Token」→ 表示されたトークンをコピー
   5. `.env` の DISCORD_BOT_TOKEN= に貼り付け  
   🔒 注意：このトークンは絶対に外部に公開しないでください。Gitに含めないよう `.gitignore` で保護します。

   ### 🔹 Discord Guild ID の取得手順（開発時のみ）
   1. DiscordクライアントでDiscordにアクセス
   2. ユーザー設定 → 詳細設定 → 「開発者モード」を有効化
   3. 対象のサーバー名を右クリック → 「IDをコピー」
   4. `.env` の DISCORD_GUILD_ID= に貼り付け

## 起動方法

```shell
pip install -r requirements.txt  # 初回のみ
python ui/discord/Discord_AIChatBot.py
```

## /コマンド一覧（Discord）

AIChatBot は以下の /コマンドを提供しています：

| 基本コマンド                   | 説明                                                                   |
|--------------------------------|------------------------------------------------------------------------|
| `/ac_help`                     | すべての /ac コマンドのヘルプを表示します。                            |
| `/ac_template`                 | 認証情報設定用テンプレート（JSON）をダウンロードします。               |
| `/ac_auth [file]`              | 使用するAIチャットの認証情報を登録します。 [*1]                        |
| `/ac_removeauth`               | 登録したAIチャットの認証情報を削除します。 [*1]                        |
| `/ac_authsharing`              | 認証情報が未登録の人に現在の認証情報をサーバー単位で共有します。 [*1]  |
| `/ac_authunsharing`            | サーバー単位で共有されている認証情報の共有を解除します。 [*1]          |
| `/ac_imageuse`                 | 使用中のモデルに画像対応マークを付けます。 [*2]                        |
| `/ac_imagenonuse`              | 使用中のモデルに画像非対応マークを付けます。 [*2]                      |
| `/ac_status`                   | 使用中のAIチャットの状態を表示します。                                 |
| `/ac_threads`                  | AIチャットと会話中のスレッド一覧を表示します。                         |
| `/ac_newchat [title] [Private]`| 新しいAIチャットスレッドを作成します（件名は任意）                     |

[*1]: 認証情報は「自分の認証情報」＞「共有された認証情報」の順に使用します。自分の認証情報のみ共有でき、誰の認証情報でも共有解除できます。
[*2]: 画像対応マークがついているモデルとのチャットでは、添付された画像も送信します。

| スレッド内コマンド             | 説明                                                                   |
|--------------------------------|------------------------------------------------------------------------|
| `/ac_invite`                   | AIChatBotを現在のスレッドに招待します。                                |
| `/ac_leave`                    | AIChatBotを現在のスレッドから退出させます。                            |
| `/ac_newtopic`                 | 新しくトピックを始めます。以前の会話内容は忘れます。                   |
| `/ac_loadtopic`                | トピックを読み直します。過去メッセージを編集/削除した場合に使用します。|
| `/ac_summary`                  | 現在のトピックを要約し、要約前の会話内容は忘れます。                   |

## 環境変数の設定（AIチャット用）

チャット機能を使用するには、認証情報（JSONファイル）のアップロードが必要です。  
1. `/ac_template` で認証情報設定用テンプレートをダウンロードします。
2. 利用するAIチャット毎にリネームして、必要な情報を記入してください：

   ### 🔹 OpenAI API Key の取得手順
   1. [OpenAI Platform](https://platform.openai.com/account/api-keys) にログイン
   2. 「+ Create new secret key」でAPIキーを生成
   3. 表示された `sk-xxxxx...` 形式のキーをコピー
   4. /ac_template コマンドでダウンロードした JSONファイル の "api_key": に貼り付け
   🔒 注意：このAPIキーは絶対に外部に公開しないでください。
   5. 必要に応じて利用するチャットモデルをJSONファイル の "model": に貼り付け
   6. 必要に応じて以下のリンクよりログインしてBillingより支払方法や使用制限を設定
      https://platform.openai.com/account/billing

3. 利用するAIチャットのファイルを `/ac_auth` コマンドでアップロードします。  
   AIチャットを切り替える場合は、別のファイルをアップロードします。


## 招待リンクの設定

AIChatBotの招待リンクの作成方法は以下の通りです。
   1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
   2. My Applicationsで AIChatBot を選択
   3. 左メニュー「OAuth2」→「OAuth2 URL Generator」を表示
   4. 「scopes」で以下のパーミッションをチェック  
     - bot  
     - applications.commands  
   5. 「Bot Permissions」で以下のパーミッションをチェック  
     - View Channels  
     - Send Messages  
     - Create Public Threads  
     - Create Private Threads  
     - Send Messages in threads  
     - Manage Threads  
     - Read Message History
     - Use Slash Commands  
   6. 「Generated URL」でコピーしてブラウザで開き、サーバーを選択して招待

AIChatBot
https://discord.com/oauth2/authorize?client_id=1392390825148944406&permissions=397284543488&integration_type=0&scope=bot+applications.commands

AIChatBot Dev
https://discord.com/oauth2/authorize?client_id=1395576546747744357&permissions=397284543488&integration_type=0&scope=bot+applications.commands
