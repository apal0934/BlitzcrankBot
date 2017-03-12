'''
Created on 19Feb.,2017

@author: Alex Palmer
'''
import discord
import asyncio
import logging
import backoff
import traceback
import permissions
from discord.ext import commands
description = "Made by SuperFrosty#5263 for various Riot API related commands. Every command should be prefix'd with bl! (for example, bl!lookup)."
bot = commands.Bot(command_prefix=commands.when_mentioned_or('bl!'),
                    description=description)
startup_extensions = ['utilities', 'summoner', 'info', 'reload']
ownerID = '66141201631285248'

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='blitzcrank.log', encoding='utf-8',
                                    mode='w')
formatter = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)
file_handler.setFormatter(logging.Formatter(formatter))
discord_logger.addHandler(file_handler)

@bot.event
async def on_ready():
    game = 'bl!help | Fleshling Compatibility Service'
    await bot.change_presence(game=discord.Game(name=game))
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
    print('--------------------------------')

@bot.event
async def on_message(message):
    #eval command here because idk how to get it to work in cogs
    if message.content.startswith('bl!eval') and permissions.is_owner():
        parameters = ' '.join(message.content.strip().split(' ')[1:])
        output = None
        try:
            originalmessage = await bot.send_message(message.channel,
                    'Executing: ' + message.content + ' one moment, please...')
            output = eval(parameters)
        except:
            error = "```fix\n" + str(traceback.format_exc()) + "\n```"
            await bot.edit_message(originalmessage, error)
            traceback.print_exc()
        if asyncio.iscoroutine(output):
            output = await output
        if output:
            success = "```fix\n" + str(output) + "\n```"
            await bot.edit_message(originalmessage, success)
    await bot.process_commands(message)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel, error)
        pass
    elif isinstance(error, commands.CommandInvokeError):
        if str(error).startswith('Command raised an exception: APIError: Server returned error '
                                '404 on call'):
            errorMsg = "Could not find one of your arguments (most likely the summoner was not found, is under level 30, or has no ranked games this season)."
            await bot.send_message(ctx.message.channel, errorMsg)
            print(ctx.message.content)
            print(error)
        elif str(error).startswith("Command raised an exception: AttributeError: 'NoneType' object has no attribute 'id'"):
            errorMsg = "Please use capitals for champion names (i.e. 'Teemo' not 'teemo')."
            await bot.send_message(ctx.message.channel, errorMsg)
        if str(error).startswith('Command raised an exception: APIError: Server returned error '
                                '400 on call'):
            errorMsg = "Server returned empty values, this usually mean no mastery points found for given champion."
            await self.bot.send_message(ctx.message.channel, errorMsg)
            print(ctx.message.content)
            print(error)
        else:
            await bot.send_message(ctx.message.channel, error)
            print(ctx.message.content)
            print(error)

async def keep_running(bot, token):
    retry = backoff.ExponentialBackoff()

    while True:
        try:
            await bot.login(token)

        except (discord.HTTPException, aiohttp.ClientError):
            logging.exception("Attempting to login")
            await asyncio.sleep(retry.delay())

        else:
            break

    while bot.is_logged_in:
        if bot.is_closed:
            bot._closed.clear()
            bot.http.recreate()

        try:
            await bot.connect()

        except (discord.HTTPException, aiohttp.ClientError,
                discord.GatewayNotFound, discord.ConnectionClosed,
                websockets.InvalidHandshake,
                websockets.WebSocketProtocolError) as e:
            if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
                raise # Do not reconnect on authentication failure
            logging.exception("Attempting to login")
            await asyncio.sleep(retry.delay())
token = 'MjgyNzY1MjQzODYyNjE0MDE2.C4rRaw.FzkDxQ2Nq4Ul5gNibWRJ3EmH3Ag'

if __name__ == '__main__':
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    asyncio.get_event_loop().run_until_complete(keep_running(bot, token))
