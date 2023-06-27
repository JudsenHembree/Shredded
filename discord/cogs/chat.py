"""Chat with GPT3.5 via a discord cog"""
import discord

# using langchain to drive the conversation
from langchain.prompts import (
        PromptTemplate,
)
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory

from dotenv import dotenv_values
from discord.ui import Modal
from discord.ext import commands
from discord.commands import SlashCommandGroup, ApplicationContext

class ChatModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = kwargs.get("title", "Chat with GPT3.5")
        self.add_item(discord.ui.InputText(label="Thread Name", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Initial prompt", style=discord.InputTextStyle.long))
        self.val0 = None
        self.val1 = None

    async def callback(self, interaction: discord.Interaction):
        try:
            self.val0 = self.children[0].value
            self.val1 = self.children[1].value
        except Exception as e:
            print(e)
        if self.val0 is None or self.val1 is None:
            await interaction.response.send_message("Please fill out all fields", ephemeral=True)
            print("Please fill out all fields")
            return
        embed = discord.Embed(title="Chat with GPT3.5")
        embed.add_field(name="Thread Name", value=self.val0)
        embed.add_field(name="Initial prompt", value=self.val1)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        # call stop to close the modal
        self.stop()

class ChatCog(commands.Cog):
    """Chat with GPT3.5 via a discord cog"""
    def __init__(self, bot, openai_key: str):
        self.bot = bot
        self.chains = {}
        self.key = openai_key

        self.template = """You are a chatbot talking with one to many participants.
        You have a gymbro personality. 
        {History}
        {Message}
        AI: """

        self.chat_prompt_template = PromptTemplate(
                input_variables=["History", "Message"],
                template=self.template,
                )

        self.chat_gpt = ChatOpenAI(temperature=0.9, 
                                   model="gpt-3.5-turbo",
                                   openai_api_key=openai_key)

    def create_chain(self, openai_key: str):
        chain = LLMChain(
                llm=self.chat_gpt,
                prompt=self.chat_prompt_template,
                verbose=True,
                memory=ConversationSummaryBufferMemory(llm=OpenAI(openai_api_key=openai_key,
                                                                  temperature=0.9),
                                                       memory_key="History")
                )
        return chain

    def spawn_chain(self, thread_id: int):
        """Spawn a new chain"""
        if thread_id not in self.chains:
            self.chains[thread_id] = self.create_chain(self.key)
        else:
            print("Chain already exists")
        return self.chains[thread_id]

    def check_for_thread(self, thread_id: int):
        """Check if a thread exists"""
        if thread_id in self.chains:
            print("Thread exists")
            return True, self.chains[thread_id]
        return False, None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        channel = message.channel.id
        user = message.author.name
        if channel in self.chains:
            chain = self.chains[channel]
            response = await chain.apredict(Message=user + ": " + message.content)
            await message.channel.send(response)

    chatter = SlashCommandGroup("chat", "Chat with GPT3.5")
    
    async def call_gpt(self, ctx: ApplicationContext, prompt: str, thread_name: str):
        """Call GPT3.5 via langchain"""
        print("Calling GPT3.5")
        # get the channel for the thread
        channel = ctx.channel
        user = ctx.author.name
        if channel is None or user is None:
            print("Channel or user is None")
            return
        # create a thread with the thread name
        if channel is not None:
            try:
                thread = await channel.create_thread(name=thread_name,
                                                     type=discord.ChannelType.public_thread)
                chain = self.spawn_chain(thread.id)
                response = await chain.apredict(Message=user + ": " + prompt)
                await thread.send(response)
                await channel.send("Thread created", embed=\
                        discord.Embed(title=thread_name, \
                        description=f"Thread created at {thread.id}"))
            except Exception as e:
                print(e)
        else:
            print("Channel is None")
            return

        # create a prompt with the initial prompt
        
    @chatter.command(name="chat", description="Start a chat thread")
    async def chat(self, ctx: ApplicationContext):
        """Chat with GPT3.5"""
        chat = ChatModal(title="Chat with GPT3.5")
        await ctx.send_modal(chat)
        await chat.wait()
        thread_name = chat.val0
        initial_prompt = chat.val1
        if thread_name is None or initial_prompt is None:
            await ctx.send("Please fill out all fields")
            print("Please fill out all fields")
            return
        await self.call_gpt(ctx, initial_prompt, thread_name)

def setup(bot):
    """Add the cog to the bot"""
    dotenv = dotenv_values(".env")
    if dotenv['OPENAI_KEY'] is None:
        print("No OpenAI key found in .env file")
        return
    bot.add_cog(ChatCog(bot, dotenv['OPENAI_KEY']))
