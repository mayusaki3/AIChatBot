import json
import os
import discord
from discord import app_commands
from discord.ext import commands
from common.session.user_session_manager import UserSessionManager

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
session_manager = UserSessionManager()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id

    # JSONファイルがアップロードされた場合 → 認証情報登録
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

    # 認証情報がなければ警告
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
@tree.command(name="help", description="コマンド一覧を表示します")
async def help_command(interaction: discord.Interaction):
    help_text = """📘 **AIChatBot コマンド一覧**

/help - このヘルプを表示します  
/template - 認証テンプレート（JSON）をダウンロード  
/newchat [トピック名] - 新しいAIチャットスレッドを開始します  

📌 スレッド内でのみAIとのチャットが可能です。  
🔐 認証には JSON ファイルをアップロードしてください。
"""
    await interaction.response.send_message(help_text, ephemeral=True)
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")

def start_discord_bot():
    client.run(os.environ["DISCORD_BOT_TOKEN"])
