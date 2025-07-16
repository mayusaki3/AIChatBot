import os
import sys
import json
import discord
from discord import app_commands, Interaction
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common.session.user_session_manager import session_manager
from ai.openai.validator import is_valid_openai_key, is_chat_model_available

HELP_TEXT = {
    "usage": "/ac_auth <file>",
    "description": "使用するAIチャットの認証情報を登録します。"
}

@app_commands.command(name="ac_auth", description=HELP_TEXT["description"])
async def ac_auth_command(interaction: Interaction, file: discord.Attachment):
    await interaction.response.defer(thinking=True, ephemeral=True)
    try:
        # ファイル形式チェック（念のため）
        if not file.filename.endswith(".json"):
            await interaction.followup.send("❌ .json ファイルを添付してください", ephemeral=True)
            return

        content = await file.read()
        auth_json = json.loads(content)

        # 検証
        for field in ["provider", "api_key", "model"]:
            if field not in auth_json:
                await interaction.followup.send(f"❌ `{field}` が含まれていません", ephemeral=True)
                return

        if auth_json["provider"] == "openai":
            api_key = auth_json["api_key"].strip()
            model_name = auth_json["model"].strip()
            result = is_valid_openai_key(api_key)
            if result is not True:
                await interaction.response.send_message(result, ephemeral=True)
                return                
            if not is_chat_model_available(api_key, model_name):
                await interaction.followup.send(f"❌ モデル `{model_name}` は利用できません", ephemeral=True)
                return
        else:
            await interaction.followup.send("❌ 現在は provider='openai' のみ対応しています", ephemeral=True)
            return

        # 保存（ユーザーごとのセッション管理）
        session_manager.set_session(interaction.user.id, auth_json)

        await interaction.followup.send("✅ 認証情報を登録しました", ephemeral=True)

    except json.JSONDecodeError:
        await interaction.followup.send("❌ JSONの読み込みに失敗しました。ファイルを確認してください", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ エラーが発生しました: {e}", ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_auth_command, guild=guild)
    else:
        tree.add_command(ac_auth_command)
