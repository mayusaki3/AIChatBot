import discord
from discord import app_commands
import importlib.util
import os

HELP_TEXT = "AIチャットBotで使用できるコマンド一覧を表示します。"

COMMANDS_DIR = os.path.join(os.path.dirname(__file__))

class HelpCommand(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="ac_help",
            description="使用できる /ac_ コマンドの一覧を表示します",
            callback=self.callback
        )

    async def callback(self, interaction: discord.Interaction):
        help_messages = []

        for filename in os.listdir(COMMANDS_DIR):
            if not filename.startswith("ac_") or not filename.endswith(".py"):
                continue
            if filename == "ac_help.py":
                continue

            module_name = filename[:-3]
            module_path = os.path.join(COMMANDS_DIR, filename)

            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                cmd_name = f"/{module_name}"
                cmd_help = getattr(module, "HELP_TEXT", "（ヘルプ未定義）")
                help_messages.append(f"**{cmd_name}**\n{cmd_help}")
            except Exception as e:
                # ロード失敗は無視
                continue

        embed = discord.Embed(title="📘 使用可能な /ac_ コマンド", color=discord.Color.blue())
        embed.description = "\n\n".join(help_messages) if help_messages else "利用可能なコマンドが見つかりませんでした。"

        await interaction.response.send_message(embed=embed, ephemeral=True)
