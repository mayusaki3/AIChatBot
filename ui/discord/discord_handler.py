import os
import discord
from discord import app_commands, Interaction, Thread, ChannelType
from discord.ext import commands
from common.session.user_session_manager import UserSessionManager
from dotenv import load_dotenv
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

# Discordメッセージ送信イベント
@client.event
async def on_message(message):
    # メッセージがボットからのものであれば無視
    if message.author.bot:
        return
        
    # AIChatスレッド内でのみ処理を行う
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

        # 参加していないサーバーの検出とクリーニング（サーバーID単位）
        existing_server_ids = {str(guild.id) for guild in client.guilds}
        thread_utils.clean_deleted_servers(service_name, existing_server_ids)

        # すべてのサーバー（Guild）に対して処理
        for guild in client.guilds:
            server_id = str(guild.id)
            thread_ids = set()

            # チャンネルごとのアーカイブ済みスレッド
            for channel in guild.text_channels:
                    for thread in channel.threads:
                        thread_ids.add(str(thread.id))

            # スレッド存在チェック用に記憶されたスレッド一覧をクリーンアップ
            thread_utils.clean_deleted_threads(service_name, server_id, thread_ids)

        print("✅ 存在しないサーバー/スレッドのチェックおよびクリーンアップを完了しました")

    except Exception as e:
        print(f"❌ コマンド同期に失敗しました: {e}")
        import sys
        sys.exit(1)

# Bot起動
def start_discord_bot():
    client.run(os.environ["DISCORD_BOT_TOKEN"])
