import datetime
import discord
from discord import app_commands, Interaction, Thread, ChannelType
from discord_handler import service_name
from typing import Optional
from common.utils.thread_utils import add_thread_to_server

HELP_TEXT = {
    "usage": "/ac_newchat <title> <private>",
    "description": "🔒 スレッド内使用不可: AIチャットとの新しいスレッドを作成します。"
}

@app_commands.command(name="ac_newchat", description=HELP_TEXT["description"])
@app_commands.describe(title="スレッドのタイトルを指定できます")
@app_commands.describe(private="プライベートスレッドに指定できます（規定値=False）")
async def ac_newchat_command(interaction: Interaction, title: Optional[str] = None, private: Optional[bool] = False):
    # 🔒 スレッド内では使用不可
    if isinstance(interaction.channel, Thread):
        await interaction.response.send_message(
            "❌ このコマンドは **スレッド内では使用できません**。\n"
            "通常のテキストチャンネルで実行してください。",
            ephemeral=True
        )
        return

    try:
        now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        user_name = interaction.user.display_name

        if title:
            thread_name = f"{title}"
        else:
            thread_name = f"{user_name} - {now_str}"

        channel_type = ChannelType.private_thread if private else ChannelType.public_thread
        thread = await interaction.channel.create_thread(
            name=thread_name,
            type=channel_type,
            auto_archive_duration=1440,
            invitable=False
        )
        await interaction.response.send_message(
            f"✅ スレッド [`{thread_name}`] を作成しました。",
            ephemeral=True
        )
        add_thread_to_server(service_name, interaction.guild_id, thread.id)
        await thread.send(
            f"💬/ac_newchat: このスレッドは {interaction.user.mention} によって作成されました。\n"
            f"・このスレッド内でのメッセージは、投稿者が登録した認証情報に基づいて AI に送信・応答されます。"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ スレッド作成に失敗しました：{str(e)}",
            ephemeral=True
        )

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_newchat_command, guild=guild)
    else:
        tree.add_command(ac_newchat_command)
