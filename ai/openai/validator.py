import aiohttp

# 認証情報で指定されたAPIが利用可能かチェックする

OPENAI_CHAT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGEGEN_ENDPOINT = "https://api.openai.com/v1/images/generations"

# APIキーのチェック
async def is_valid_openai_key(api_key: str):
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=test_payload) as response:
                if response.status == 200:
                    return True
                elif response.status == 429:
                    if "insufficient_quota" in await response.text():
                        return "❌ 利用上限を超過しています。OpenAIの請求情報を確認してください。"
                    else:
                        return "❌ リクエストが多すぎます（429）。しばらく待って再試行してください。"
                elif response.status == 401:
                    return "❌ APIキーが無効です。"
                else:
                    return f"❌ 不明なエラー: {response.status} / {await response.text()}"

    except Exception as e:
        print(f"[validator] APIキー検証例外: {e}")
        return f"❌ 通信エラー: {e}"

# チャットモデルのチェック
async def is_openai_chat_model_available(api_key: str, model_name: str) -> bool:
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=test_payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"[validator] Chatモデル利用可否確認エラー: {e}")
        return False

# ビジョンモデルのチェック
async def is_openai_vision_model_available(api_key: str, model_name: str) -> bool:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    test_payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": "Describe this image."},
                {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/640px-PNG_transparency_demonstration_1.png"}}
            ]}
        ],
        "max_tokens": 10
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=test_payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"[validator] Visionモデル利用可否確認エラー: {e}")
        return False

# イメージ生成モデルのチェック
async def is_openai_imagegen_model_available(api_key: str, model_name: str) -> bool:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    test_payload = {
        "model": model_name,
        "prompt": "A cute baby sea otter",
        "n": 1,
        "size": "1024x1024"
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(OPENAI_IMAGEGEN_ENDPOINT, headers=headers, json=test_payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"[validator] ImageGenモデル利用可否確認エラー: {e}")
        return False
