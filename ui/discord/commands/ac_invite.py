import os
import sys
import discord
from discord import app_commands, Interaction
from discord_handler import service_name
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common.utils.thread_utils import add_thread_to_server, is_thread_managed

HELP_TEXT = {
    "usage": "/ac_invite",
    "description": "🧵スレッド内のみ: AIChatBotを現在のスレッドに招待します。"
}

@app_commands.command(name="ac_invite", description=HELP_TEXT["description"])
async def ac_invite_command(interaction: Interaction):
    thread = interaction.channel
    if thread is None or not hasattr(thread, "add_user"):
        await interaction.response.send_message("❌ スレッド外では実行できません。", ephemeral=True)
        return

    if is_thread_managed(service_name, interaction.guild_id, thread.id):
        await interaction.response.send_message("⚠️ AIChatBotは既にこのスレッドに参加しています。", ephemeral=True)
        return

    try:
        if thread.owner_id != interaction.client.user.id:
            # Botがスレッド作成者でない場合
            if thread.is_private() and interaction.user.id != thread.owner_id:
                await interaction.response.send_message("⚠️ プライベートスレッドでAIChatBotを招待するには、スレッド作成者である必要があります。", ephemeral=True)
                return

            # Botが招待できるか試行
            try:
                await thread.add_user(interaction.client.user)
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ AIChatBotを招待する権限がありません。\n@AIChatBot に memtion してから再実行してください。", ephemeral=True)
                return

        add_thread_to_server(service_name, interaction.guild_id, thread.id)
        await interaction.response.send_message("✅ AIChatBotをこのスレッドに招待しました。", ephemeral=True)
        await thread.send(
            f"💬 AIChatBotが参加しました。\n"
            f"・このスレッド内での発言は、発言者が登録した認証情報に基づいて AI に送信・応答されます。"
        )

    except Exception as e:
        await interaction.response.send_message(f"❌ AIChatBotの招待に失敗しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_invite_command, guild=guild)
    else:
        tree.add_command(ac_invite_command)
