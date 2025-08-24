from openai import AsyncOpenAI
import aiohttp, base64, asyncio

OPENAI_IMAGEGEN_ENDPOINT = "https://api.openai.com/v1/images/generations"

# 認証情報で指定されたAPIを呼び出す

# ChatGPTにメッセージ送信
async def call_chatgpt(context_list: list[dict], api_key: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1024) -> str:
    messages = []
    for msg in context_list:
        if msg.startswith("AIChatBot:"):
            messages.append({"role": "assistant", "content": msg.replace("AIChatBot:", "", 1).strip()})
        else:
            messages.append({"role": "user", "content": msg})

    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI 応答エラー: {e}"

# 画像生成APIを呼び出す
async def generate_image_from_prompt(prompt: str, api_key: str, model: str, size: str, quality: str, timeout_sec: int = 60) -> bytes:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    if model == "dall-e-3":
        payload["response_format"] = "b64_json"
    
    timeout = aiohttp.ClientTimeout(total=timeout_sec)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(OPENAI_IMAGEGEN_ENDPOINT, headers=headers, json=payload) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"OpenAI image gen failed: {resp.status} / {data}")
           
        if not data.get("data"):
            raise RuntimeError(f"OpenAI image gen empty response: {data}")

        first = data["data"][0]

        # 1) b64_json があればそれを使う
        b64 = first.get("b64_json")
        if b64:
            return base64.b64decode(b64)

        # 2) URL の場合はダウンロードしてバイト化
        url = first.get("url")
        if url:
            async with aiohttp.ClientSession(timeout=timeout) as session2:
                async with session2.get(url) as img_resp:
                    if img_resp.status != 200:
                        raise RuntimeError(f"Download image failed: {img_resp.status}")
                    return await img_resp.read()

        # どちらも無い場合は失敗
        raise RuntimeError(f"OpenAI image gen: neither b64_json nor url in response: {first}")
