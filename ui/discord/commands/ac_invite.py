import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import discord
from discord import app_commands, Interaction
from common.utils.thread_utils import add_thread_to_server
from discord_handler import service_name

HELP_TEXT = {
    "usage": "/ac_invite",
    "description": "🧵スレッド内のみ: AIチャットを現在のスレッドに招待します。"
}

@app_commands.command(name="ac_invite", description=HELP_TEXT["description"])
async def ac_invite_command(interaction: Interaction):
    thread = interaction.channel
    if thread is None or not hasattr(thread, "add_user"):
        await interaction.response.send_message("❌ このチャンネルでは実行できません。", ephemeral=True)
        return

    try:
        await thread.add_user(interaction.client.user)
        add_thread_to_server(service_name, interaction.guild_id, thread.id)
        await interaction.response.send_message("✅ Botをこのスレッドに招待しました。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ 招待に失敗しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_invite_command, guild=guild)
    else:
        tree.add_command(ac_invite_command)
