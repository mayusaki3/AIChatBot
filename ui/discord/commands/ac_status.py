import discord
from discord import app_commands, Interaction, Thread
from discord_handler import service_name
from common.session.user_session_manager import session_manager
from common.utils.thread_utils import is_thread_managed
from common.utils.image_model_manager import is_image_model_supported
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
            msg = "ℹ️ このスレッドでAIチャットを利用するには /ac_invite でAIChatBotを招待してください。\n"
        else:
            managed = True
    else:
        msg = "ℹ️ AIチャットはスレッド内でのみ利用できます。\n"

    # ユーザー認証情報の状態
    user_id = interaction.user.id
    user_auth = session_manager.get_session(user_id)
    if user_auth:
        auth_provider = user_auth.get("provider", "未登録")
        auth_model = user_auth.get("model", "未登録")
        if is_image_model_supported(user_auth):
            auth_model += " 🖼️"
        msg += f"🧑‍💻 現在の認証情報［ {auth_provider} / {auth_model} ］"
    else:
        msg += "⚠️ AIと会話するには /ac_auth で認証情報を登録してください。"

    # AIチャットスレッドのコンテキスト状態
    if managed:
        if not context_manager.is_initialized(thread.id):
            print(f"[INIT ] {thread.name}")  
            await context_manager.ensure_initialized(thread)
        else:
            print(f"[READY] {thread.name}")
        context = context_manager.get_context(thread.id)
        if context:
            msg += f"\n📜 スレッドのコンテキスト履歴は {len(context)} 件あります。"
            print(f"\n[START] {thread.name}")
            for mm in context:
                print(f"🟡{mm}")
            print(f"[END  ] {thread.name}")
        else:
            msg += "\n📜 スレッドのコンテキスト履歴はありません。"

    await interaction.followup.send(msg, ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_status_command, guild=guild)
    else:
        tree.add_command(ac_status_command)
