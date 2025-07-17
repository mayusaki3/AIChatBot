import discord
from discord import app_commands, Interaction, Thread, ChannelType, Forbidden, HTTPException
from discord_handler import service_name
from common.utils.thread_utils import load_server_threads

HELP_TEXT = {
    "usage": "/ac_threads",
    "description": "AIチャットと会話中のスレッド一覧を表示します。"
}

@app_commands.command(name="ac_threads", description=HELP_TEXT["description"])
async def ac_threads_command(interaction: Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    thread_ids = load_server_threads(service_name, interaction.guild_id)
    if not thread_ids:
        await interaction.followup.send("📭 会話中のスレッドはありません。", ephemeral=True)
        return

    lines = ["🧵 会話中のスレッド一覧:"]
    for thread_id in thread_ids:
        try:
            thread = await interaction.guild.fetch_channel(thread_id)
            if isinstance(thread, Thread):
                is_private = thread.type == ChannelType.private_thread
                try:
                    # コマンド入力者がスレッドに参加しているかを確認
                    await thread.fetch_member(interaction.user.id)
                    user_is_member = True
                except (Forbidden, HTTPException):
                    user_is_member = False

                # 表示条件：パブリックスレッド or 参加済みプライベートスレッド
                if not is_private or user_is_member:
                    lines.append(f"- {thread.name}（ID: `{thread.id}`）")
                else:
                    lines.append(f"- ？？？？？（ID: `{thread.id}`）")
            else:
                lines.append(f"- ID: `{thread_id}`（スレッドではありません）")
        except Exception as e:
            lines.append(f"- ID: `{thread_id}`（取得失敗: {e}）")

    await interaction.followup.send("\n".join(lines), ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_threads_command, guild=guild)
    else:
        tree.add_command(ac_threads_command)
