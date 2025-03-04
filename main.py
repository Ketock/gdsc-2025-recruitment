import discord
from discord.ext import commands,tasks
from discord import app_commands
import asyncio
import google.generativeai as genai
import yt_dlp
from datetime import datetime, timedelta


# Configure Gemini API
GEMINI_API_KEY = "your-gemini-api-key-here"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro") 

WELCOME_MESSAGE = 'Wsg bruh {member}, have fun'
WELCOME_GIF_URL = 'https://i.gifer.com/7Jg9.gif'

NUMBER_EMOJIS = ["1️⃣", "2️⃣",]

SONG_QUEUE = {}

reminders = {}

class Client(commands.Bot):

    @tasks.loop(seconds=30)
    async def check_reminder(self):
        now = datetime.now()
        for user_id, reminder_list in list(reminders.items()):
            for reminder in reminder_list[:]:
                reminder_time, message, reminder_id = reminder
                if now>= reminder_time:
                    user = await client.fetch_user(user_id)
                    await user.send(f"**Reminder:** {message}")
                    reminder_list.remove(reminder) # auto deletes the expired reminders
    
    
    async def on_ready(self):  #sending the green flag to terminal about bot coming online
        print(f'Logged as {self.user}')
        try:
            await self.tree.sync()  # Syncing slash commands
            print(f"Slash commands synced successfully")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        if not self.check_reminder.is_running():
            self.check_reminder.start()


    async def on_member_join(self, member):    
        channel = discord.utils.get(member.guild.text_channels, name="general")  # Change to your welcome channel name
        if channel:
            embed = discord.Embed(
                title="Yo",
                description=WELCOME_MESSAGE.format(member=member.mention),
                color=discord.Color.blue()
            )
            embed.set_image(url=WELCOME_GIF_URL)  # Add the welcome GIF
            await channel.send(embed=embed)

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
            poll_message += f"{NUMBER_EMOJIS[i]} **{option}**\n\n"
        
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
        queue = self.get_guild_queue(interaction.guild.id)

        if not queue:
            await interaction.response.send_message("Empty queue lmfao", ephemeral=True)
            return
        embed = discord.Embed(title = "Song Queue", colour=discord.Colour.red())
        queue_text = "\n".join([f"**{i+1}.** {song}" for i,song in enumerate(queue)])
        embed.add_field(name="Current Songs:",value=queue_text,inline = False)
        await interaction.response.send_message(embed=embed)

    async def queue_add(self, interaction: discord.Interaction, song: str):
        queue = self.get_guild_queue(interaction.guild.id)
        queue.append(song)
        await interaction.response.send_message(f"Added **{song}** to the queue")

    async def queue_remove(self, interaction: discord.Interaction, position: int):
        queue = self.get_guild_queue(interaction.guild.id)
        if position < 1 or position > len(queue):
            await interaction.response.send_message(f"Invalid Song position", ephemeral=True)
            return
        removed_song=queue.pop(position-1)
        await interaction.response.send_message(f"Removed **{removed_song}** from the queue")
    
    async def queue_clear(self, interaction: discord.Interaction):
        queue = self.get_guild_queue(interaction.guild.id)
        if queue == []:
            await interaction.response.send_message(f"There is nothing in the queue!", ephemeral=True)
            return
        queue = []
        await interaction.response.send_message(f"The queue has been **cleared**")
    
    def get_user_reminder(self,user_id):
        
        if user_id not in reminders:
            reminders[user_id] = []
        return reminders[user_id]


            
    async def reminder(self, interaction: discord.Interaction, action:str, date:str = None, time:str = None, message:str = None, reminder_id:int = None):
        
        await interaction.response.defer() # for timeout issues
        user_id = interaction.user.id
        user_reminders = self.get_user_reminder(user_id)

        if action.lower() == 'create':
            try:
                reminder_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                if reminder_datetime < datetime.now():
                    await interaction.followup.send("Can't set a reminder in past", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("Invalid date or time format! Use `YYYY-MM-DD HH:MM`.", ephemeral=True)
                return
        
            new_id = len(user_reminders) + 1
            user_reminders.append((reminder_datetime,message,new_id))
            await interaction.followup.send(f"Reminder for `{date} {time}`: {message} has been set")
        
        elif action.lower() == 'list':
            if not user_reminders:
                await interaction.followup.send("No active reminders for the user", ephemeral=True)
                return

            reminder_text = "\n".join([f"**ID {r[2]}:** {r[0].strftime('%Y-%m-%d %H:%M')} - {r[1]}" for r in user_reminders])
            embed = discord.Embed(title="Your Reminders", description=reminder_text, color=discord.Color.purple())
            await interaction.followup.send(embed=embed)
        
        elif action.lower() == 'delete':
            if not reminder_id or not any(r[2] == reminder_id for r in user_reminders):
                await interaction.followup.send("Invalid reminder id", ephemeral=True)
                return
            
            reminders[user_id] = [r for r in user_reminders if r[2] != reminder_id]
            await interaction.followup.send(f"Reminder **ID {reminder_id}** deleted successfully")


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

@client.tree.command(name='reminder',description="set/delete/modify/view reminder")
@app_commands.describe(
    action="Action to perform (create, list, delete, modify)",
    date="Reminder date (YYYY-MM-DD) (for create/modify)",
    time="Reminder time (HH:MM 24-hour format) (for create/modify)",
    message="Reminder message (for create/modify)",
    reminder_id="Reminder ID to delete/modify (for delete/modify)"
)
async def reminder(interaction: discord.Interaction, action:str, date:str = None, time:str = None, message:str = None, reminder_id:int = None):
    await client.reminder(interaction, action, date, time, message, reminder_id)

client.run('your-discord-bot-token') #insert token here



