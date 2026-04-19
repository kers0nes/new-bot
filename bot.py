import discord
from discord.ext import commands
import asyncio
import aiohttp
from config import DISCORD_TOKEN, PREFIX
from roblox_scraper import RobloxScriptFinder
from keep_alive import keep_alive
import json
from datetime import datetime
import random

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
script_finder = RobloxScriptFinder()

# Cooldown system
user_cooldowns = {}

# Script cache
script_cache = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}find <script> | {PREFIX}help"))

@bot.command(name='find')
async def find_script(ctx, *, query: str):
    """Find Roblox scripts by name/keyword"""
    user_id = ctx.author.id
    
    # Cooldown check (5 seconds per user)
    if user_id in user_cooldowns:
        time_diff = (datetime.now() - user_cooldowns[user_id]).total_seconds()
        if time_diff < 5:
            await ctx.send(f"⏰ Please wait {5 - int(time_diff)} seconds before searching again!")
            return
    
    user_cooldowns[user_id] = datetime.now()
    
    # Send typing indicator
    async with ctx.typing():
        await asyncio.sleep(1)  # Small delay to show typing
        
        # Search for scripts
        results = await script_finder.search_scripts(query)
        
        if not results:
            embed = discord.Embed(
                title="❌ No Scripts Found",
                description=f"Couldn't find any scripts for `{query}`",
                color=discord.Color.red()
            )
            embed.add_field(name="Try:", value="• Different keywords\n• More specific terms\n• Check spelling", inline=False)
            await ctx.send(embed=embed)
            return
        
        # Create embed for results
        embed = discord.Embed(
            title=f"🔍 Roblox Scripts for: {query}",
            description=f"Found {len(results)} results",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for i, script in enumerate(results[:5], 1):
            embed.add_field(
                name=f"{i}. {script['title']}",
                value=f"**Source:** {script['source']}\n**Link:** {script['url']}\n**Description:** {script['description'][:100]}...",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {ctx.author.name} | Use !view <number> to see script content")
        
        # Store results in cache
        cache_key = f"{ctx.author.id}_{ctx.message.id}"
        script_cache[cache_key] = results
        await ctx.send(embed=embed)
        
        # Send follow-up message with numbers
        await ctx.send("💡 **Tip:** Use `!view 1` to see the content of the first script (numbers 1-5)")

@bot.command(name='view')
async def view_script(ctx, number: int):
    """View content of a script from last search"""
    cache_key = None
    for key in script_cache.keys():
        if key.startswith(str(ctx.author.id)):
            cache_key = key
            break
    
    if not cache_key:
        await ctx.send("❌ No recent search found! Use `!find <script>` first.")
        return
    
    results = script_cache[cache_key]
    if number < 1 or number > len(results):
        await ctx.send(f"❌ Invalid number! Please choose between 1 and {len(results)}")
        return
    
    script = results[number - 1]
    
    async with ctx.typing():
        content = script_finder.extract_script_content(script['url'])
        
        embed = discord.Embed(
            title=f"📝 Script Content: {script['title']}",
            description=f"**Source:** {script['source']}\n**URL:** {script['url']}",
            color=discord.Color.green()
        )
        
        # Check if content is too long
        if len(content) > 1024:
            # Split into multiple fields
            chunks = [content[i:i+1024] for i in range(0, len(content), 1024)]
            for i, chunk in enumerate(chunks[:3]):  # Max 3 chunks
                embed.add_field(name=f"Content (Part {i+1})", value=f"```lua\n{chunk}\n```", inline=False)
            if len(chunks) > 3:
                embed.add_field(name="Note", value="Script too long, showing first 3 parts. Check the link for full script.", inline=False)
        else:
            embed.add_field(name="Content", value=f"```lua\n{content}\n```", inline=False)
        
        await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="🤖 Roblox Script Finder Bot",
        description="Find and share Roblox scripts easily!",
        color=discord.Color.purple()
    )
    
    embed.add_field(name=f"{PREFIX}find <script>", value="Search for Roblox scripts", inline=False)
    embed.add_field(name=f"{PREFIX}view <number>", value="View script content from search results", inline=False)
    embed.add_field(name=f"{PREFIX}popular", value="Show popular script categories", inline=False)
    embed.add_field(name=f"{PREFIX}ping", value="Check bot latency", inline=False)
    embed.add_field(name=f"{PREFIX}info", value="Bot information", inline=False)
    
    embed.set_footer(text="⚠️ Disclaimer: Use scripts at your own risk. Only use scripts you trust!")
    await ctx.send(embed=embed)

@bot.command(name='popular')
async def popular_categories(ctx):
    """Show popular script categories"""
    categories = {
        "🔫 Combat": "Aimbot, ESP, Silent Aim",
        "🏃 Movement": "Speed, Fly, Noclip",
        "💰 Farming": "Auto-farm, Auto-collect",
        "🎮 Game Specific": "Arsenal, MM2, Jailbreak scripts",
        "🛠️ Utilities": "Admin commands, GUI libraries"
    }
    
    embed = discord.Embed(
        title="🔥 Popular Script Categories",
        color=discord.Color.gold()
    )
    
    for category, examples in categories.items():
        embed.add_field(name=category, value=examples, inline=False)
    
    embed.add_field(name="💡 Tip", value=f"Use `{PREFIX}find <category>` to search for these!", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: {latency}ms",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def bot_info(ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        description="A powerful Roblox script finder bot",
        color=discord.Color.blue()
    )
    embed.add_field(name="Version", value="1.0.0", inline=True)
    embed.add_field(name="Commands", value=f"{len(bot.commands)}", inline=True)
    embed.add_field(name="Servers", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="Creator", value="Your Name", inline=True)
    embed.add_field(name="Hosting", value="Render + GitHub", inline=True)
    embed.add_field(name="Uptime", value="24/7", inline=True)
    
    embed.set_footer(text="⚠️ Disclaimer: This bot is for educational purposes only")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found! Use `{PREFIX}help` to see all commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Example: `{PREFIX}find aimbot`")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")

# Run the bot with keep_alive
if __name__ == "__main__":
    keep_alive()  # Start Flask server
    bot.run(DISCORD_TOKEN)
