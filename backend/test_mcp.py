import asyncio
import os
import json
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card
from dotenv import load_dotenv

load_dotenv()

async def test_end_to_end():
    username = "torvalds"
    print(f"--- Testing for user: {username} ---")
    
    try:
        # 1. Scrape GitHub
        print("Step 1: Scraping GitHub...")
        github_data = await scrape_github(username)
        print("Successfully scraped data.")
        
        # 2. Analyze Profile
        print("Step 2: Analyzing profile with Gemini...")
        analysis = await analyze_profile(github_data)
        print("Successfully analyzed profile.")
        
        # 3. Generate Card HTML
        print("Step 3: Generating HTML card...")
        card_html = await generate_card_html(username, github_data, analysis)
        print("Successfully generated HTML card.")
        
        # 4. Save Card
        print("Step 4: Saving card...")
        file_path = await save_card(username, card_html)
        print(f"Card saved to: {file_path}")
        
        # Output results
        print("\n--- Results ---")
        print(f"Card Theme: {analysis.get('card_theme')}")
        print(f"Developer Vibe: {analysis.get('developer_vibe')}")
        
    except Exception as e:
        print(f"\n[!] Test Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
