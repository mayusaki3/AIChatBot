# ユーザーID毎にセッション情報をメモリ上で管理する。
# セッション情報として、以下の内容を保持する。
# - auth_data  :  認証情報
class UserSessionManager:
    def __init__(self):
        self.sessions = {}

    # ユーザーIDごとに認証情報を登録。
    def set_session(self, user_id: int, auth_data: dict):
        user_id = str(user_id)
        auth_data["user_id"] = user_id
        self.sessions[user_id] = auth_data

    # 指定ユーザーIDのセッション情報を削除。
    def clear_session(self, user_id: int):
        user_id = str(user_id)
        self.sessions.pop(user_id, None)

    # 指定ユーザーのセッション情報を取得。
    def get_session(self, user_id: int):
        user_id = str(user_id)
        return self.sessions.get(user_id)

    # 指定ユーザーのセッションが存在するか確認。
    def has_session(self, user_id: int) -> bool:
        user_id = str(user_id)
        return user_id in self.sessions


# シングルトンとして使うインスタンス
user_session_manager = UserSessionManager()
