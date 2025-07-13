from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_template",
    "description": "AIとの新しいスレッドを作成します。",
    "usage": "/ac_template"
}

@app_commands.command(name="ac_template", description=HELP_TEXT["description"])
async def ac_newchat(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_template` コマンドが実行されました。")
