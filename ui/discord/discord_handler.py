import os
import sys
import discord
import io
from discord import app_commands, Interaction, Thread
from discord.ext import commands
from dotenv import load_dotenv
from common.session.user_session_manager import user_session_manager
from common.session.server_session_manager import server_session_manager
from common.utils import thread_utils
from common.utils.thread_utils import remove_thread_from_server, is_thread_managed
from ui.discord.commands.load_commands import load_commands
from ui.discord.discord_thread_context import context_manager
from ai.openai.openai_api import call_chatgpt, generate_image_from_prompt
import aiohttp
import base64

load_dotenv()

# .envから DISCORD_GUILD_ID を読み取り
raw_gid = os.getenv("DISCORD_GUILD_ID", "").strip()
USE_GUILD = bool(raw_gid and not raw_gid.startswith("#"))
GUILD_OBJ = discord.Object(id=int(raw_gid)) if USE_GUILD else None

service_name = "discord"
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 添付画像をbase64で取得
async def fetch_image_as_base64(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_bytes = await resp.read()
                return base64.b64encode(image_bytes).decode('utf-8')

# Discordメッセージ送信イベント
@client.event
async def on_message(message):
    # AIチャットスレッド以外は無視
    thread = message.channel
    if isinstance(thread, Thread):
        guild_id = str(message.guild.id)
        if not thread_utils.is_thread_managed(service_name, guild_id, thread.id):
            return
    else:
        return

    # メッセージをコンテキストに追加
    author_name = message.author.display_name
    refid = ""
    if not context_manager.is_initialized(thread.id):
        await context_manager.ensure_initialized(thread)
    else:
        if message.reference and message.reference.message_id:
            refid = str(message.reference.message_id)
            try:
                # 人間が返信した場合のみ返信元を辿り補完する
                if not message.author.bot:
                    await context_manager.backfill_reply_chain(thread, message, max_hops=10)
            except Exception as e:
                print(f"[reply-chain] backfill failed: {e}")
        context_manager.append_context(thread.id, f"{author_name}: {message.content}", str(message.id), refid, message.attachments)

    # メッセージがボットからのものであれば終了
    if message.author.bot:
        return

    context_list = []
    for context in context_manager.get_context(thread.id):
        context_list.append(context["message"])
    
    # 認証情報チェック
    user_id = message.author.id
    guild_id = message.guild.id
    if not user_session_manager.has_session(user_id):
        if not server_session_manager.has_session(guild_id):
            await message.reply("⚠️ あいちゃぼと会話するには、認証情報を /ac_auth で登録してください。")
            return

    # 認証情報を取得
    if server_session_manager.has_session(guild_id):
        auth_data = server_session_manager.get_session(guild_id)
    else:
        auth_data = user_session_manager.get_session(user_id)

    # 返信元の情報を注入
    if refid:
        try:
            parent_chain = await context_manager.fetch_parent_chain(thread, message, 1)
            print(f"parent_chain={parent_chain}")
            if parent_chain:
                parent_text = parent_chain[-1].content or "(テキストなし)"
                reply_hint = auth_data["chat"]["reply_prompt"].format(parent_message=parent_text)
                context_list.append(reply_hint)
        except Exception as e:
            print(f"[reply-chain] backfill failed: {e}")

    # 追加情報を注入
    context_list.append(context_manager.get_injection_message(auth_data))

    # 添付画像がある場合はコンテキストに追加
    # imageuse = is_image_model_supported(auth_data)
    # if message.attachments and imageuse:
    #     msg = "["
    #     count = 0
    #     for attachment in message.attachments:
    #         if attachment.content_type and attachment.content_type.startswith("image/"):
    #             image_base64 = await fetch_image_as_base64(attachment.url)
    #             if image_base64:
    #                 if count > 0:
    #                     msg += ","
    #                 msg += '{"type": "image_url","image_url": {"url": '
    #                 msg += f"data:image/png;base64,{image_base64}"
    #                 msg += '}'
    #                 count += 1
    #     msg += "]"
    #     context_list.append(f"{msg}")

    # オプション -printmsg:on 処理
    if server_session_manager.get_option(guild_id, "printmsg", False):
        print("context_list =>")
        for msg in context_list:
            print(f"  {msg}")

    # 画像生成か判定
    keywords = set(auth_data["chat"].get("imagegen_keywords", []))
    if any(k in message.content for k in keywords):

        # 画像生成 ==========

        # OpenAIの場合
        if auth_data["imagegen"]["provider"] == "OpenAI":
            try:
                # 画像用プロンプトは chat.imagegen_prompt を使って文脈から生成
                image_prompt_seed = auth_data["chat"].get("imagegen_prompt", "")
                # 直近の文脈を少し短めに連結（必要に応じて調整）
                joined_context = "\n".join(context_list[-10:])
                image_prompt = f"{image_prompt_seed}\n\n{joined_context}".strip()

                async with message.channel.typing():
                    img_bytes = await generate_image_from_prompt(
                        prompt=image_prompt,
                        api_key=auth_data["imagegen"]["api_key"],
                        model=auth_data["imagegen"]["model"],
                        size=auth_data["imagegen"]["size"],
                        quality=auth_data["imagegen"]["quality"],
                        timeout_sec=90
                    )
                    # 添付送信
                    file = discord.File(fp=io.BytesIO(img_bytes), filename="aichabo_image.png")
                    await message.channel.send(
                        content="🖼️ 画像を生成しました。",
                        file=file
                    )
            except Exception as e:
                # 画像生成だけ失敗しても会話は続行できるよう、ここで握りつぶして通知のみ
                await message.channel.send(f"⚠️ 画像生成に失敗しました: {e}")

    else:
        # チャット ==========

        # OpenAIの場合
        if auth_data["chat"]["provider"] == "OpenAI":
            async with message.channel.typing():
                reply = await call_chatgpt(context_list, auth_data["chat"]["api_key"], auth_data["chat"]["model"], auth_data["chat"]["max_tokens"])
                # レスポンス
                await message.channel.send(reply)

    return

# スレッド削除イベント
@client.event
async def on_thread_delete(thread: discord.Thread):
    thread_id = str(thread.id)
    guild_id = str(thread.guild.id)

    if is_thread_managed(service_name, guild_id, thread_id):
        try:
            remove_thread_from_server(service_name, guild_id, thread_id)
            print(f"✅ あいちゃぼの会話対象からスレッド {thread_id} を削除しました。")
        except Exception as e:
            print(f"❌ あいちゃぼの会話対象からスレッド {thread_id} が削除できませんでした: {e}")

# メッセージ変更イベント
@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    print(f"🔄 メッセージが編集されました: {before.author.name} {before.content} ⇒ {after.author.name} {after.content}")
    context_manager.reset_context(before.channel.id)

# メッセージ削除イベント
@client.event
async def on_message_delete(message):
    print(f"❌ メッセージが削除されました: {message.content}")
    context_manager.reset_context(message.channel.id)

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
        await client.close()

# Bot起動
def start_discord_bot():
    client.run(os.environ["DISCORD_BOT_TOKEN"])
