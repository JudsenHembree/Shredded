"""Chat with GPT3.5 via a discord cog"""
import discord
from discord.ui import Modal
from discord.ext import commands
from discord.commands import SlashCommandGroup

async def Chat(user, message, chain):
    """Chat with GPT3.5"""
    response = await chain.apredict(Message=user + ": " + message)
    return response

class ChatModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Thread Name", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Initial prompt", style=discord.InputTextStyle.long))
        self.val1 = None
        self.val2 = None

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            self.val1 = self.children[0].value
            self.val2 = self.children[1].value
        except Exception as e:
            print("Invalid input")
            print(e)
        await interaction.followup.send("Finished", ephemeral=True)
        self.stop()

    def add_to_threads(self, etas):
        if etas == None:
            etas = []
        etas.append(self.val1)
        return etas

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chain = None

    @commands.command(name="chat")
    async def chat(self, ctx):
        """Chat with GPT3.5"""
        chat = ChatModal()

    @commands.command(name="chat_init")
    async def chat_init(self, ctx):
        """Initialize chat with GPT3.5"""
