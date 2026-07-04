import asyncio
from fastmcp import FastMCP

# Import your tool logic from the 'tools' package
from tools.get_user import fetch_and_parse_user_data
from tools.compare_user import compare_users_data
from tools.get_problemlist import get_filtered_problems
from tools.get_problem import get_problem_details
from tools.get_practice import get_practice_plan
from tools.get_random_problem import get_random_problem_suggestion
from tools.get_upsolve import get_upsolve_suggestions

# Initialize the MCP Server
mcp = FastMCP("Codeforces Universal Tool")

# ==========================================
# TOOL 1: Get Single User Profile
# ==========================================
@mcp.tool()
async def get_user(username: str) -> str:
    """
    Fetches a complete Codeforces profile in one call, returning:
    - Current rating, max rating, title, and max title.
    - Number of total contests given.
    - Recent 5 contest rating changes (delta).
    - Total distinct problems solved.
    - Breakdown of solved problems by difficulty.
    - Top 10 problem categories solved.
    """
    data = await fetch_and_parse_user_data(username)

    if data["status"] == "error":
        return f"❌ Error fetching user: {data['message']}"

    output = f"**🧑‍💻 User Profile: {username}**\n\n"
    
    output += f"**🏆 Ratings & Titles:**\n"
    output += f"- Current Rating: **{data['rating']}**\n"
    output += f"- Max Rating: **{data['max_rating']}**\n"
    output += f"- Current Title: {data['title']}\n"
    output += f"- Max Title: {data['max_title']}\n\n"

    output += f"**🏁 Contest History:**\n"
    output += f"- Total Rated Contests Given: **{data['total_contests']}**\n"
    
    if data['recent_5']:
        output += "- **Last 5 Rating Changes:**\n"
        for c in data['recent_5']:
            sign = "+" if c['newRating'] > c['oldRating'] else ""
            output += f"  - {c['contestName']}: Rank {c['rank']} ({sign}{c['newRating'] - c['oldRating']}, {c['oldRating']} ➜ {c['newRating']})\n"
    else:
        output += "- No rated contests found.\n"
    output += "\n"

    output += f"**✅ Problem Solving Stats:**\n"
    output += f"- Total Distinct Problems Solved: **{data['total_solved']}**\n"

    if data['difficulty_stats']:
        output += "- **Solved by Difficulty:**\n"
        sorted_diff = sorted(data['difficulty_stats'].items(), key=lambda x: int(x[0]) if x[0] != 'Unrated' else 0)
        for diff, count in sorted_diff:
            output += f"  - Rating {diff}: {count} problems\n"
    else:
        output += "- No solved problems found by difficulty.\n"

    if data['top_10_categories']:
        output += "- **Top 10 Categories:**\n"
        for tag, count in data['top_10_categories']:
            output += f"  - {tag}: {count} problems\n"
    else:
        output += "- No categories found.\n"

    return output

# ==========================================
# TOOL 2: Compare Two Users
# ==========================================
@mcp.tool()
async def compare_user(user_a: str, user_b: str) -> str:
    """
    Compare two Codeforces users side-by-side. 
    Returns a detailed comparison of ratings, titles, contest count, 
    and problem solving breakdown (difficulty & category).
    """
    return await compare_users_data(user_a, user_b)

# ==========================================
# TOOL 3: Search Problem List
# ==========================================
@mcp.tool()
async def get_problemlist(
    min_rating: int = None,
    max_rating: int = None,
    topics: list = None,
    sort_by: str = "recent",
    match_type: str = "OR"
) -> str:
    """
    Search the entire Codeforces problemset and return up to 10 problems.
    
    Parameters:
    - min_rating: Minimum difficulty rating (e.g., 800)
    - max_rating: Maximum difficulty rating (e.g., 2400)
    - topics: List of tags to filter by (e.g., ["dp", "greedy"])
    - sort_by: "recent" (newest first) or "oldest" (oldest first)
    - match_type: "OR" (match any topic) or "AND" (must match ALL topics)
    
    Returns 10 problems with names, ratings, tags, and direct links.
    """
    try:
        problems = await get_filtered_problems(
            min_rating=min_rating,
            max_rating=max_rating,
            topics=topics,
            sort_by=sort_by,
            match_type=match_type
        )
        
        if not problems:
            return "No problems found matching your criteria. Try broadening your filters."

        output = f"**💻 Found {len(problems)} Problems:**\n\n"
        
        for p in problems:
            name = p.get('name', 'Unknown Problem')
            contest_id = p['contestId']
            index = p['index']
            rating = p.get('rating', 'Unrated')
            tags = ", ".join(p.get('tags', [])[:5])
            url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
            
            output += f"### [{name}]({url})\n"
            output += f"- **Rating**: {rating}\n"
            output += f"- **Tags**: {tags}\n\n"
            
        return output
        
    except Exception as e:
        return f"❌ Error fetching problem list: {str(e)}"

