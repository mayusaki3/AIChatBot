from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_invite",
    "description": "Botを現在のスレッドに招待します。",
    "usage": "/ac_invite"
}

@app_commands.command(name="ac_invite", description=HELP_TEXT["description"])
async def ac_invite(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_invite` コマンドが実行されました。")
