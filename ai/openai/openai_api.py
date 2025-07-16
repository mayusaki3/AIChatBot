from openai import AsyncOpenAI
from typing import Optional

# メイン関数：ChatGPTにメッセージ送信
async def call_chatgpt(user_message: str, api_key: str, model: str = "gpt-3.5-turbo") -> str:
    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ ChatGPT 応答エラー: {e}"
