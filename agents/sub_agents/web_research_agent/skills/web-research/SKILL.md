---
name: web-research
description: Research the web using Google Search and URL content analysis. Use when the user asks about recent events, current information, needs to find sources online, or wants detailed analysis of specific web pages.
metadata:
  adk_additional_tools:
    - google_search_agent
    - url_context_agent
---

# Web Research

This skill enables comprehensive web research by combining Google Search with deep URL content analysis. Use it to find current information and analyze specific web pages in detail.

## Architecture

This skill uses a sub-agent architecture with two specialized agents:

### 1. `google_search_agent`
A specialized agent that uses Google Search to find information.
- Returns relevant URLs with brief descriptions
- Provides relevance scores for each result
- Suggests URLs for detailed analysis

### 2. `url_context_agent`
A specialized agent that analyzes URL content.
- Retrieves complete content from the URL
- Analyzes thoroughly for relevant information
- Extracts actionable insights

Both agents are accessible as tools through the main web_research_agent, which delegates to the appropriate sub-agent based on the research needs.

## Workflows

### Workflow 1: Search and Analyze

For general research questions:

1. **Search**: Delegate to `google_search_agent` to find relevant sources
2. **Review**: Analyze search results for relevance
3. **Deep Dive**: Delegate to `url_context_agent` on the most promising URLs
4. **Synthesize**: Combine findings into a comprehensive response

Example:
```
User: "What are the latest developments in AI regulation?"
-> google_search_agent searches for "AI regulation latest developments 2024"
-> Review top 3 results
-> url_context_agent analyzes the most relevant article
-> Synthesize findings
```

### Workflow 2: Direct URL Analysis

When the user provides a URL:

1. **Fetch**: Delegate to `url_context_agent` to retrieve and analyze the URL
2. **Extract**: Identify key information, insights, and warnings
3. **Relate**: Connect findings back to the user's query

Example:
```
User: "What does this article say: https://example.com/ai-news"
-> url_context_agent analyzes "https://example.com/ai-news"
-> Summarize key points
-> Provide actionable insights
```

## Output Format

For search results:
1. Relevant URLs found
2. Brief description of what each result contains
3. Relevance to the original query
4. Suggestions for which URLs to analyze deeply

For URL analysis:
1. Summary of what the content provides
2. How the content relates to the original query
3. Actionable insights and recommendations
4. Any warnings or important considerations

## When to Use

- User asks about recent events or current information
- Topic requires up-to-date data (news, prices, releases)
- User provides a URL and wants to understand its content
- Need to extract detailed information from a web page
- Following up on search results with deeper analysis
