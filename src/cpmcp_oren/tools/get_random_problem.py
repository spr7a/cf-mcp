import random
import httpx
from urllib.parse import quote
from .get_problemlist import fetch_all_problems

BASE_URL = "https://codeforces.com/api/"

async def fetch_user_rating(username: str):
    """Fetch just the current rating to keep the API call lightweight."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"{BASE_URL}user.info?handles={quote(username)}"
        resp = await client.get(url)
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError("User not found")
        user = data["result"][0]
        # If user is unrated (no rating key), default to 800
        return user.get("rating", 800)

async def get_random_problem_suggestion(username: str):
    try:
        rating = await fetch_user_rating(username)
        if rating < 800:
            rating = 800
        
        min_r = max(800, rating - 300)
        max_r = rating + 300

        # Fetch the entire Codeforces problem set and filter locally
        all_problems = await fetch_all_problems()
        
        candidates = []
        for p in all_problems:
            r = p.get('rating')
            # Only include problems that actually have a rating
            if r is not None and min_r <= r <= max_r:
                candidates.append(p)

        if not candidates:
            return {"error": f"No problems found in the range {min_r} - {max_r}. Try a wider range."}

        # Pick a completely random problem
        return random.choice(candidates)

    except Exception as e:
        return {"error": str(e)}