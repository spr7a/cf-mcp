import httpx
import asyncio
from urllib.parse import quote

BASE_URL = "https://codeforces.com/api/"

async def fetch_json(url: str):
    """Helper to fetch JSON from Codeforces API."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError(f"Codeforces API Error: {data.get('comment', 'Unknown error')}")
        return data["result"]

async def fetch_and_parse_user_data(username: str):
    """Fetches user info, contest history, and submission stats in parallel."""
    try:
        # Define the 3 API calls
        async def get_info():
            url = f"{BASE_URL}user.info?handles={quote(username)}"
            result = await fetch_json(url)
            return result[0]

        async def get_contests():
            url = f"{BASE_URL}user.rating?handle={quote(username)}"
            return await fetch_json(url)

        async def get_submissions():
            url = f"{BASE_URL}user.status?handle={quote(username)}&count=1000"
            return await fetch_json(url)

        # Run them all at the exact same time
        user_info, contest_history, submissions = await asyncio.gather(
            get_info(), get_contests(), get_submissions()
        )

        # --- Process Info ---
        rating = user_info.get("rating", "Unrated")
        max_rating = user_info.get("maxRating", "N/A")
        title = user_info.get("rank", "Unranked")
        max_title = user_info.get("maxRank", "Unranked")
        total_contests = len(contest_history)
        recent_5 = contest_history[-5:] if total_contests >= 5 else contest_history

        # --- Process Submissions (Distinct solved problems) ---
        solved_problems = set()
        category_stats = {}
        difficulty_stats = {}

        for sub in submissions:
            if sub["verdict"] != "OK":
                continue
            problem = sub["problem"]
            
            if "contestId" in problem and "index" in problem:
                prob_id = f"{problem['contestId']}{problem['index']}"
                if prob_id in solved_problems:
                    continue
                solved_problems.add(prob_id)

                for tag in problem.get("tags", []):
                    category_stats[tag] = category_stats.get(tag, 0) + 1

                rating_val = problem.get("rating")
                if rating_val:
                    difficulty_stats[str(rating_val)] = difficulty_stats.get(str(rating_val), 0) + 1
                else:
                    difficulty_stats["Unrated"] = difficulty_stats.get("Unrated", 0) + 1

        total_solved = len(solved_problems)
        top_10_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "status": "ok",
            "rating": rating,
            "max_rating": max_rating,
            "title": title,
            "max_title": max_title,
            "total_contests": total_contests,
            "total_solved": total_solved,
            "recent_5": recent_5,
            "difficulty_stats": difficulty_stats,
            "top_10_categories": top_10_categories
        }

    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}