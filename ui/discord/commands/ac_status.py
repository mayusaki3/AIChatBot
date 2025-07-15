import os
import sys
import discord
from discord import app_commands, Interaction, Thread
from common.utils.thread_utils import is_thread_managed
from common.session.user_session_manager import UserSessionManager
from discord_handler import service_name
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common.session.user_session_manager import session_manager

HELP_TEXT = {
    "usage": "/ac_status",
    "description": "使用中のAIチャットの状態を表示します。"
}

@app_commands.command(name="ac_status", description=HELP_TEXT["description"])
async def ac_status_command(interaction: Interaction):
    thread = interaction.channel
    msg = ""
    if isinstance(thread, Thread):
        # スレッドIDでスレッド情報取得（存在しない場合は None）
        if not is_thread_managed(service_name, interaction.guild_id, thread.id):
            msg = "ℹ️ このスレッドでAIチャットを利用するには /ac_invite でAIChatBotを招待してください。\n"
    else:
        msg = "ℹ️ AIチャットはスレッド内でのみ利用できます。\n"

    # ユーザー認証情報の状態
    user_id = interaction.user.id
    user_auth = session_manager.get_session(user_id)
    if user_auth:
        auth_provider = user_auth.get("provider", "未登録")
        auth_model = user_auth.get("model", "未登録")
        msg += f"🧑‍💻 現在の認証情報［ {auth_provider} / {auth_model} ］"
    else:
        msg += "⚠️ AIと会話するには /ac_auth で認証情報を登録してください。"

    await interaction.response.send_message(msg, ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_status_command, guild=guild)
    else:
        tree.add_command(ac_status_command)
