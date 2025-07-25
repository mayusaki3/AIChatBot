import discord
from discord import app_commands, Interaction
from common.session.user_session_manager import user_session_manager
from common.utils.image_model_manager import is_image_model_supported, remove_image_supported_model

HELP_TEXT = {
    "usage": "/ac_imagenonuse",
    "description": "認証情報のモデルを、画像非対応にマークします。"
}

@app_commands.command(name="ac_imagenonuse", description=HELP_TEXT["description"])
async def ac_imagenonuse_command(interaction: Interaction):
    user_id = interaction.user.id
    user_auth = user_session_manager.get_session(user_id)
    if not user_auth:
        await interaction.response.send_message("⚠️ 認証情報を /ac_auth で登録してください。", ephemeral=True)
        return

    model = user_auth["model"]
    if not is_image_model_supported(user_auth):
        await interaction.response.send_message(f"⚠️ モデル {model} は既に画像非対応にマークされています。", ephemeral=True)
        return

    try:
        remove_image_supported_model(user_auth)
        await interaction.response.send_message(f"✅ モデル {model} を画像非対応にマークしました。", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"❌ モデル {model} を画像非対応マークに失敗しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_imagenonuse_command, guild=guild)
    else:
        tree.add_command(ac_imagenonuse_command)
