import requests

OPENAI_CHAT_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# APIキーのチェック
def is_valid_openai_key(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    test_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    try:
        response = requests.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=test_payload, timeout=10)
        if response.status_code == 200:
            return True
        elif response.status_code == 429:
            if "insufficient_quota" in response.text:
                return "❌ 利用上限を超過しています。OpenAIの請求情報を確認してください。"
            else:
                return "❌ リクエストが多すぎます（429）。しばらく待って再試行してください。"
        elif response.status_code == 401:
            return "❌ APIキーが無効です。"
        else:
            return f"❌ 不明なエラー: {response.status_code} / {response.text}"

    except Exception as e:
        print(f"[validator] APIキー検証例外: {e}")
        return f"❌ 通信エラー: {e}"

# チャットモデルのチェック
def is_chat_model_available(api_key: str, model_name: str) -> bool:
    """指定モデルが chat API で利用可能か検証"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    test_payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    try:
        response = requests.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=test_payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"[validator] モデル利用可否確認エラー: {e}")
        return False