# ==========================================
# TOOL 4: Get Full Problem Statement
# ==========================================
@mcp.tool()
async def get_problem(contest_id: int, index: str) -> str:
    """
    Fetch the full problem statement, rating, and topics for a specific Codeforces problem.
    Provide the contest ID and the problem index (e.g., contest_id=4, index='A').
    """
    try:
        data = await get_problem_details(contest_id, index)
        
        if "error" in data:
            return f"❌ {data['error']}"
        
        output = f"# {data['title']}\n\n"
        output += f"**Link:** [View on Codeforces]({data['url']})\n\n"
        
        # The dropdown you requested!
        output += f"📊 **Rating:** `{data['rating']}`  |  **Topics:** `{', '.join(data['topics'])}`\n\n"
        output += f"---\n\n"
           
        output += "---\n\n"
        output += "**Problem Statement:**\n\n"
        output += data['statement']
        
        return output
    except Exception as e:
        return f"❌ Error fetching problem: {str(e)}"
# --- TOOL 5: Get Practice Problems ---
@mcp.tool()
async def get_practiceproblems(username: str) -> str:
    """
    Analyzes a user's solved problems to identify their weakest topics.
    Recommends up to 3 practice problems within +300 rating of their current level.
    """
    result = await get_practice_plan(username)
    
    if result["status"] == "error":
        return f"❌ Error generating practice plan: {result['message']}"

    output = f"**🎯 Practice Plan for `{username}`**\n\n"
    output += f"Current Rating: **{result['rating']}**\n"
    output += f"Identified Weak Topic(s): **{', '.join(result['weak_topics'])}**\n"
    output += f"Target Rating Range: **{result['rating']} - {result['rating'] + 300}**\n\n"

    if not result["problems"]:
        output += "No suitable practice problems found in the target rating range. Try increasing your range or broadening topics."
        return output

    output += "**💻 Recommended Problems to Practice:**\n"
    for idx, p in enumerate(result["problems"], 1):
        name = p.get('name', 'Unknown Problem')
        contest_id = p['contestId']
        index = p['index']
        rating = p.get('rating', 'Unrated')
        tags = ", ".join(p.get('tags', [])[:5])
        url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        
        output += f"\n**{idx}. [{name}]({url})**\n"
        output += f"   - Rating: {rating}\n"
        output += f"   - Topics: {tags}\n"
        
    return output
# --- TOOL 7: Get Random Practice Problem ---
@mcp.tool()
async def get_random_practice(username: str) -> str:
    """
    Ignore weaknesses and recommend a single, completely random Codeforces problem 
    within +/- 300 rating of the user's current rating. 
    Great for a fresh, challenging surprise!
    """
    result = await get_random_problem_suggestion(username)
    
    if "error" in result:
        return f"❌ Error generating random problem: {result['error']}"

    p = result
    name = p.get('name', 'Unknown Problem')
    contest_id = p['contestId']
    index = p['index']
    rating = p.get('rating', 'Unrated')
    tags = ", ".join(p.get('tags', [])[:5])
    url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
    
    output = f"**🎲 Random Practice Problem for `{username}`**\n\n"
    output += f"**[{name}]({url})**\n"
    output += f"- **Rating**: {rating}\n"
    output += f"- **Tags**: {tags}\n"
    output += f"- *(Generated from range: Current Rating ± 300)*\n"
    
    return output
# --- TOOL 8: Get Upsolve Problems ---
@mcp.tool()
async def get_upsolve(username: str) -> str:
    """
    Analyze the user's last 10 rated Codeforces contests.
    Recommends up to 2 unsolved problems per contest if:
    - The problem is unrated, OR
    - The problem is rated within +/- 300 of the user's current rating.
    This is perfect for targeted practice to improve rank!
    """
    result = await get_upsolve_suggestions(username)
    
    if result["status"] == "error":
        return f"❌ Error generating upsolve list: {result['message']}"

    if not result["suggestions"]:
        return f"🎉 No upsolve problems found for `{username}` within +/- 300 of {result['rating']} rating. Either you solved them all, or they are out of your range!"

    output = f"**📝 Upsolve Plan for `{username}`**\n"
    output += f"(Based on last 10 rated contests. Current Rating: **{result['rating']}**)\n\n"

    for item in result["suggestions"]:
        p = item["problem"]
        name = p.get('name', 'Unknown')
        contest_id = p['contestId']
        index = p['index']
        rating = p.get('rating', 'Unrated')
        tags = ", ".join(p.get('tags', [])[:3]) # Show top 3 tags
        url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        
        output += f"### [{name}]({url})\n"
        output += f"- **Contest:** {item['contest_name']}\n"
        output += f"- **Rating:** {rating}\n"
        output += f"- **Tags:** {tags}\n"
        output += f"- **Why upsolve?** *{item['reason']}*\n\n"

    return output
# ==========================================
# RUN THE SERVER
# ==========================================
if __name__ == "__main__":
    mcp.run(transport="stdio")