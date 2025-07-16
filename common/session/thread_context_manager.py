# スレッド単位のコンテキストを管理
class ThreadContextManager:
    def __init__(self):
        self.contexts = {}  # thread_id -> list of messages

    # スレッドIDごとにコンテキストを取得
    def get_context(self, thread_id: str) -> list[str]:
        thread_id = str(thread_id)
        return self.contexts.get(thread_id, [])

    # スレッドIDごとにメッセージを追加
    def append_context(self, thread_id: str, message: str):
        thread_id = str(thread_id)
        if thread_id not in self.contexts:
            self.contexts[thread_id] = []
        self.contexts[thread_id].append(message)

    # スレッドIDごとにコンテキストをクリア
    def clear_context(self, thread_id: str):
        thread_id = str(thread_id)
        self.contexts[thread_id] = []

    # スレッドIDが存在するか確認
    def has_context(self, thread_id: str) -> bool:
        thread_id = str(thread_id)
        return thread_id in self.contexts

# シングルトンとして使うインスタンス
context_manager = ThreadContextManager()