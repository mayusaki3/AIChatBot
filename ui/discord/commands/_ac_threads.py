from discord import app_commands
from discord import Interaction

HELP_TEXT = {
    "name": "ac_threads",
    "description": "このサーバーでBotが管理しているAIスレッド一覧を表示します。",
    "usage": "/ac_threads"
}

@app_commands.command(name="ac_threads", description=HELP_TEXT["description"])
async def ac_threads(interaction: Interaction):
    await interaction.response.send_message("✅ `ac_threads` コマンドが実行されました。")
