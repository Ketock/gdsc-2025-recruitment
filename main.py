import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import google.generativeai as genai


# Configure Gemini API
GEMINI_API_KEY = "your-gemini-api-key-here"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro") 

WELCOME_MESSAGE = 'Wsg bruh {member}, have fun'
WELCOME_GIF_URL = 'https://i.gifer.com/7Jg9.gif'

NUMBER_EMOJIS = ["1️⃣", "2️⃣",]

class Client(commands.Bot):
    async def on_ready(self):  #sending the green flag to terminal about bot coming online
        print(f'Logged as {self.user}')
        try:
            await self.tree.sync()  # Syncing slash commands
            print(f"Slash commands synced successfully")
        except Exception as e:
            print(f"Failed to sync commands: {e}")


    async def on_member_join(self, member):    
        channel = discord.utils.get(member.guild.text_channels, name="general")  # sub the name to the channel you want to deliver the welcome message at (will update this later)
        if channel:
            embed = discord.Embed(
                title="Yo",
                description=WELCOME_MESSAGE.format(member=member.mention),
                color=discord.Color.blue()
            )
            embed.set_image(url=WELCOME_GIF_URL) 
            await channel.send(embed=embed)
    
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello")

    async def respond_with_gemini(self, interaction: discord.Interaction, query: str):
        try:
            if not query:
                await interaction.response.send_message("Please provide a query!", ephemeral=True)
                return

            response = model.generate_content(query)
            reply_text = response.text if hasattr(response, "text") else "I couldn't generate a response."

            # sad discord 2000 chara text limit :(
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await interaction.response.send_message(reply_text)
        except Exception as e:
            await interaction.response.send_message("Error processing request. Try again later.", ephemeral=True)
            print(f"Error: {e}")
    
    async def summarize(self, interaction: discord.Interaction, query: str):
        try:
            if not query:
                await interaction.response.send_message("Please provide a text to summarize!", ephemeral=True)
                return
            prompt = f"Summarize the following text in under 2000 characters:\n\n{query}"
            response = model.generate_content(prompt)
            summary = response.text if hasattr(response, "text") else "I couldn't generate a summary"
            
            if len(summary) > 2000:
                summary = summary[:1997] + "..."

            await interaction.response.send_message(summary)
        
        except Exception as e:
            await interaction.response.send_message("Error processing request. Try again later.", ephemeral=True)
            print(f"Error: {e}")

    async def poll(self, interaction: discord.Interaction, content:str, option1:str, option2:str):
        
        options = [option1,option2]
        options = [option for option in options if option]

        if len(options) < 2:
            await interaction.response.send_message("Can't create a poll with less than 2 option", ephemeral=True)
            return
        embed = discord.Embed(title="Poll", description=f"**{content}**", color=discord.Colour.blue())
        poll_message = ""
        for i, option in enumerate(options):
            poll_message += f"{NUMBER_EMOJIS[i]} **{option}**\n"
        
        embed.add_field(name="Options", value=poll_message, inline=False)
        embed.set_footer(text=f"Poll created by {interaction.user.name}")

        await interaction.response.send_message(embed=embed)
        poll_msg =  await interaction.original_response()

        for i in range(len(options)):
            await poll_msg.add_reaction(NUMBER_EMOJIS[i])

    def get_guild_queue(self, guild_id):
        if guild_id not in SONG_QUEUE:
            SONG_QUEUE[guild_id] = []
        return SONG_QUEUE[guild_id]
    
    async def queue(self, interaction: discord.Interaction):
        queue = get_guild_queue(interaction.guild.id)

        if not queue:
            await interaction.response.send_message("Empty queue lmfao", ephemeral=True)
            return
        embed = discord.embed(title = "Song Queue", colour=discord.Colour.red())
        queue_text = "\n".join([f"**{i+1}.** {song}" for i,song in enumerate(queue)])
        embed.add_field(name="Current Songs:",value=queue_text,inline = False)
        await interaction.response.send_message(embed=embed)

    async def queue_add(self, interaction: discord.Interaction, song: str):
        queue = get_guild_queue(interaction.guild.id)
        queue.append(song)
        await interaction.response.send_message(f"Added **{song}** to the queue")

    async def queue_remove(self, interaction: discord.Interaction, position: int):
        queue = get_guild_queue(interaction.guild.id)
        if position < 1 or position > len(queue):
            await interaction.response.send_message(f"Invalid Song position", ephemeral=True)
            return
        removed_song=queue.pop(position-1)
        await interaction.response.send_message(f"Removed **{removed_song}** from the queue")
    
    async def queue_clear(self, interaction: discord.Interaction):
        queue = get_guild_queue(interaction.guild.id)
        if queue == []:
            await interaction.response.send_message(f"There is nothing in the queue!", ephemeral=True)
            return
        queue = []
        await interaction.response.send_message(f"The queue has been **cleared**")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Client(command_prefix='!', intents=intents)

@client.tree.command(name='respond', description="generate message response with gemini")
@app_commands.describe(query="Your question for the AI")
async def respond(interaction: discord.Interaction, query: str):
    await client.respond_with_gemini(interaction, query)

@client.tree.command(name='summarize', description="Summarize your text with gemini")
@app_commands.describe(query="Your question for the AI")
async def summarize(interaction: discord.Interaction, query: str):
    await client.summarize(interaction, query)

@client.tree.command(name='poll', description="create poll")
async def poll(interaction: discord.Interaction, question:str, option1:str, option2:str):
    await client.poll(interaction,question,option1,option2)

@client.tree.command(name='queue', description="view queue")
async def queue(interaction: discord.Interaction):
    await client.queue(interaction)

@client.tree.command(name='queue_add', description="add songs to queue")
async def queue_add(interaction: discord.Interaction, song:str):
    await client.queue_add(interaction,song)

@client.tree.command(name='queue_remove', description="remove song from the queue")
async def queue_remove(interaction: discord.Interaction, position:int):
    await client.queue_remove(interaction,position)

@client.tree.command(name='queue_clear', description="clear the queue")
async def queue_clear(interaction: discord.Interaction):
    await client.queue_clear(interaction)

client.run('your-discord-bot-token') #insert token here



