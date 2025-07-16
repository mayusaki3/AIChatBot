import discord
from common.session.thread_context_manager import ThreadContextManager

class DiscordThreadContextManager:
    def __init__(self):
        self.manager = ThreadContextManager()
        self.initialized_threads = set()

    # スレッドIDごとに未初期化ならコンテキスト履歴を追加
    async def ensure_initialized(self, thread: discord.Thread):
        if thread.id in self.initialized_threads:
            return
        await self.load_context_from_history(thread)
        self.initialized_threads.add(thread.id)

    # スレッドIDごとにコンテキスト履歴を追加
    async def load_context_from_history(self, thread: discord.Thread):
        messages = []
        async for msg in thread.history(limit=100, oldest_first=False):
            if msg.author.bot:
                if "/ac_summary: " in msg.content or "/ac_newtopic: " in msg.content:
                    break
            messages.append(msg)
        for msg in reversed(messages):
            self.manager.append_context(thread.id, f"{msg.author.name}: {msg.content}")

    # スレッドIDごとにメッセージを追加
    def append_context(self, thread_id: str, content: str):
        self.manager.append_context(thread_id, content)

    # スレッドIDごとにコンテキストを取得
    def get_context(self, thread_id: str):
        return self.manager.get_context(thread_id)

    # スレッドIDごとにコンテキストをクリア
    def clear(self, thread_id: str):
        self.manager.clear_context(thread_id)

    # スレッドIDが初期化されているか確認
    def is_initialized(self, thread_id: str):
        return thread_id in self.initialized_threads

# シングルトンとして使うインスタンス
context_manager = DiscordThreadContextManager()