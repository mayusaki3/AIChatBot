import json
import discord
from discord import app_commands, Interaction
from common.session.user_session_manager import user_session_manager
from common.session.server_session_manager import server_session_manager
from common.utils.image_model_manager import is_image_model_supported

HELP_TEXT = {
    "usage": "/ac_authsharing",
    "description": "認証情報が未登録の人に現在の認証情報をサーバー単位で共有します。"
}

@app_commands.command(name="ac_authsharing", description=HELP_TEXT["description"])
async def ac_authsharing_command(interaction: Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)

    user_id = interaction.user.id
    guild_id = interaction.guild_id
    guild = interaction.guild
    auth_data = server_session_manager.get_session(guild_id)
    msg = ""
    if auth_data:
        member = guild.get_member(user_id)
        user_name = f"id: {user_id}"
        if member:
            user_name = member.display_name
        msg += f"⚠️ {user_name} さんの認証情報が共有されていました。\n"
    
    auth_data = user_session_manager.get_session(interaction.user.id)
    if not auth_data:
        await interaction.followup.send("❌ 共有する認証情報が登録されていません。/ac_auth で登録してください。", ephemeral=True)
        return

    server_session_manager.set_session(guild_id, auth_data)
    auth_provider = auth_data["provider"]
    auth_model = auth_data["model"]
    if is_image_model_supported(auth_data):
        auth_model += " 🖼️"
    await interaction.followup.send(f"{msg}✅ 現在の認証情報［ {auth_provider} / {auth_model} ］を共有しました", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_authsharing_command, guild=guild)
    else:
        tree.add_command(ac_authsharing_command)
