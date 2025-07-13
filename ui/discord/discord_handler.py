import json
import os
import sys
import datetime
import shutil
import discord
from discord import app_commands
from discord import Interaction, Thread, ChannelType
from discord import Interaction
from discord.ext import commands
from common.session.user_session_manager import UserSessionManager
from dotenv import load_dotenv
from typing import Optional
from common.utils import thread_utils
from ui.discord.commands.load_commands import load_commands

load_dotenv()

# .envから DISCORD_GUILD_ID を読み取り
raw_gid = os.getenv("DISCORD_GUILD_ID", "").strip()
USE_GUILD = bool(raw_gid and not raw_gid.startswith("#"))
GUILD_OBJ = discord.Object(id=int(raw_gid)) if USE_GUILD else None

service_name = "discord"
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
session_manager = UserSessionManager()


import importlib
import pkgutil
from pathlib import Path

# Discordメッセージ送信イベント
@client.event
async def on_message(message):
    # メッセージがボットからのものであれば無視
    if message.author.bot:
        return
        
    # AIChatスレッド内でのみ処理を行う
    if not isinstance(message.channel, discord.Thread):
        return
    if "AIChat - " not in discord.Thread.name:
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

# # AIチャット用スレッドを作成
# @tree.command(
#     name="ac_newchat",
#     description="🛑スレッド内では使用できません：AIチャット用スレッドを作成します",
#     guild=GUILD_OBJ  # または None = 全体公開
# )
# @app_commands.describe(title="（任意）スレッドのタイトルを指定できます")
# async def ac_newchat_command(interaction: Interaction, title: Optional[str] = None):
#     # 🔒 スレッド内では使用不可
#     if isinstance(interaction.channel, Thread):
#         await interaction.response.send_message(
#             "❌ このコマンドは **スレッド内では使用できません**。\n"
#             "通常のテキストチャンネルで実行してください。",
#             ephemeral=True
#         )
#         return

#     try:
#         now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#         user_name = interaction.user.display_name

#         if title:
#             thread_name = f"AIChat - {title}"
#         else:
#             thread_name = f"AIChat - {user_name} - {now_str}"

#         thread = await interaction.channel.create_thread(
#             name=thread_name,
#             type=ChannelType.public_thread,
#             auto_archive_duration=1440,
#             invitable=False
#         )

#         await thread.send(
#             f"💬 このスレッドは {interaction.user.mention} によって作成された **AIChatBot 用スレッド** です。\n"
#             f"・このスレッド内での発言は、発言者が登録した認証情報に基づいて AI に送信・応答されます。\n"
#             f"・現時点、文脈情報は利用できません。"
#         )

#         await interaction.response.send_message(
#             f"✅ スレッド [`{thread_name}`] を作成しました。",
#             ephemeral=True
#         )

#     except Exception as e:
#         await interaction.response.send_message(
#             f"❌ スレッド作成に失敗しました：{str(e)}",
#             ephemeral=True
#         )



# /ac_auth [ファイル] - 認証情報をアップロードして登録します

# チャンネル専用コマンド
# /ac_newchat [トピック名] - 新しいAIチャットスレッドを開始します

# スレッド内専用コマンド


# 📌 AIChatスレッド内でのみAIとのチャットが可能です。
# 🔐 認証には JSON ファイルをアップロードしてください。
# """
#     await interaction.response.send_message(help_text, ephemeral=True)

# Bot起動イベント
@client.event
async def on_ready():
    print(f"✅ {client.user} としてログインしました。(Ctrl-Cで終了します)")

    try:
        load_commands(tree, client, GUILD_OBJ)
        for cmd in tree.get_commands():
            print(f"🔍 コマンド登録: /{cmd.name}")
        if USE_GUILD:
            await tree.sync(guild=GUILD_OBJ)
            print(f"🧪 開発モード（サーバーID={raw_gid}）でコマンドを同期しました")
        else:
            await tree.sync()
            print("🚀 本番モード（グローバル）でコマンドを同期しました")
	
        # すべてのサーバー（Guild）に対して処理
        for guild in client.guilds:
            server_id = str(guild.id)

            thread_ids = []
            for channel in guild.text_channels:
                for thread in channel.threads:
                    thread_ids.append(str(thread.id))

            # スレッド削除検出（ファイル上の管理情報と実際のスレッドを突き合わせ）
            thread_utils.clean_deleted_threads("discord", server_id, thread_ids)

        # 削除済みサーバーの検出とクリーニング
        known_server_ids = set(str(guild.id) for guild in client.guilds)
        thread_utils.clean_deleted_servers("discord", known_server_ids)

        print("✅ 存在しないサーバー/スレッドのチェックおよびクリーンアップを完了しました")

    except Exception as e:
        print(f"❌ コマンド同期に失敗しました: {e}")
        import sys
        sys.exit(1)

# Bot起動
def start_discord_bot():
    client.run(os.environ["DISCORD_BOT_TOKEN"])
