import os
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# --- TOOLS ---

def search_web(query: str) -> str:
    """Search the web and return text from the first result."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        snippets = soup.find_all("div", class_="BNeawe")
        results = " ".join([s.get_text() for s in snippets[:5]])
        return results if results else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

def fetch_url(url: str) -> str:
    """Fetch the text content of a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]
    except Exception as e:
        return f"Failed to fetch URL: {str(e)}"

# --- TOOL DEFINITIONS FOR CLAUDE ---

tools = [
    {
        "name": "search_web",
        "description": "Search the web for information about a company or topic. Use this to research the company from the job description.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch the content of a specific URL. Use this to read a company website or job posting.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch"
                }
            },
            "required": ["url"]
        }
    }
]

# --- AGENT LOOP ---

def run_agent(job_description: str, resume: str):
    print("\n🤖 Agent starting...\n")

    messages = [
        {
            "role": "user",
            "content": f"""You are a job application assistant. Your goal is to write a tailored cover letter.

Here is the job description:
{job_description}

Here is the candidate's resume:
{resume}

Instructions:
1. First search the web to research the company
2. Use what you learn about the company + the job description + the resume to write a tailored cover letter
3. The cover letter should be professional, specific, and under 300 words
4. After writing the cover letter, also list 3 likely interview questions for this role

Use your tools to research first, then write the cover letter."""
        }
    ]

    # Agent loop — keeps running until Claude stops using tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        print(f"Claude: {response.stop_reason}")

        # If Claude is done, print final response and exit
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print("\n--- FINAL OUTPUT ---\n")
                    print(block.text)
            break

        # If Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"🔧 Using tool: {block.name} with input: {block.input}")

                    # Run the tool
                    if block.name == "search_web":
                        result = search_web(block.input["query"])
                    elif block.name == "fetch_url":
                        result = fetch_url(block.input["url"])
                    else:
                        result = "Unknown tool"

                    print(f"✅ Tool result: {result[:100]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add tool results back to messages
            messages.append({"role": "user", "content": tool_results})

# --- RUN ---

if __name__ == "__main__":
    job_description = input("Paste the job description (press Enter twice when done):\n")

    resume = """
    Jun Han — CS Student at Toronto Metropolitan University, graduating May 2026
    GPA: 3.58

    Projects:
    - AI Interview Coach: Built with React, TypeScript, Claude API. Mock interview app with structured feedback.
    - VulnScan: Multi-page AI security scanner with attack simulation playground. React, TypeScript, Claude API.
    - Liturgy App: Full stack REST API with Quarkus, MongoDB, React, TypeScript.

    Experience:
    - Co-Founder, Roblox Game Development Studio (2025-Present)
    - Construction Helper, Shinkarev Construction (2018-2019)

    Skills: React, TypeScript, JavaScript, Python, Java, REST APIs, Git, Claude API
    """

    run_agent(job_description, resume)