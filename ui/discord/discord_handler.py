import discord
from common.core.chatbot_core import get_chat_response
from common.utils.file_io import parse_auth_file

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

session_data = {}

@client.event
async def on_ready():
    print(f"[INFO] Bot is logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith('.json'):
            file_bytes = await attachment.read()
            session_data[message.author.id] = parse_auth_file(file_bytes)
            await message.channel.send("✅ 認証情報を受け取りました。メッセージを送ってください。")
            return

    if message.author.id not in session_data:
        await message.channel.send("⚠️ 先に認証ファイル（JSON）をアップロードしてください。")
        return

    auth = session_data[message.author.id]
    prompt = message.content
    response = get_chat_response(auth["openai_api_key"], prompt)
    await message.channel.send(response)

def start_discord_bot():
    import os
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        token = input("Enter your Discord Bot Token: ")
    client.run(token)
