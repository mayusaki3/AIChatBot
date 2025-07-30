import discord
from discord import app_commands, Interaction, Thread
from discord_handler import service_name
from common.session.user_session_manager import user_session_manager
from common.session.server_session_manager import server_session_manager
from common.utils.thread_utils import is_thread_managed
from ui.discord.discord_thread_context import context_manager

HELP_TEXT = {
    "usage": "/ac_status",
    "description": "使用中のAIチャットの状態を表示します。"
}

@app_commands.command(name="ac_status", description=HELP_TEXT["description"])
async def ac_status_command(interaction: Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    thread = interaction.channel
    msg = ""
    managed = False
    if isinstance(thread, Thread):
        # スレッドIDでスレッド情報取得（存在しない場合は None）
        if not is_thread_managed(service_name, interaction.guild_id, thread.id):
            msg = "ℹ️ このスレッドでAIチャットを利用するには /ac_invite でAIChatBotを招待してください。"
        else:
            managed = True
    else:
        msg = "ℹ️ AIチャットはスレッド内でのみ利用できます。"

    # ユーザー認証情報の状態
    user_id = interaction.user.id
    guild_id = interaction.guild.id
    guild = interaction.guild
    server_auth = server_session_manager.get_session(guild_id)
    if server_auth:
        sharing_user_id = server_auth.get("user_id")
        member = guild.get_member(sharing_user_id)
        if not member:
            member = await guild.fetch_member(sharing_user_id)
        if member:
            user_name = member.display_name
        else:
            user_name = f"id: {sharing_user_id}"
        auth = f"🗨️{server_auth['chat']['provider']}/{server_auth['chat']['model']}, "
        auth += f"👀{server_auth['vision']['provider']}/{server_auth['vision']['model']}, "
        auth += f"🖼️{server_auth['imagegen']['provider']}/{server_auth['imagegen']['model']}"
        msg += f"\nℹ️ {user_name} さんの認証情報［ {auth} ］が共有されています。"

    user_auth = user_session_manager.get_session(user_id)
    if user_auth:
        auth = f"🗨️{user_auth['chat']['provider']}/{user_auth['chat']['model']}, "
        auth += f"👀{user_auth['vision']['provider']}/{user_auth['vision']['model']}, "
        auth += f"🖼️{user_auth['imagegen']['provider']}/{user_auth['imagegen']['model']}"
        msg += f"\n🧑‍💻 現在の認証情報［ {auth} ］"
    else:
        if not server_auth:
            msg += "\n⚠️ AIと会話するには /ac_auth で認証情報を登録してください。"

    # AIチャットスレッドのコンテキスト状態
    if managed:
        if not context_manager.is_initialized(thread.id):
            # print(f"[INIT ] {thread.name}")  
            await context_manager.ensure_initialized(thread)
        # else:
            # print(f"[READY] {thread.name}")
        context = context_manager.get_context(thread.id)
        if context:
            msg += f"\n📜 スレッドのコンテキスト履歴は {len(context)} 件あります。"
            # print(f"[START] {thread.name}")
            # for mm in context:
            #     print(f"🟡{mm}")
            # print(f"[END  ] {thread.name}\n")
        else:
            msg += "\n📜 スレッドのコンテキスト履歴はありません。"

    await interaction.followup.send(msg, ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_status_command, guild=guild)
    else:
        tree.add_command(ac_status_command)
