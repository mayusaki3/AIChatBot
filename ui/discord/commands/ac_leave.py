import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import discord
from discord import app_commands, Interaction
from common.utils.thread_utils import remove_thread_from_server
from discord_handler import service_name

HELP_TEXT = {
    "usage": "/ac_invite",
    "description": "🧵スレッド内のみ: AIチャットを現在のスレッドから退出させます。"
}

@app_commands.command(name="ac_leave", description=HELP_TEXT["description"])
async def ac_leave_command(interaction: Interaction):
    thread = interaction.channel
    if thread is None or not hasattr(thread, "remove_user"):
        await interaction.response.send_message("❌ このチャンネルでは実行できません。", ephemeral=True)
        return

    try:
        await thread.remove_user(interaction.client.user)
        remove_thread_from_server(service_name, interaction.guild_id, thread.id)
        await interaction.response.send_message("👋 スレッドから退出しました。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ 退出に失敗しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_leave_command, guild=guild)
    else:
        tree.add_command(ac_leave_command)
