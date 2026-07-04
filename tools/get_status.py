import httpx
from urllib.parse import quote

BASE_URL = "https://codeforces.com/api/"

# Map Codeforces verdicts to readable emojis
VERDICT_EMOJIS = {
    "OK": "✅ ACCEPTED",
    "WRONG_ANSWER": "❌ Wrong Answer",
    "TIME_LIMIT_EXCEEDED": "⏱️ TLE",
    "MEMORY_LIMIT_EXCEEDED": "💾 MLE",
    "RUNTIME_ERROR": "💥 RE",
    "COMPILATION_ERROR": "🛠️ CE",
    "SKIPPED": "⏭️ Skipped",
    "CHALLENGED": "⚔️ Hacked",
    "IDLENESS_LIMIT_EXCEEDED": "💤 Idle",
}

async def fetch_json(url: str):
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError(f"Codeforces API Error: {data.get('comment', 'Unknown error')}")
        return data["result"]

async def get_user_submission_status(username: str):
    try:
        submissions = await fetch_json(f"{BASE_URL}user.status?handle={quote(username)}&count=1000")
        
        if not submissions:
            return {"error": "No submissions found for this user."}

        # 1. Calculate summary statistics
        total = len(submissions)
        verdict_counts = {}
        last_20 = submissions[:20] # Get the 20 most recent

        for sub in submissions:
            v = sub.get("verdict", "UNKNOWN")
            verdict_counts[v] = verdict_counts.get(v, 0) + 1

        # Format the summary for the top of the output
        summary = f"**Total Submissions analyzed:** {total}\n"
        for verdict, count in verdict_counts.items():
            emoji = VERDICT_EMOJIS.get(verdict, "📄")
            summary += f"- {emoji}: {count}\n"

        # 2. Format the most recent 20 submissions
        recent_list = []
        for sub in last_20:
            prob = sub.get("problem", {})
            prob_name = prob.get("name", "Unknown")
            prob_id = f"{prob.get('contestId', '?')}{prob.get('index', '?')}"
            
            verdict = sub.get("verdict", "PENDING")
            display_verdict = VERDICT_EMOJIS.get(verdict, f"📄 {verdict}")
            
            # If still pending, show a spinning clock
            if verdict == "TESTING":
                display_verdict = "⌛ Testing..."

            time_consumed = sub.get("timeConsumedMillis", 0)
            memory_consumed = sub.get("memoryConsumedBytes", 0) // 1024 # Convert to KB

            submission_id = sub.get("id")
            url = f"https://codeforces.com/contest/{prob.get('contestId', '?')}/submission/{submission_id}" if prob.get('contestId') else "N/A"

            recent_list.append({
                "prob_name": f"{prob_id} - {prob_name}",
                "verdict": display_verdict,
                "time": f"{time_consumed} ms",
                "memory": f"{memory_consumed} KB",
                "url": url
            })

        return {
            "status": "ok",
            "summary": summary,
            "recent_submissions": recent_list
        }

    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}