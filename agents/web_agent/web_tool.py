import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool

# Load API key
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=TAVILY_API_KEY)

# 🔍 Enhance prompt with SDoH context
SDOH_CONTEXT = (
    "Social Determinants of Health (SDoH) include topics like: "
    "stress, income inequality, education, housing, food access, healthcare access, public health policies, "
    "mental health, environmental conditions, and community-based health programs."
)

@tool
def web_search(query: str) -> str:
    """
    Retrieves real-time information on Social Determinants of Health (SDoH) such as policies, programs,
    news, and interventions. Complements insights from Snowflake and RAG agents.
    """
    print(f"🌐 [Web Search Tool] Searching for: {query}")

    try:
        # 🧠 Expand query to emphasize SDoH domain
        enhanced_query = f"{query} (related to Social Determinants of Health, stress, income, education, public health)"

        response = client.search(
            query=enhanced_query,
            search_depth="advanced",
            max_results=10
        )
        sources = response.get("results", [])

        if not sources:
            return "❌ No relevant SDoH content found."

        summary = "\n\n".join(
            f"🔹 **{item.get('title')}**\n{item.get('content')}\n🔗 {item.get('url')}"
            for item in sources
        )
        return f"**🌍 Web Search Results on SDoH for:** `{query}`\n\n{summary}"

    except Exception as e:
        print("❌ Web search error:", e)
        return "❌ Web search failed due to an internal error."
