import httpx
from bs4 import BeautifulSoup
from .get_problemlist import fetch_all_problems

# Define a standard browser User-Agent to bypass Codeforces bot protection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def get_problem_details(contest_id: int, index: str):
    # 1. Get metadata (rating, topics) from the full problemset
    try:
        all_problems = await fetch_all_problems()
        meta = None
        for p in all_problems:
            if p.get('contestId') == contest_id and p.get('index') == index:
                meta = p
                break

        if not meta:
            return {"error": f"Problem {contest_id}/{index} not found in the Codeforces problemset."}
        
        rating = meta.get('rating', 'Unrated')
        topics = meta.get('tags', [])
    except Exception as e:
        return {"error": f"Failed to fetch problem metadata: {str(e)}"}

    # 2. Scrape the statement from the webpage
    url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"
    
    # Use the HEADERS dictionary to mimic a real browser
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        resp = await client.get(url)
        
        # Handle 403 specifically
        if resp.status_code == 403:
            return {"error": "Access blocked by Codeforces (HTTP 403). Try again later or use a valid browser User-Agent."}
        if resp.status_code != 200:
            return {"error": f"Failed to fetch problem page (HTTP {resp.status_code})"}
        
        soup = BeautifulSoup(resp.text, 'html.parser')

    statement_div = soup.find('div', class_='problem-statement')
    if not statement_div:
        return {"error": "Could not find the problem statement on the page."}

    # 3. Extract and clean the data with proper error handling
    try:
        # Remove unwanted scripts and styles
        for script in statement_div.find_all(['script', 'style']):
            script.decompose()
        
        # Extract title safely
        title_div = statement_div.find('div', class_='title')
        if not title_div:
            return {"error": "Could not find the problem title div on the page."}
        
        title = title_div.get_text(strip=True)
        
        # Replace line breaks with newlines
        for br in statement_div.find_all('br'):
            br.replace_with('\n\n')
        
        # Properly convert <pre> blocks into Markdown code blocks
        for pre in statement_div.find_all('pre'):
            code_content = pre.get_text()
            pre.replace_with(f"\n```text\n{code_content}\n```\n")
        
        # Add spacing between paragraphs
        for p in statement_div.find_all('p'):
            p.insert_before('\n\n')

        # Extract the final clean text
        statement_text = statement_div.get_text().strip()
        
        return {
            "title": title,
            "rating": rating,
            "topics": topics,
            "statement": statement_text,
            "url": url
        }
    except Exception as e:
        return {"error": f"Error parsing the problem statement: {str(e)}"}