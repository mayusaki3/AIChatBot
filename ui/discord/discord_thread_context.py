import discord
from common.session.thread_context_manager import ThreadContextManager

class DiscordThreadContextManager:
    def __init__(self):
        self.manager = ThreadContextManager()
        self.initialized_threads = set()

    # スレッドIDごとに未初期化ならコンテキスト履歴を追加
    async def ensure_initialized(self, thread: discord.Thread):
        thread_id = str(thread.id)
        if thread_id in self.initialized_threads:
            return
        await self.load_context_from_history(thread)

    # スレッドIDごとにコンテキスト履歴を追加
    async def load_context_from_history(self, thread: discord.Thread):
        print(f"L [START]: {thread.name}")
        thread_id = str(thread.id)
        self.clear_context(thread_id)
        prefixes = ("⚠️ 認証情報を", "💬/ac_newchat:", "💬/ac_invite:", "💬/ac_leave:", "💬/ac_newtopic:", "💬/ac_summary:")
        skip_prefixes = ("⚠️ 認証情報を", "💬/ac_newchat:", "💬/ac_invite:", "💬/ac_leave:")
        messages = []
        async for msg in thread.history(limit=100, oldest_first=False):
            if msg.author.bot:
                # 無視すべきBotメッセージか
                if any(msg.content.startswith(p) for p in skip_prefixes):
                    # print(f"  [SKIP ]: {msg.content}")
                    continue
                # 要約が見つかったら内容を含めて処理終了
                if msg.content.startswith("💬/ac_summary:"):
                    lines = msg.content.splitlines()
                    if len(lines) > 2:
                        msg.content = "\n".join(lines[2:])  # 3行目以降のみ使用
                        print(f"  [要約 ]: {msg.content}")
                        messages.append(msg)
                    break
                # 新規トピックが見つかったら終了
                if msg.content.startswith("💬/ac_newtopic:"):
                    break
            print(f"  [MSG  ]: {msg.content}")
            messages.append(msg)
        for msg in reversed(messages):
            self.manager.append_context(thread.id, f"{msg.author.name}: {msg.content}")
        print(f"L [END  ]: {thread.name}")

    # スレッドIDごとにメッセージを追加
    def append_context(self, thread_id: str, content: str):
        self.manager.append_context(thread_id, content)

    # スレッドIDごとにコンテキストを取得
    def get_context(self, thread_id: str):
        return self.manager.get_context(thread_id)

    # スレッドIDごとにコンテキストをクリア
    def clear_context(self, thread_id: str):
        thread_id = str(thread_id)
        if not thread_id in self.initialized_threads:
            self.initialized_threads.add(thread_id)
            print(f"- [INIT ]: {thread_id}")
        self.manager.clear_context(thread_id)

    # スレッドIDごとにコンテキストをリセット
    def reset_context(self, thread_id: str):
        thread_id = str(thread_id)
        if thread_id in self.initialized_threads:
            self.initialized_threads.remove(thread_id)
            print(f"- [RESET]: {thread_id}")
        self.manager.clear_context(thread_id)

    # スレッドIDが初期化されているか確認
    def is_initialized(self, thread_id: str):
        thread_id = str(thread_id)
        return thread_id in self.initialized_threads

# シングルトンとして使うインスタンス
context_manager = DiscordThreadContextManager()