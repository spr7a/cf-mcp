# Codeforces MCP Server

A **Model Context Protocol (MCP)** server that provides a comprehensive set of tools for interacting with the [Codeforces](https://codeforces.com/) competitive programming platform. Built with [FastMCP](https://github.com/jlowin/fastmcp) and Python.

This server exposes tools that can be used by any MCP-compatible client (e.g., Claude Desktop, Cline, etc.) to fetch user profiles, compare users, search problems, generate practice plans, and more.

---

## Features

| Tool | Description |
|------|-------------|
| **`get_user`** | Fetch a complete Codeforces profile — rating, titles, contest history, solved problems breakdown by difficulty & category. |
| **`compare_user`** | Side-by-side comparison of two Codeforces users across ratings, contests, solved problems, and categories. |
| **`get_problemlist`** | Search the Codeforces problemset with filters (rating range, tags, sort order, match type). Returns up to 10 problems. |
| **`get_problem`** | Fetch the full problem statement, rating, and tags for a specific problem by contest ID and index. |
| **`get_practiceproblems`** | Analyze a user's solved problems to identify their weakest topics and recommend up to 3 practice problems within +300 rating. |
| **`get_random_practice`** | Recommend a single random Codeforces problem within ±300 rating of the user's current level. |
| **`get_upsolve`** | Analyze the user's last 10 rated contests and recommend unsolved problems within ±300 rating for targeted improvement. |
| **`get_status`** | Fetch the last 1000 submissions of a user — AC/WA/TLE summary and details of the 20 most recent submissions. |

---

## Installation

### Prerequisites

- Python 3.10+
- `pip` (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/spr7a/cf-mcp.git
cd cf-mcp

# Install dependencies
pip install fastmcp httpx
```

---

## Usage

### Running the Server

```bash
python test.py
```

The server runs on **stdio transport** by default, making it compatible with MCP clients.

### Configuring with Claude Desktop / Cline

Add the following to your MCP settings configuration file (e.g., `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "codeforces": {
      "command": "python",
      "args": ["/path/to/cf-mcp/test.py"]
    }
  }
}
```

### Example Queries

Once connected, you can ask your MCP client questions like:

- *"What is tourist's Codeforces profile?"*
- *"Compare tourist and petr side by side."*
- *"Find me DP problems rated 1600-1800."*
- *"Get the full statement for problem 4A."*
- *"Generate a practice plan for reikc."*
- *"Give me a random problem for reikc."*
- *"What unsolved problems does reikc have from recent contests?"*
- *"What did reikc solve recently?"*

---

## Project Structure

```
cf-mcp/
├── test.py                  # Main MCP server entry point (FastMCP)
├── tools/
│   ├── get_user.py          # Fetch & parse user profile data
│   ├── compare_user.py      # Compare two users side-by-side
│   ├── get_problemlist.py   # Search problemset with filters
│   ├── get_problem.py       # Fetch full problem statement
│   ├── get_practice.py      # Generate practice plan from weak topics
│   ├── get_random_problem.py# Random problem suggestion
│   ├── get_upsolve.py       # Upsolve recommendations from recent contests
│   ├── get_status.py        # Submission status & history
│   └── problems.py          # Shared problem-fetching utilities
└── README.md
```

---

## How It Works

The entire tool suite is powered by the official Codeforces API, which acts as the backbone for all data operations. To ensure lightning-fast performance, the server uses Python's httpx library to issue asynchronous, non-blocking network calls, allowing multiple requests to run in parallel instead of waiting for each one sequentially.

---

## Dependencies

- [fastmcp](https://pypi.org/project/fastmcp/) — MCP server framework
- [httpx](https://pypi.org/project/httpx/) — Async HTTP client

---

## License

MIT