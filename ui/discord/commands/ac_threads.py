import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import discord
from discord import app_commands, Interaction
from common.utils.thread_utils import load_server_threads
from discord_handler import service_name

HELP_TEXT = {
    "usage": "/ac_threads",
    "description": "AIチャットと会話中のスレッド一覧を表示します。"
}

@app_commands.command(name="ac_threads", description=HELP_TEXT["description"])
async def ac_threads_command(interaction: Interaction):
    thread_ids = load_server_threads(service_name, interaction.guild_id)
    if not thread_ids:
        await interaction.response.send_message("📭 会話中のスレッドはありません。", ephemeral=True)
        return

    lines = ["🧵 会話中のスレッド一覧:"]
    for thread_id in thread_ids:
        try:
            thread = await interaction.guild.fetch_channel(thread_id)
            lines.append(f"- {thread.name}（ID: `{thread.id}`）")
        except Exception as e:
            lines.append(f"- ID: `{thread_id}`（取得失敗: {e}）")

    await interaction.response.send_message("\n".join(lines), ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_threads_command, guild=guild)
    else:
        tree.add_command(ac_threads_command)
