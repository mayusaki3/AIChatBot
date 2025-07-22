import discord
from discord import app_commands, Interaction
from common.session.user_session_manager import user_session_manager

HELP_TEXT = {
    "usage": "/ac_removeauth",
    "description": "登録したAIチャットの認証情報を削除します。"
}

@app_commands.command(name="ac_removeauth", description=HELP_TEXT["description"])
async def ac_removeauth_command(interaction: Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)

    auth_data = user_session_manager.get_session(interaction.user.id)
    if not auth_data:
        await interaction.followup.send("❌ 認証情報は登録されていません。", ephemeral=True)
        return

    user_session_manager.clear_session(interaction.user.id)
    await interaction.followup.send("✅ 認証情報を削除しました", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_removeauth_command, guild=guild)
    else:
        tree.add_command(ac_removeauth_command)
