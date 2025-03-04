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
async def respond(interaction: discord.Interaction, query: str):
    await client.respond_with_gemini(interaction, query)

client.run('your-discord-bot-token') #insert token here



