import httpx
from urllib.parse import quote
from .get_problemlist import get_filtered_problems

BASE_URL = "https://codeforces.com/api/"

# Only analyze these core topics. This prevents recommending obscure niche tags.
CORE_TOPICS = [
    'implementation', 'math', 'greedy', 'dp', 'data structures', 
    'graphs', 'constructive algorithms', 'binary search', 'strings', 
    'sortings', 'two pointers', 'brute force', 'dfs and similar', 
    'number theory', 'combinatorics'
]

async def fetch_json(url: str):
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError(f"Codeforces API Error: {data.get('comment', 'Unknown error')}")
        return data["result"]

async def get_practice_plan(username: str):
    try:
        # 1. Fetch current rating
        user_info = await fetch_json(f"{BASE_URL}user.info?handles={quote(username)}")
        rating = user_info[0].get("rating", 800)
        if rating < 800: rating = 800

        # 2. Fetch submissions to analyze solved tags
        submissions = await fetch_json(f"{BASE_URL}user.status?handle={quote(username)}&count=1000")
        solved_tags = {}
        solved_problems = set()

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
                    # Only count it if it's in our core topics list
                    if tag in CORE_TOPICS:
                        solved_tags[tag] = solved_tags.get(tag, 0) + 1

        # 3. Identify weak core topics (the ones they solved the LEAST of)
        core_counts = {topic: solved_tags.get(topic, 0) for topic in CORE_TOPICS}
        sorted_core = sorted(core_counts.items(), key=lambda x: x[1])
        
        # Pick the 3 least-solved topics from the core list
        weak_topics = [tag for tag, count in sorted_core[:3]]

        # Fallback if for some reason they solved nothing in the core list
        if not weak_topics:
            weak_topics = ["implementation", "math", "greedy"]

        # 4. Define target rating range (Current to Current + 300)
        min_r = rating
        max_r = rating + 300

        # 5. Fetch up to 3 problems specifically in those weak core topics
        problems = await get_filtered_problems(
            min_rating=min_r,
            max_rating=max_r,
            topics=weak_topics,
            sort_by="recent",
            match_type="OR"
        )

        # 6. Fallback: If < 3 problems found, remove the topic constraint entirely
        # Just give them general problems in their rating range instead of failing.
        if len(problems) < 3:
            problems = await get_filtered_problems(
                min_rating=min_r,
                max_rating=max_r,
                topics=None, # No topic filter
                sort_by="recent"
            )

        return {
            "status": "ok",
            "rating": rating,
            "weak_topics": weak_topics,
            "problems": problems[:3]
        }

    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}