import discord
from discord import app_commands, Interaction, Thread
from discord_handler import service_name
from common.session.user_session_manager import session_manager
from common.utils.thread_utils import is_thread_managed
from ui.discord.discord_thread_context import context_manager
from ai.openai.openai_api import call_chatgpt

HELP_TEXT = {
    "usage": "/ac_summary",
    "description": "現在のトピックを要約して、その内容で新しくトピックを始めます。以前の会話内容は忘れます。"
}

@app_commands.command(name="ac_summary", description=HELP_TEXT["description"])
async def ac_summarycommand(interaction: Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if not isinstance(interaction.channel, Thread):
        await interaction.followup.send("❌ スレッド外では実行できません。", ephemeral=True)
        return

    thread = interaction.channel
    if not is_thread_managed(service_name, interaction.guild_id, thread.id):
        await interaction.followup.send("❌ AIChatBotはこのスレッドに参加していません。", ephemeral=True)
        return

    # 認証情報チェック
    user_id = interaction.user.id
    if not session_manager.has_session(user_id):
        await interaction.followup.send("⚠️ 認証情報を /ac_auth で登録してください。")
        return

    if not context_manager.is_initialized(thread.id):
        await context_manager.ensure_initialized(thread)

    # メッセージをAIに送信
    user_auth = session_manager.get_session(user_id)
    context_list = context_manager.get_context(thread.id)
    if len(context_list) == 0:
        await interaction.followup.send("❌ 要約する内容がありません。", ephemeral=True)
        return
    message_list = []
    message_list.append(f"AIChatBot: {user_auth['summary_prompt']}\n")
    for message in context_list:
        message_list.append(message)

    # OpenAIの場合
    reply = ""
    if user_auth["provider"] == "OpenAI":
        reply = await call_chatgpt(message_list, user_auth["api_key"], user_auth["model"])

    await thread.send(
        f"💬/ac_summary: 要約した内容で新しくトピックを始めます。\n"
        f"・取り消す場合は、このメッセージを削除してから /ac_loadtopic を実行してください。\n"
        f"{reply}"
    )
    context_manager.reset_context(thread.id)
    await interaction.followup.send("✅ ここまでの内容を要約しました。")

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_summarycommand, guild=guild)
    else:
        tree.add_command(ac_summarycommand)
