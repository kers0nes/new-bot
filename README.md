# Roblox Script Finder Discord Bot

A Discord bot that finds and shares Roblox scripts from various sources.

## Commands
- `!find <script>` - Search for Roblox scripts
- `!view <number>` - View script content
- `!popular` - Show popular categories
- `!ping` - Check bot latency
- `!info` - Bot information

## Setup

### Local Development
1. Clone repository
2. Create `.env` file with `DISCORD_TOKEN=your_token_here`
3. Run `pip install -r requirements.txt`
4. Run `python bot.py`

### Deploy to Render
1. Push code to GitHub
2. Connect repository to Render
3. Add environment variable `DISCORD_TOKEN`
4. Deploy!

## Features
- 24/7 uptime with keep-alive
- Rate limiting per user
- Script content extraction
- Multiple source support
