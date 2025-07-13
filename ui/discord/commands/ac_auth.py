import discord
from discord import app_commands, Interaction

HELP_TEXT = {
    "usage": "/ac_auth",
    "description": "AIとの新しいスレッドを作成します。"
}

@app_commands.command(name="ac_auth", description=HELP_TEXT["description"])
async def ac_auth_command(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_auth` コマンドが実行されました。")

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_auth_command, guild=guild)
    else:
        tree.add_command(ac_auth_command)
