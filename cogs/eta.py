import discord
from discord.ui import Modal, InputText, View
from discord.ext import tasks, commands
from discord.commands import ApplicationContext, SlashCommandGroup

from datetime import time, datetime
from pytz import timezone as tz

def print_times(times):
    for time in times:
        print(time)

class pre_modal_button(View):
    @discord.ui.button(label="Add ETA", custom_id="add", style=discord.ButtonStyle.primary)
    async def add(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Adding", ephemeral=True)
    @discord.ui.button(label="View ETAs", custom_id="view", style=discord.ButtonStyle.primary)
    async def view(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Viewing", ephemeral=True)

class eta_form(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="hour (1-12)", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="minute (0-59)", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="am/pm", style=discord.InputTextStyle.short))
        self.val1 = None
        self.val2 = None
        self.val3 = None
        self.user = None

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            self.val1 = int(self.children[0].value)
            self.val2 = int(self.children[1].value)
            self.val3 = self.children[2].value
            self.user = interaction.user
            await interaction.followup.send("Finished", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("Invalid input", ephemeral=True)
            print("Invalid input")
            print(e)
        self.stop()

    def add_to_etas(self, etas):
        if etas == None:
            etas = []
        for eta in etas:
            if eta[0] == self.user.name:
                etas.remove(eta)
        etas.append((self.user.name, self.val1, self.val2, self.val3))
        return etas

class ETA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.eta_loop.start()

    current_time = datetime.now(tz('EST'))
    # one minute from now
    one_minute = time(current_time.hour, current_time.minute + 1, 0, tzinfo=tz('EST'))
    schedule = [one_minute]
    etas = []

    eta = SlashCommandGroup(name="eta", description="ETA commands", )

    @tasks.loop(time=schedule)
    async def eta_loop(self):
        print('requesting etas...')
        users = self.bot.get_all_members()
        valid_roles = ['Sewer King', 'Las Vegas Lackey']
        valid_users = []
        # remove bots
        for user in users:
            has_valid_role = False
            if user.roles == None:
                continue
            for role in user.roles:
                if role.name in valid_roles:
                    has_valid_role = True
            if not user.bot and has_valid_role:
                valid_users.append(user)
        for user in valid_users:
            if user.id == 293100675133341699:
                await user.send(view=pre_modal_button())

    @eta_loop.before_loop
    async def before_eta(self):
        await self.bot.wait_until_ready()
        print("About to start updating leaderboard.")
        print_times(self.schedule)
        await self.send_message(1082451720556249158, "starting leaderboard... \
                current time is: " + str(datetime.now(tz('EST'))))

    @eta_loop.after_loop
    async def after_eta(self):
        print("Stopped updating leaderboard.")
        print_times(self.schedule)

    @eta_loop.error
    async def eta_error(self, error):
        print(f"Oh no, an error occurred while updating the leaderboard. Error: {error}")

    @eta.command(name="add", description="Add a time to the leaderboard")
    async def add(self, ctx: ApplicationContext):
        eta_f = eta_form(title="test")
        await ctx.send_modal(eta_f)
        await eta_f.wait()
        print("Finished waiting")
        if eta_f.val1 != None and eta_f.val2 != None and eta_f.user != None:
            self.etas = eta_f.add_to_etas(self.etas)
            print("Added to etas")
            print_times(self.etas)

    @eta.command(name="view", description="Check etas")
    async def show_etas(self, ctx):
        if self.etas == None:
            await ctx.respond("No etas yet")
            return
        if len(self.etas) == 0:
            await ctx.respond("No etas yet")
            return
        await ctx.respond("Here are the etas:")
        for eta in self.etas:
            await ctx.respond(f"{eta[0]}: {eta[1]}:{eta[2]}")

    async def send_message(self, channel, message):
        await self.bot.get_channel(channel).send(message)

def setup(bot):
    bot.add_cog(ETA(bot))
