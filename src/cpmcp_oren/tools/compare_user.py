import asyncio
from .get_user import fetch_and_parse_user_data

async def compare_users_data(user_a: str, user_b: str):
    # Fetch both concurrently
    data_a, data_b = await asyncio.gather(
        fetch_and_parse_user_data(user_a),
        fetch_and_parse_user_data(user_b)
    )

    if data_a["status"] == "error":
        return f"❌ Error fetching user '{user_a}': {data_a['message']}"
    if data_b["status"] == "error":
        return f"❌ Error fetching user '{user_b}': {data_b['message']}"

    # Helper to format deltas
    def format_delta(old, new):
        d = new - old
        sign = "+" if d > 0 else ""
        return f"{sign}{d}"

    output = f"**👥 Comparison: `{user_a}` vs `{user_b}`**\n\n"

    # 1. Ratings & Titles
    output += "**🏆 Ratings & Titles**\n"
    output += f"| Metric | **{user_a}** | **{user_b}** |\n"
    output += f"| :--- | :---: | :---: |\n"
    output += f"| Current Rating | **{data_a['rating']}** | **{data_b['rating']}** |\n"
    output += f"| Max Rating | **{data_a['max_rating']}** | **{data_b['max_rating']}** |\n"
    output += f"| Current Title | {data_a['title']} | {data_b['title']} |\n"
    output += f"| Max Title | {data_a['max_title']} | {data_b['max_title']} |\n\n"

    # 2. Contests & Problems
    output += "**📊 Statistics**\n"
    output += f"| Metric | **{user_a}** | **{user_b}** |\n"
    output += f"| :--- | :---: | :---: |\n"
    output += f"| Total Contests | **{data_a['total_contests']}** | **{data_b['total_contests']}** |\n"
    output += f"| Problems Solved | **{data_a['total_solved']}** | **{data_b['total_solved']}** |\n\n"

    # 3. Last 5 Contests
    output += "**🔄 Last 5 Rating Changes**\n"
    output += f"**{user_a}**:\n"
    for c in data_a['recent_5']:
        d = c['newRating'] - c['oldRating']
        sign = "+" if d > 0 else ""
        output += f"- {c['contestName']}: Rank {c['rank']} ({sign}{d})\n"
    output += f"\n**{user_b}**:\n"
    for c in data_b['recent_5']:
        d = c['newRating'] - c['oldRating']
        sign = "+" if d > 0 else ""
        output += f"- {c['contestName']}: Rank {c['rank']} ({sign}{d})\n"
    output += "\n"

    # 4. Difficulty Stats (Side by Side)
    output += "**📈 Difficulty Breakdown**\n"
    output += f"| Rating | **{user_a}** | **{user_b}** |\n"
    output += f"| :--- | :---: | :---: |\n"
    all_diffs = set(data_a['difficulty_stats'].keys()) | set(data_b['difficulty_stats'].keys())
    sorted_diffs = sorted(all_diffs, key=lambda x: int(x) if x != 'Unrated' else 0)
    for diff in sorted_diffs:
        a_count = data_a['difficulty_stats'].get(diff, 0)
        b_count = data_b['difficulty_stats'].get(diff, 0)
        if a_count > 0 or b_count > 0:
            output += f"| {diff} | {a_count} | {b_count} |\n"

    # 5. Top 10 Categories (Side by Side)
    output += "\n**📚 Top Categories**\n"
    # Merge top categories from both users
    cat_map_a = dict(data_a['top_10_categories'])
    cat_map_b = dict(data_b['top_10_categories'])
    all_cats = set(cat_map_a.keys()) | set(cat_map_b.keys())
    sorted_cats = sorted(all_cats)
    if all_cats:
        output += f"| Category | **{user_a}** | **{user_b}** |\n"
        output += f"| :--- | :---: | :---: |\n"
        for cat in sorted_cats:
            a_count = cat_map_a.get(cat, 0)
            b_count = cat_map_b.get(cat, 0)
            if a_count > 0 or b_count > 0:
                output += f"| {cat} | {a_count} | {b_count} |\n"

    return output