import json
import os
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from common.session.user_session_manager import UserSessionManager
from dotenv import load_dotenv

load_dotenv()

# .envから DISCORD_GUILD_ID を読み取り
raw_gid = os.getenv("DISCORD_GUILD_ID", "").strip()
USE_GUILD = bool(raw_gid and not raw_gid.startswith("#"))
GUILD_OBJ = discord.Object(id=int(raw_gid)) if USE_GUILD else None

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
session_manager = UserSessionManager()

# Discordメッセージ送信イベント
@client.event
async def on_message(message):
    # メッセージがボットからのものであれば無視
    if message.author.bot:
        return
        
    # スレッド内でのみ処理を行う
    if not isinstance(message.channel, discord.Thread):
        return

    user_id = message.author.id

    # 認証ファイルアップロード処理
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(".json"):
                content = await attachment.read()
                try:
                    auth_json = json.loads(content)
                    session_manager.set_session(user_id, auth_json)
                    await message.channel.send("✅ 認証情報を登録しました。")
                except Exception as e:
                    await message.channel.send(f"❌ 認証情報の登録に失敗: {e}")
                return

    # 認証情報チェック
    if not session_manager.has_session(user_id):
        await message.channel.send("⚠️ 先に認証ファイル（JSON）をアップロードしてください。")
        return

    # メッセージをAIに送信
    auth = session_manager.get_session(user_id)
    if auth["provider"] == "openai":
        reply = await call_chatgpt(message.content, auth["api_key"], auth["model"])
    else:
        reply = f"❌ 未対応のプロバイダ: {auth['provider']}"

    await message.channel.send(reply)

# 認証テンプレートダウンロードコマンド
@tree.command(name="ac_template", description="認証テンプレート（JSON）をダウンロード", guild=GUILD_OBJ)
async def ac_template_command(interaction: discord.Interaction):
    try:
        file_path = Path(__file__).resolve().parent.parent.parent / "common/template/auth_template.json"
        if not file_path.exists():
            await interaction.response.send_message("テンプレートファイルが見つかりません。", ephemeral=True)
            return

        await interaction.response.send_message(
            content="以下が認証用テンプレートです。\nJSONをダウンロードして記入後、/ac_auth でアップロードしてください。",
            file=discord.File(fp=file_path, filename="auth_template.json"),
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"エラーが発生しました: {e}", ephemeral=True)

# ヘルプコマンド
@tree.command(name="ac_help", description="コマンド一覧を表示します", guild=GUILD_OBJ)
async def ac_help_command(interaction: discord.Interaction):
    help_text = """📘 **AIChatBot コマンド一覧**

/ac_help     - このヘルプを表示します
/ac_template - 認証テンプレート（JSON）をダウンロード
/ac_newchat [トピック名] - 新しいAIチャットスレッドを開始します

📌 スレッド内でのみAIとのチャットが可能です。
🔐 認証には JSON ファイルをアップロードしてください。
"""
    await interaction.response.send_message(help_text, ephemeral=True)

# Bot起動イベント
@client.event
async def on_ready():
    print(f"✅ {client.user} としてログインしました。")

    try:
        if USE_GUILD:
            await tree.sync(guild=GUILD_OBJ)
            print(f"🧪 開発モード（サーバーID={raw_gid}）でコマンドを同期しました")
        else:
            await tree.sync()
            print("🚀 本番モード（グローバル）でコマンドを同期しました")

    except Exception as e:
        print(f"❌ コマンド同期に失敗しました: {e}")
        import sys
        sys.exit(1)  # プロセスを停止

# Bot起動
def start_discord_bot():
    client.run(os.environ["DISCORD_BOT_TOKEN"])
