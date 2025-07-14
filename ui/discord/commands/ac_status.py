import discord
from discord import app_commands, Interaction

HELP_TEXT = {
    "usage": "/ac_status",
    "description": "使用中のAIチャットの状態を表示します。"
}

@app_commands.command(name="ac_status", description=HELP_TEXT["description"])
async def ac_status_command(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_status` コマンドが実行されました。")

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_status_command, guild=guild)
    else:
        tree.add_command(ac_status_command)
