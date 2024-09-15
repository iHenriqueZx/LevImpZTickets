import discord
from discord.ext import commands
from discord.ui import Select, View
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="l!", intents=intents)

ATENDIMENTO_CATEGORY_ID = Your_ID

CATEGORY_OPTIONS = [
    "Suporte.",
    "Solicitar Plugins.",
    "Solicitar Builds.",
    "Solicitar Sites.",
    "Solicitar Bots."
]

ATENDIMENTO_CHANNEL_ID = Your_ID

class CategorySelect(Select):
    def __init__(self):
        options = [discord.SelectOption(label=option) for option in CATEGORY_OPTIONS]
        super().__init__(placeholder="Selecione uma categoria.", options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=ATENDIMENTO_CATEGORY_ID)
        
        if not category:
            await interaction.response.send_message("Categoria de atendimento não encontrada.", ephemeral=True)
            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await category.create_text_channel(f'ticket-{interaction.user.name}', overwrites=overwrites)

        color = int('18fcf2', 16)
        embed = discord.Embed(
            title="TICKET ABERTO",
            description=(
                f"Olá {interaction.user.mention}, obrigado por abrir um ticket.\n"
                f"Categoria: {self.values[0]}\n"
                "Um membro do suporte estará com você em breve."
            ),
            color=color
        )

        await channel.send(embed=embed)
        await interaction.response.send_message(f'Ticket criado: {channel.mention}', ephemeral=True)
        
        self.view.clear_items()
        self.view.add_item(CategorySelect())
        await interaction.message.edit(view=self.view)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())

@bot.tree.command(name='close')
@commands.has_role('Suporte')
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message(f"Seu ticket será fechado por {interaction.user.mention} em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("Este comando só pode ser usado em canais de tickets.", ephemeral=True)

@close.error
async def close_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')
    channel = bot.get_channel(ATENDIMENTO_CHANNEL_ID)
    if channel:
        color = int('18fcf2', 16)
        
        embed = discord.Embed(
            title="📩 CENTRAL DE ATENDIMENTO",
            description=(
                "Olá jogador(a), está necessitando do auxílio da nossa equipe relacionado a um problema ou esclarecer dúvidas?\n\n"
                "• Selecione uma das opções abaixo para que possamos lhe ajudar com seus problemas ou dúvidas\n"
                "• O seu atendimento será realizado de forma privada apenas com membros da equipe."
            ),
            color=color
        )
        await channel.send(embed=embed, view=TicketView())
    await bot.tree.sync()

bot.run('Your_Token')
