import json

import discord
from discord.ext import commands

from config.config import DISCORD_TOKEN
from scripts.producer import monProducer
from config.logging_config import setup_logging
from scripts.postgresdb import PostgresConnector

logger = setup_logging()

producer = monProducer()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

postgresconn = PostgresConnector()
postgresconn.create_table()

def is_valid_string(s):
    return all(c.isalnum() or c.isspace() for c in s)

def create_embed(title, url, price, src):
    embed = discord.Embed(
        title=title,
        url=url,
        color=discord.Color.blue()
    )
    embed.add_field(name="💰 Price", value=price, inline=False)
    embed.set_image(url=src)
    return embed

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.command()
async def launch(ctx, *, subject):
    try:
        if is_valid_string(subject):
            webhooks = await ctx.channel.webhooks()
            if webhooks:
                webhook_url = webhooks[0].url
                data = {
                    "subject": subject,
                    "webhook_url": webhook_url
                }
                data_bytes = json.dumps(data).encode('utf-8')

                producer.send_message_to_topic(subject=data_bytes)
                logger.info(f"The message {data} has been successfully sent to a Kafka partition.")            

            else:
                await ctx.send("You need to create a webhook for this channel first.")
        else:
            await ctx.send(f"'{subject}' can only contain letters and numbers.")

    except Exception as e:
        logger.error(f"Error detected: {e}")

@bot.command()
async def history(ctx, *, subject):
    try:
        if is_valid_string(subject):
            results = postgresconn.offer_history(subject)

            if results != []:
                for row in results:
                    logger.info(f"{row[1], row[3], row[2], row[4]}")
                    embed = create_embed(row[1], row[3], row[2], row[4])
                    await ctx.send(embed=embed)

            else:
                await ctx.send(f"Nothing found for {subject}.")

    except Exception as e:
        logger.error(f"Error detected: {e}")
        
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)