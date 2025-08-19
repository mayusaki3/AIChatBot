import inspect
import discord
from discord import app_commands, Interaction, Thread
from discord_handler import service_name
from common.session.user_session_manager import user_session_manager
from common.session.server_session_manager import server_session_manager
from common.utils.thread_utils import is_thread_managed
from ui.discord.discord_thread_context import context_manager

HELP_TEXT = {
    "usage": "/ac_status <option>",
    "description": "使用中のあいちゃぼの状態を表示します。"
}

# optionの解析（スペース区切りを想定）
def _parse_flags(option: str | None) -> set[str]:
    if not option:
        return set()
    return {tok.strip() for tok in option.split() if tok.strip().startswith("-")}

# 非同期処理
async def _maybe_await(result):
    return await result if inspect.isawaitable(result) else result

@app_commands.command(name="ac_status", description=HELP_TEXT["description"])
@app_commands.describe(option="追加の指示: -exp=現スレッドのコンテキストをエクスポート, -expall=全スレッドのコンテキストをエクスポート")
async def ac_status_command(interaction: Interaction, option: str = None):
    await interaction.response.defer(thinking=True, ephemeral=True)

    flags = _parse_flags(option)
    thread = interaction.channel
    msg_lines: list[str] = []
    managed = False

    # スレッド管理状況
    if isinstance(thread, Thread):
        # スレッドIDでスレッド情報取得（存在しない場合は None）
        if not is_thread_managed(service_name, interaction.guild_id, thread.id):
            msg_lines.append("ℹ️ このスレッドであいちゃぼと会話するには /ac_invite であいちゃぼを招待してください。")
        else:
            managed = True
    else:
        msg_lines.append("ℹ️ あいちゃぼとの会話はスレッド内でのみ利用できます。")

    # 共有されたユーザー認証情報の状態
    guild = interaction.guild
    guild_id = interaction.guild.id
    server_auth = server_session_manager.get_session(guild_id)
    if server_auth:
        sharing_user_id = server_auth.get("user_id")
        member = guild.get_member(sharing_user_id) or await guild.fetch_member(sharing_user_id)
        user_name = (member.display_name if member else f"id: {sharing_user_id}")
        auth = (
            f"🗨️{server_auth['chat']['provider']}/{server_auth['chat']['model']}, "
            f"👀{server_auth['vision']['provider']}/{server_auth['vision']['model']}, "
            f"🖼️{server_auth['imagegen']['provider']}/{server_auth['imagegen']['model']}"
        )
        msg_lines.append(f"ℹ️ {user_name} さんの認証情報［ {auth} ］が共有されています。")

    # ユーザー認証情報の確認
    user_id = interaction.user.id
    user_auth = user_session_manager.get_session(user_id)
    if user_auth:
        auth = (
            f"🗨️{user_auth['chat']['provider']}/{user_auth['chat']['model']}, "
            f"👀{user_auth['vision']['provider']}/{user_auth['vision']['model']}, "
            f"🖼️{user_auth['imagegen']['provider']}/{user_auth['imagegen']['model']}"
        )
        msg_lines.append(f"🧑‍💻 現在の認証情報［ {auth} ］")
    else:
        if not server_auth:
            msg_lines.append("⚠️ あいちゃぼと会話するには /ac_auth で認証情報を登録してください。")

    # AIチャットスレッドのコンテキスト状態
    if managed:
        if not context_manager.is_initialized(thread.id):
            await context_manager.ensure_initialized(thread)
        context = context_manager.get_context(thread.id)
        if context:
            msg_lines.append(f"📜 スレッドのコンテキスト履歴は {len(context)} 件あります。")
            if option == "d":
                msg_lines.append("")
                msg_lines.append("📜 コンテキスト履歴:")
                for mm in context:
                    msg_lines.append(f"🟡{mm['message']}")
                    msg_lines.append(f"   - Id: {mm['msgid']}, Ref: {mm['refid']}")
                    msg_lines.append(f"   - Attachment: {mm['attachments']}")
        else:
            msg_lines.append("📜 スレッドのコンテキスト履歴はありません。")

    # option処理: -expall オプション, -exp オプション
    export_msgs: list[str] = []
    if "-expall" in flags:
        try:
            res = await _maybe_await(context_manager.export_all_contexts())
            # res が dict の場合のヒント処理
            if isinstance(res, dict):
                count = res.get("count", 0)
                outdir = res.get("dir", "common/session/dump")
                export_msgs.append(f"🗂️ 全スレッド（{count} 件）のコンテキスト履歴を `{outdir}` にエクスポートしました。")
            else:
                export_msgs.append("🗂️ 全スレッドのコンテキスト履歴をエクスポートしました。")
        except Exception as e:
            export_msgs.append(f"❌ 全スレッドのエクスポートに失敗しました: {e}")
    elif "-exp" in flags:
        if isinstance(thread, Thread):
            try:
                res = await _maybe_await(context_manager.export_context(thread.id))
                if isinstance(res, dict):
                    path = res.get("path", "")
                    export_msgs.append(f"💾 このスレッドのコンテキスト履歴をエクスポートしました。{f'`{path}`' if path else ''}")
                else:
                    export_msgs.append("💾 このスレッドのコンテキスト履歴をエクスポートしました。")
            except Exception as e:
                export_msgs.append(f"❌ このスレッドのエクスポートに失敗しました: {e}")
        else:
            export_msgs.append("⚠️ スレッド外では `-exp` は使用できません。")

    if export_msgs:
        msg_lines.append("")
        msg_lines.extend(export_msgs)

    await interaction.followup.send("\n".join(msg_lines), ephemeral=True)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_status_command, guild=guild)
    else:
        tree.add_command(ac_status_command)
