# サーバーID毎にセッション情報をメモリ上で管理する。
# セッション情報として、以下の内容を保持する。
# - auth_data      :  認証情報
# - system_option  :  システムオプション
class ServerSessionManager:
    def __init__(self):
        self.sessions = {}
        self.system_options = {}

    # サーバーIDごとに認証情報を登録。
    def set_session(self, server_id: int, auth_data: dict):
        server_id = str(server_id)
        self.sessions[server_id] = auth_data

    # 指定サーバーのセッション情報を削除。
    def clear_session(self, server_id: int):
        server_id = str(server_id)
        self.sessions.pop(server_id, None)

    # 指定サーバーのセッション情報を取得。
    def get_session(self, server_id: int):
        server_id = str(server_id)
        return self.sessions.get(server_id)

    # 指定サーバーのセッションが存在するか確認。
    def has_session(self, server_id: int) -> bool:
        server_id = str(server_id)
        return server_id in self.sessions

    # システムオプション設定
    def set_option(self, server_id: int, key: str, value: bool) -> None:
        sid = str(server_id)
        key = key.lower()
        opts = self.system_options.setdefault(sid, {})
        opts[key] = bool(value)
    
    # システムオプション取得
    def get_option(self, server_id: int, key: str, default: bool | None = None) -> bool | None:
        sid = str(server_id)
        key = key.lower()
        return self.system_options.get(sid, {}).get(key, default)

    # システムオプション削除
    def clear_option(self, server_id: int, key: str) -> None:
        sid = str(server_id)
        key = key.lower()
        if sid in self.system_options:
            self.system_options[sid].pop(key, None)
            if not self.system_options[sid]:
                self.system_options.pop(sid, None)

    # 全システムオプション取得
    def all_options(self, server_id: int) -> dict[str, bool]:
        return dict(self.system_options.get(str(server_id), {}))

# シングルトンとして使うインスタンス
server_session_manager = ServerSessionManager()
