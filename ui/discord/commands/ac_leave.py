import os
import sys
import discord
from discord import app_commands, Interaction
from discord_handler import service_name
from common.utils.thread_utils import remove_thread_from_server, is_thread_managed

HELP_TEXT = {
    "usage": "/ac_leave",
    "description": "🧵スレッド内のみ: AIChatBotを現在のスレッドから退出させます。"
}

@app_commands.command(name="ac_leave", description=HELP_TEXT["description"])
async def ac_leave_command(interaction: Interaction):
    thread = interaction.channel
    if thread is None or not hasattr(thread, "remove_user"):
        await interaction.response.send_message("❌ スレッド外では実行できません。", ephemeral=True)
        return

    if not is_thread_managed(service_name, interaction.guild_id, thread.id):
        await interaction.response.send_message("⚠️ AIChatBotはこのスレッドに参加していません。", ephemeral=True)
        return

    try:
        if thread.owner_id != interaction.client.user.id:
            try:
                await thread.remove_user(interaction.client.user)
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ AIChatBotを退出させる権限がありません。", ephemeral=True)
                return
        remove_thread_from_server(service_name, interaction.guild_id, thread.id)
        await interaction.response.send_message("👋 AIChatBotはスレッドから退出しました。", ephemeral=True)
        await thread.send(
            f"💬 AIChatBotが退出しました。\n"
            f"・以後のスレッド内での発言は、AI に送信されることはありません。"
        )

    except Exception as e:
        await interaction.response.send_message(f"❌ AIChatBotの退出に失敗しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_leave_command, guild=guild)
    else:
        tree.add_command(ac_leave_command)
