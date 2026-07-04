import httpx
from urllib.parse import quote
from .get_problemlist import fetch_all_problems

BASE_URL = "https://codeforces.com/api/"

async def fetch_json(url: str):
    """Helper to fetch JSON from Codeforces API."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError(f"Codeforces API Error: {data.get('comment', 'Unknown error')}")
        return data["result"]

async def get_upsolve_suggestions(username: str):
    try:
        # 1. Fetch Current Rating
        user_info = await fetch_json(f"{BASE_URL}user.info?handles={quote(username)}")
        rating = user_info[0].get("rating", 800)
        if rating < 800: rating = 800

        # 2. Fetch last 10 rated contests
        contest_history = await fetch_json(f"{BASE_URL}user.rating?handle={quote(username)}")
        if not contest_history:
            return {"error": "User has no rated contest history."}
        
        last_10_contests = contest_history[-10:]
        contest_ids = [c["contestId"] for c in last_10_contests]

        # 3. Fetch solved problems (check which ones the user got AC on)
        submissions = await fetch_json(f"{BASE_URL}user.status?handle={quote(username)}&count=1000")
        solved_set = set()
        for sub in submissions:
            if sub["verdict"] == "OK" and "contestId" in sub["problem"] and "index" in sub["problem"]:
                prob_id = f"{sub['problem']['contestId']}{sub['problem']['index']}"
                solved_set.add(prob_id)

        # 4. Fetch full problem set to get metadata (rating, name, tags)
        all_problems = await fetch_all_problems()
        # Map it to {contestId}{index} for fast lookup
        problem_map = {f"{p['contestId']}{p['index']}": p for p in all_problems if "contestId" in p and "index" in p}

        # 5. Filter logic
        suggestions = []

        for contest in last_10_contests:
            cid = contest["contestId"]
            contest_name = contest["contestName"]
            
            # Find all problems that exist in this contest ID
            contest_problems = [p for pid, p in problem_map.items() if p["contestId"] == cid]
            
            unsolved_in_contest = []
            for p in contest_problems:
                p_id = f"{p['contestId']}{p['index']}"
                if p_id not in solved_set:
                    p_rating = p.get("rating")
                    
                    # Condition 1: Unrated problem? Give it.
                    # Condition 2: Rated and within +/- 300 of current rating? Give it.
                    if p_rating is None or abs(p_rating - rating) <= 300:
                        unsolved_in_contest.append(p)
            
            # Max 2 problems per contest
            for p in unsolved_in_contest[:2]:
                suggestions.append({
                    "contest_name": contest_name,
                    "problem": p,
                    "reason": "Unrated problem" if p.get("rating") is None else f"Within +/- 300 of your rating ({rating})"
                })

        return {"status": "ok", "rating": rating, "suggestions": suggestions}

    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}