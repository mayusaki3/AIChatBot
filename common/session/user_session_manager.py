class UserSessionManager:
    def __init__(self):
        self.sessions = {}  # user_id: {provider, api_key, model}

    # ユーザーIDごとに認証情報を登録。
    def set_session(self, user_id: int, auth_data: dict):
        user_id = str(user_id)
        if "provider" not in auth_data:
            auth_data["provider"] = "openai"  # デフォルトプロバイダ
        if "model" not in auth_data:
            auth_data["model"] = "gpt-3.5-turbo"  # デフォルトモデル
        self.sessions[user_id] = auth_data

    # 指定ユーザーのセッション情報を取得。
    def get_session(self, user_id: int):
        user_id = str(user_id)
        return self.sessions.get(user_id)

    # 指定ユーザーのセッションが存在するか確認。
    def has_session(self, user_id: int) -> bool:
        user_id = str(user_id)
        return user_id in self.sessions

# シングルトンとして使うインスタンス
session_manager = UserSessionManager()