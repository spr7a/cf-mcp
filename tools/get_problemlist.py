import httpx
from urllib.parse import quote

BASE_URL = "https://codeforces.com/api/"

async def fetch_all_problems():
    """Fetch the entire Codeforces problemset."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{BASE_URL}problemset.problems")
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError("Failed to fetch problemset from Codeforces API.")
        return data["result"]["problems"]

async def get_filtered_problems(
    min_rating: int = None,
    max_rating: int = None,
    topics: list = None,
    sort_by: str = "recent",
    match_type: str = "OR"
):
    """
    Fetches, filters, and sorts problems from Codeforces.
    """
    try:
        raw_problems = await fetch_all_problems()
        filtered = []

        # Default topics to empty list
        if topics is None:
            topics = []
        # Sanitize topics to lowercase for case-insensitive matching
        topics = [t.lower() for t in topics]

        for p in raw_problems:
            # 1. Rating filter
            r = p.get('rating')
            if min_rating is not None and (r is None or r < min_rating):
                continue
            if max_rating is not None and (r is None or r > max_rating):
                continue

            # 2. Topics filter
            tags = [t.lower() for t in p.get('tags', [])]
            if topics:
                if match_type.upper() == "AND":
                    if not all(t in tags for t in topics):
                        continue
                else: # Default to OR
                    if not any(t in tags for t in topics):
                        continue

            # 3. URL validation (need both contestId and index)
            if 'contestId' not in p or 'index' not in p:
                continue

            filtered.append(p)

        # 4. Sorting (recent = highest contestId, oldest = lowest contestId)
        if not filtered:
            return []

        if sort_by.lower() == "oldest":
            filtered.sort(key=lambda x: x['contestId'])
        else: # Default to "recent"
            filtered.sort(key=lambda x: x['contestId'], reverse=True)

        # 5. Return max 10 problems
        return filtered[:10]

    except Exception as e:
        raise ValueError(f"Error filtering problems: {str(e)}")