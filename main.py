import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import google.generativeai as genai


# Configure Gemini API
GEMINI_API_KEY = "your-gemini-api-key-here"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro") 

class Client(commands.Bot):
    async def on_ready(self):  #sending the green flag to terminal about bot coming online
        print(f'Logged as {self.user}')
        try:
            synced = await self.tree.sync()  # Syncing slash commands
            print(f"Slash commands synced successfully")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

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


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix='!', intents=intents)

@client.tree.command(name='respond', description="Generate message response with gemini")
@app_commands.describe(query="Your question for the AI")
async def respond(interaction: discord.Interaction, query: str):
    await client.respond_with_gemini(interaction, query)


client.run('your-discord-bot-token') #insert token here



