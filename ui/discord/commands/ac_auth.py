from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_auth",
    "description": "AIとの新しいスレッドを作成します。",
    "usage": "/ac_auth"
}

@app_commands.command(name="ac_auth", description=HELP_TEXT["description"])
async def ac_newchat(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_auth` コマンドが実行されました。")
