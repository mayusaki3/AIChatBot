import discord
from common.session.thread_context_manager import ThreadContextManager

class DiscordThreadContextManager:
    def __init__(self):
        self.manager = ThreadContextManager()
        self.initialized_threads = set()

    # スレッドIDごとにコンテキストを取得
    async def ensure_initialized(self, thread: discord.Thread):
        if thread.id in self.initialized_threads:
            return
        await self.load_context_from_history(thread)
        self.initialized_threads.add(thread.id)

    # スレッドIDごとにコンテキストを追加
    async def load_context_from_history(self, thread: discord.Thread):
        messages = []
        async for msg in thread.history(limit=100, oldest_first=False):
            if msg.author.bot:
                continue
            if "/ac_summary" in msg.content or "/ac_newtopic" in msg.content:
                break
            messages.append(msg)
        for msg in reversed(messages):
            self.manager.add_context(thread.id, "user", msg.content)

    # スレッドIDごとにメッセージを追加
    def add_message(self, thread_id: int, role: str, content: str):
        self.manager.add_context(thread_id, role, content)

    # スレッドIDごとにコンテキストを取得
    def get_context(self, thread_id: int):
        return self.manager.get_context(thread_id)

    # スレッドIDごとにコンテキストをクリア
    def clear(self, thread_id: int):
        self.manager.clear_context(thread_id)

    # スレッドIDが初期化されているか確認
    def is_initialized(self, thread_id: int):
        return thread_id in self.initialized_threads

# シングルトンとして使うインスタンス
context_manager = DiscordThreadContextManager()