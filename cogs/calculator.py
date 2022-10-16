import discord
from discord import app_commands
from discord.ext import commands
from simpcalc import simpcalc


class InteractiveView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.expr = ""
        self.calc = simpcalc.Calculate()

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="1", row=0)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "1"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="2", row=0)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "2"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="3", row=0)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "3"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="+", row=0)
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "+"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="4", row=1)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "4"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="5", row=1)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "5"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="6", row=1)
    async def six(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "6"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="÷", row=1)
    async def divide(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "/"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="7", row=2)
    async def seven(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "7"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="8", row=2)
    async def eight(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "8"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="9", row=2)
    async def nine(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "9"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="x", row=2)
    async def multiply(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "*"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label=".", row=3)
    async def dot(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "."
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="0", row=3)
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "0"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="=", row=3)
    async def equal(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.expr = await self.calc.calculate(self.expr)
        except Exception: 
            return await interaction.response.send_message("ERROR")
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="-", row=3)
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "-"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label="(", row=4)
    async def left_bracket(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += "("
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.green, label=")", row=4)
    async def right_bracket(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr += ")"
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.red, label="C", row=4)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr = ""
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

    @discord.ui.button(style=discord.ButtonStyle.red, label="<==", row=4)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.expr = self.expr[:-1]
        await interaction.response.edit_message(content=f"```\n{self.expr}\n```")

class Cal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Calculator Cog is now ready!")

    @commands.hybrid_command(name="calculator", description="計算機", with_app_command=True)    
    async def cal(self, ctx:commands.Context):
        view = InteractiveView()
        await ctx.send("```\n```",view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Cal(bot))