import os
import json
import httpx
from typing import Dict, List, Any
from fastmcp import FastMCP
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GitHub Dev Card Tools")

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

GITHUB_API_URL = "https://api.github.com"

@mcp.tool()
async def scrape_github(username: str) -> Dict[str, Any]:
    """Fetch basic GitHub profile data and top repositories for a user."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Dev-Card-Generator"
    }
    
    # Optional: use GITHUB_TOKEN if provided for higher rate limits
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as http_client:
        # Fetch user profile
        user_res = await http_client.get(f"{GITHUB_API_URL}/users/{username}")
        if user_res.status_code != 200:
            raise Exception(f"Failed to fetch user {username}: {user_res.text}")
        user_data = user_res.json()

        # Fetch repos
        repos_res = await http_client.get(f"{GITHUB_API_URL}/users/{username}/repos?sort=updated&per_page=100")
        if repos_res.status_code != 200:
            raise Exception(f"Failed to fetch repos for {username}")
        repos = repos_res.json()

        # Sort by stars and take top 6
        sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
        
        top_repos = []
        for r in sorted_repos:
            top_repos.append({
                "name": r.get("name"),
                "stars": r.get("stargazers_count"),
                "language": r.get("language"),
                "description": r.get("description")
            })

        # Aggregate languages
        languages_count = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                languages_count[lang] = languages_count.get(lang, 0) + 1
        
        sorted_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
        top_languages = [lang for lang, count in sorted_langs[:5]]

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "avatar_url": user_data.get("avatar_url"),
            "top_repos": top_repos,
            "top_languages": top_languages
        }

@mcp.tool()
async def analyze_profile(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze GitHub data using Gemini 2.5 Flash to infer developer vibe and skills."""
    
    prompt = f"""
    Analyze this GitHub profile data and provide a personality assessment in JSON format.
    Data: {json.dumps(github_data)}

    Return exactly this JSON structure:
    {{
        "developer_vibe": "1 sentence personality",
        "top_skills": ["skill1", "skill2", "skill3"],
        "fun_fact": "something clever inferred from their repos",
        "card_theme": "one of: hacker, builder, researcher, designer, open-source-hero"
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", # Using available model from list
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    return json.loads(response.text)

@mcp.tool()
async def generate_card_html(username: str, github_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """Generate a beautiful, self-contained HTML dev card string."""
    
    theme_configs = {
        "hacker": {"bg": "#000000", "text": "#00ff00", "border": "#00ff00", "accent": "#008f11"},
        "builder": {"bg": "#0d1117", "text": "#ffffff", "border": "#30363d", "accent": "#238636"},
        "researcher": {"bg": "#f6f8fa", "text": "#24292f", "border": "#d0d7de", "accent": "#0969da"},
        "designer": {"bg": "#fff0f6", "text": "#a61e4d", "border": "#ffa8bc", "accent": "#f06595"},
        "open-source-hero": {"bg": "#1a0633", "text": "#e9d5ff", "border": "#7c3aed", "accent": "#a855f7"}
    }
    
    theme = analysis.get("card_theme", "builder")
    config = theme_configs.get(theme, theme_configs["builder"])
    
    skills_badges = "".join([f'<span style="padding: 2px 8px; border-radius: 12px; border: 1px solid {config["text"]}; font-size: 10px; margin-right: 5px;">{s}</span>' for s in analysis.get("top_skills", [])])
    
    repo_items = "".join([
        f'<div style="margin-bottom: 8px;">'
        f'<div style="font-weight: bold; font-size: 14px;">→ {r["name"]} <span style="font-weight: normal; font-size: 11px; opacity: 0.7;">★ {r["stars"]}</span></div>'
        f'<div style="font-size: 11px; opacity: 0.8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{r["description"] or "No description"}</div>'
        f'</div>'
        for r in github_data.get("top_repos", [])[:3]
    ])

    html = f"""
    <div style="width: 350px; background-color: {config['bg']}; color: {config['text']}; border: 2px solid {config['border']}; border-radius: 12px; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <img src="{github_data['avatar_url']}" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid {config['accent']}; margin-right: 15px;">
            <div>
                <div style="font-weight: bold; font-size: 18px;">{github_data['name']}</div>
                <div style="font-size: 12px; opacity: 0.7;">@{username}</div>
            </div>
        </div>
        
        <div style="font-style: italic; margin-bottom: 15px; font-size: 14px; line-height: 1.4;">"{analysis['developer_vibe']}"</div>
        
        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 15px;">
            {skills_badges}
        </div>
        
        <div style="display: flex; justify-content: space-around; border-top: 1px solid {config['border']}; border-bottom: 1px solid {config['border']}; padding: 10px 0; margin-bottom: 15px; text-align: center;">
            <div>
                <div style="font-weight: bold; font-size: 16px;">{github_data['public_repos']}</div>
                <div style="font-size: 10px; text-transform: uppercase;">Repos</div>
            </div>
            <div>
                <div style="font-weight: bold; font-size: 16px;">{github_data['followers']}</div>
                <div style="font-size: 10px; text-transform: uppercase;">Followers</div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="font-size: 10px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.6;">Featured Projects</div>
            {repo_items}
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 9px; opacity: 0.5; border-top: 1px solid {config['border']}; pt: 10px;">
            <span>{analysis['fun_fact']}</span>
            <span style="font-weight: bold;">GITHUB DEV CARD</span>
        </div>
    </div>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Save the HTML card to a static file and return the relative URL path."""
    # Ensure static directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static", "cards")
    os.makedirs(static_dir, exist_ok=True)
    
    file_name = f"{username}.html"
    file_path = os.path.join(static_dir, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return f"/static/cards/{file_name}"

if __name__ == "__main__":
    mcp.run()
