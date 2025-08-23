import json
import discord
from discord import app_commands, Interaction
from common.session.user_session_manager import user_session_manager
from ai.openai.validator import is_valid_openai_key, is_openai_chat_model_available, is_openai_vision_model_available, is_openai_imagegen_model_available

HELP_TEXT = {
    "usage": "/ac_auth <file>",
    "description": "あいちゃぼが使用するAIチャットの認証情報を登録します。"
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
        try:
            for field in ["template_version"]:
                if field not in auth_json:
                    raise KeyError(field)
            if auth_json["template_version"] != "1.0":
                await interaction.followup.send("❌ 認証情報のテンプレートバージョンが不正です", ephemeral=True)
                return
            for key in ["chat", "vision", "imagegen"]:
                section = auth_json.get(key)
                if section:
                    for field in ["provider", "api_key", "model"]:
                        if field not in section:
                            raise KeyError(field)
                    if key == "chat":
                        for field in ["max_tokens", "tone_prompt", "reply_prompt", "summary_prompt", "injection_prompt", "imagegen_prompt", "imagegen_keywords"]:
                            if field not in section:
                                raise KeyError(f"chat.{field}")
                    if key == "vision":
                        for field in ["vision_prompt"]:
                            if field not in section:
                                raise KeyError(f"vision.{field}")
                    if key == "imagegen":
                        for field in ["size", "quality"]:
                            if field not in section:
                                raise KeyError(f"imagegen.{field}")
        except KeyError as e:
            await interaction.followup.send(f"❌ 認証情報に必要なフィールド `{e}` が含まれていません", ephemeral=True)
            return   

        try:
            if auth_json["chat"]["provider"] == "OpenAI":
                api_key = auth_json["chat"]["api_key"].strip()
                model_name = auth_json["chat"]["model"].strip()
                result = await is_valid_openai_key(api_key)
                if result is not True:
                    await interaction.response.send_message(result, ephemeral=True)
                    return                
                if not await is_openai_chat_model_available(api_key, model_name):
                    await interaction.followup.send(f"❌ Chatモデル `{model_name}` は利用できません", ephemeral=True)
                    return
            else:
                raise ValueError("Unsupported provider")

            if auth_json["vision"]["provider"] == "OpenAI":
                api_key = auth_json["vision"]["api_key"].strip()
                model_name = auth_json["vision"]["model"].strip()
                result = await is_valid_openai_key(api_key)
                if result is not True:
                    await interaction.response.send_message(result, ephemeral=True)
                    return                
                if not await is_openai_vision_model_available(api_key, model_name):
                    await interaction.followup.send(f"❌ Visionモデル `{model_name}` は利用できません", ephemeral=True)
                    return
            else:
                raise ValueError("Unsupported provider")

            if auth_json["imagegen"]["provider"] == "OpenAI":
                api_key = auth_json["imagegen"]["api_key"].strip()
                model_name = auth_json["imagegen"]["model"].strip()
                result = await is_valid_openai_key(api_key)
                if result is not True:
                    await interaction.response.send_message(result, ephemeral=True)
                    return                
                if not await is_openai_imagegen_model_available(api_key, model_name):
                    await interaction.followup.send(f"❌ ImageGenモデル `{model_name}` は利用できません", ephemeral=True)
                    return
            else:
                raise ValueError("Unsupported provider")

        except ValueError as e:
            await interaction.followup.send("❌ 現在は provider='OpenAI' のみ対応しています", ephemeral=True)
            return

        # 保存（ユーザーごとのセッション管理）
        user_session_manager.set_session(interaction.user.id, auth_json)

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
