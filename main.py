import discord

class Client(discord.Client):
    async def on_ready(self):  #sending the green flag to terminal about bot coming online
        print(f'Logged as {self.user}') 

    async def on_message(self,message): # message log type thing to monitor 
        print(f'Message from {message.author}:{message.content}')


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('') #insert token here

