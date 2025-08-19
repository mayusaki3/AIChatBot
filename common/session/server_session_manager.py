# サーバーID毎にセッション情報をメモリ上で管理する。
# セッション情報として、以下の内容を保持する。
# - auth_data  :  認証情報
class ServerSessionManager:
    def __init__(self):
        self.sessions = {}

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


# シングルトンとして使うインスタンス
server_session_manager = ServerSessionManager()
