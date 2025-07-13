from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_status",
    "description": "このスレッドがBot対象かを確認し、設定済みAIの情報を表示します。",
    "usage": "/ac_status"
}

@app_commands.command(name="ac_status", description=HELP_TEXT["description"], guild=GUILD_OBJ)
async def ac_status(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_status` コマンドが実行されました。")
