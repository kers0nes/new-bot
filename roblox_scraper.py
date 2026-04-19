import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict

class RobloxScriptFinder:
    def __init__(self):
        self.sources = {
            'v3rmillion': 'https://v3rmillion.net/forumdisplay.php?fid=168',
            'github': 'https://github.com/search?q=roblox+script+executor',
        }
    
    async def search_scripts(self, query: str) -> List[Dict]:
        results = []
        
        # Search GitHub
        github_results = await self.search_github(query)
        results.extend(github_results)
        
        # Search pastebin-like sites
        paste_results = await self.search_paste_sites(query)
        results.extend(paste_results)
        
        return results[:10]  # Limit to 10 results
    
    async def search_github(self, query: str) -> List[Dict]:
        try:
            url = f"https://api.github.com/search/repositories?q=roblox+script+{query}+in:file&per_page=5"
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for repo in data.get('items', []):
                    results.append({
                        'title': repo['name'],
                        'url': repo['html_url'],
                        'description': repo.get('description', 'No description'),
                        'source': 'GitHub',
                        'stars': repo.get('stargazers_count', 0)
                    })
                return results
        except Exception as e:
            print(f"GitHub search error: {e}")
        return []
    
    async def search_paste_sites(self, query: str) -> List[Dict]:
        results = []
        # Search pastebin (via Google dork simulation)
        try:
            search_url = f"https://pastebin.com/search?q=roblox+script+{query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                # Basic parsing (simplified)
                results.append({
                    'title': f'Pastebin results for {query}',
                    'url': search_url,
                    'description': 'Check Pastebin for scripts',
                    'source': 'Pastebin',
                    'stars': 0
                })
        except Exception as e:
            print(f"Pastebin search error: {e}")
        return results

    def extract_script_content(self, url: str) -> str:
        """Extract script content from various sources"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if 'github' in url:
                # Try to get raw content
                raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                raw_response = requests.get(raw_url, headers=headers)
                if raw_response.status_code == 200:
                    return raw_response.text[:1900]  # Discord limit
            
            elif 'pastebin' in url:
                # Get raw pastebin content
                if 'pastebin.com' in url and not 'raw' in url:
                    paste_id = url.split('/')[-1]
                    raw_url = f'https://pastebin.com/raw/{paste_id}'
                    raw_response = requests.get(raw_url, headers=headers)
                    if raw_response.status_code == 200:
                        return raw_response.text[:1900]
            
            return "Could not extract script content. Please check the link manually."
        except Exception as e:
            return f"Error extracting script: {str(e)}"
