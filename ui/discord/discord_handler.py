import os
import sys
import discord
from discord import app_commands, Interaction, Thread, ChannelType
from discord.ext import commands
from dotenv import load_dotenv
from common.session.user_session_manager import session_manager
from common.utils import thread_utils
from common.utils.thread_utils import remove_thread_from_server, is_thread_managed
from common.utils.image_model_manager import is_image_model_supported
from ui.discord.commands.load_commands import load_commands
from ui.discord.discord_thread_context import context_manager
from ai.openai.openai_api import call_chatgpt

load_dotenv()

# .envから DISCORD_GUILD_ID を読み取り
raw_gid = os.getenv("DISCORD_GUILD_ID", "").strip()
USE_GUILD = bool(raw_gid and not raw_gid.startswith("#"))
GUILD_OBJ = discord.Object(id=int(raw_gid)) if USE_GUILD else None

service_name = "discord"
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

# Discordメッセージ送信イベント
@client.event
async def on_message(message):
    # メッセージがボットからのものであれば無視
    if message.author.bot:
        return

    # AIチャットスレッド以外は無視
    thread = message.channel
    if isinstance(thread, Thread):
        guild_id = str(message.guild.id)
        if not thread_utils.is_thread_managed(service_name, guild_id, thread.id):
            return
    else:
        return

    # 認証情報チェック
    user_id = message.author.id
    if not session_manager.has_session(user_id):
        await message.channel.send("⚠️ 認証情報を /ac_auth で登録してください。")
        return

    # メッセージをコンテキストに追加
    author_name = message.author.display_name
    if not context_manager.is_initialized(thread.id):
        await context_manager.ensure_initialized(thread)
    context_manager.append_context(thread.id, f"{author_name}: {message.content}")
    context_list = context_manager.get_context(thread.id)

    # メッセージをAIに送信
    user_auth = session_manager.get_session(user_id)
    imageuse =is_image_model_supported(user_auth)

    # OpenAIの場合
    if user_auth["provider"] == "openai":
        async with message.channel.typing():
            reply = await call_chatgpt(context_list, user_auth["api_key"], user_auth["model"])
            # レスポンスをコンテキストに追加
            await message.channel.send(reply)
            context_manager.append_context(thread.id, f"AIChatBot: {reply}")

    return

# スレッド削除イベント
@client.event
async def on_thread_delete(thread: discord.Thread):
    thread_id = str(thread.id)
    guild_id = str(thread.guild.id)

    if is_thread_managed(service_name, guild_id, thread.id):
        try:
            remove_thread_from_server(service_name, guild_id, thread.id)
            print(f"✅ AIチャット対象からスレッド {thread_id} を削除しました。")
        except Exception as e:
            print(f"❌ AIチャット対象からスレッド {thread_id} が削除できませんでした: {e}")

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
