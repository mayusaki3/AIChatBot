import discord
from discord import app_commands
import importlib.util
import os

HELP_TEXT = {
    "usage": "/ac_help",
    "description": "すべての /ac_ コマンドのヘルプを表示します。"
}

COMMANDS_DIR = os.path.dirname(__file__)

@app_commands.command(name="ac_help", description=HELP_TEXT["description"])
async def ac_help_command(interaction: discord.Interaction):
    help_messages = []

    for filename in os.listdir(COMMANDS_DIR):
        if filename.startswith("ac_") and filename.endswith(".py"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"ui.discord.commands.{module_name}")
                help_text = getattr(module, "HELP_TEXT", None)
                if isinstance(help_text, dict):
                    usage = help_text.get("usage", f"/{module_name}")
                    desc = help_text.get("description", "(未定義)")
                    help_messages.append(f"**/{module_name}**\n使い方: {usage}\n説明: {desc}")
                else:
                    help_messages.append(f"**/{module_name}**\n使い方: /{module_name}\n説明: (ヘルプ未定義)")
            except Exception as e:
                help_messages.append(f"**/{module_name}**\nエラー: {e}")

    embed = discord.Embed(
        title="AIChatBot コマンドヘルプ",
        description="\n\n".join(help_messages),
        color=0x00ffcc
    )
    await interaction.response.send_message(embed=embed)

def register(tree: app_commands.CommandTree, client: discord.Client, guild: discord.Object = None):
    if guild:
        tree.add_command(ac_help_command, guild=guild)
    else:
        tree.add_command(ac_help_command)
