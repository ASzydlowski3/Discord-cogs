import discord
from redbot.core import Config, commands
from .list import roles

class MyView(discord.ui.View):
    def create_button(label, id):
        @discord.ui.button(label=label, style=discord.ButtonStyle.success)
        async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
            user = interaction.user
            role = user.guild.get_role(id)
            await self.checkRole(interaction, role, user)
        return button

    for i, (role, role_id) in enumerate(roles.items()):
        func_name = f"button_{i}"
        locals()[func_name] = create_button(role, role_id)

    async def checkRole(self, interaction, role, user):
        if role.id in [y.id for y in user.roles]:
            await user.remove_roles(role)
            await interaction.response.send_message(f"Usunąłeś rolę {role.name}", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"Przypisano rolę {role.name}", ephemeral=True)


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channels = [1003996397739188294, 1004028454913724546]
        
    @commands.is_owner()
    @commands.command()
    async def roles(self, ctx):
        if ctx.channel.id in self.allowed_channels:
            embed = discord.Embed(title="Role na serwerze", description="Kliknij guzik żeby przypisać/usunąć rolę",
                                  colour=0x00FFFF)
            await ctx.send(embed=embed, view=MyView(timeout=None))