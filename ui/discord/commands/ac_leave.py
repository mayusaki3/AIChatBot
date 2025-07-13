from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_leave",
    "description": "Botを現在のスレッドから退出させます。",
    "usage": "/ac_leave"
}

@app_commands.command(name="ac_leave", description=HELP_TEXT["description"])
async def ac_leave(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_leave` コマンドが実行されました。")
