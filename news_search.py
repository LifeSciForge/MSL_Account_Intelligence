# news_search.py
# ===============
# Searches the web for latest news about a hospital
# Uses Tavily API — designed specifically for AI applications
# Finds recent news, press releases, and developments
# Requires TAVILY_API_KEY in .env file

import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load API key from .env file
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

def search_hospital_news(hospital_name, state=None):
    """
    Search for latest news about a hospital.
    
    Args:
        hospital_name: Name of the hospital e.g. 'Mayo Clinic'
        state: Optional US state e.g. 'Minnesota'
    
    Returns:
        List of news article dictionaries
    """
    
    if not TAVILY_API_KEY:
        print("No Tavily API key found — check your .env file")
        return []
    
    print(f"Searching news for: {hospital_name}")
    
    # Build search query
    query = f"{hospital_name} hospital latest news research clinical trials"
    if state:
        query += f" {state}"
    
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=True
        )
        
        articles = []
        for result in response.get("results", []):
            article = {
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:300],
                "score": result.get("score", 0)
            }
            articles.append(article)
        
        print(f"Found {len(articles)} news articles")
        return articles
        
    except Exception as e:
        print(f"Error searching news: {e}")
        return []


def search_doctor_news(doctor_name, hospital_name):
    """
    Search for news and pharma relationships for a specific doctor.
    
    Args:
        doctor_name: Full name of the doctor
        hospital_name: Hospital they work at
    
    Returns:
        List of relevant articles
    """
    
    if not TAVILY_API_KEY:
        print("No Tavily API key found — check your .env file")
        return []
    
    print(f"Searching news for doctor: {doctor_name}")
    
    query = f"{doctor_name} {hospital_name} pharma research publications clinical trials"
    
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=3
        )
        
        articles = []
        for result in response.get("results", []):
            article = {
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:300],
                "score": result.get("score", 0)
            }
            articles.append(article)
        
        print(f"Found {len(articles)} articles for {doctor_name}")
        return articles
        
    except Exception as e:
        print(f"Error searching doctor news: {e}")
        return []


def format_news_for_llm(articles, source_name):
    """
    Format news articles as clean text for Claude input.
    
    Args:
        articles: List of article dictionaries
        source_name: Hospital or doctor name for context
    
    Returns:
        Formatted string ready for Claude
    """
    
    if not articles:
        return f"No recent news found for {source_name}."
    
    lines = [f"Recent news and developments for {source_name}:"]
    
    for i, article in enumerate(articles, 1):
        lines.append(f"\n{i}. {article['title']}")
        lines.append(f"   {article['content']}")
        lines.append(f"   Source: {article['url']}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    # Test hospital news search
    articles = search_hospital_news("Mayo Clinic", "Minnesota")
    
    if articles:
        print(f"\nFirst article:")
        print(f"Title: {articles[0]['title']}")
        print(f"Preview: {articles[0]['content'][:150]}")
        print(f"URL: {articles[0]['url']}")
    else:
        print("No articles found")