from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_newchat",
    "description": "AIとの新しいスレッドを作成します。",
    "usage": "/ac_newchat"
}

@app_commands.command(name="ac_newchat", description=HELP_TEXT["description"])
async def ac_newchat(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_newchat` コマンドが実行されました。")
