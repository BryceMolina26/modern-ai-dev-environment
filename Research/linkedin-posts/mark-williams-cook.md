# Mark Williams-Cook

## Source Type
LinkedIn / AlsoAsked / Candour / YouTube (Search and AI with MWC)

## Source Link
https://www.linkedin.com/in/markwilliamscook/

## Date Reviewed
2026-06-14

## Why This Expert Was Selected
Mark Williams-Cook is Director at Candour SEO agency and founder of AlsoAsked, the largest People Also Ask intent research tool (100,000+ registered users including TripAdvisor, Lego, and IKEA). With 20+ years in SEO, he combines deep technical understanding of how LLMs ground queries with practical intent-mapping workflows. His 2026 work focuses on distinguishing grounded vs. non-grounded queries, generating synthetic prompt libraries from ICPs, and treating AI visibility as a multi-site problem—not just a ranking problem.

## Key Ideas Collected

1. **Determine whether queries need grounding before investing.** When users query ChatGPT or Google AI Mode, the model first decides if the answer requires live web retrieval. "Solved knowledge" queries (e.g., "What do red blood cells do?") draw from training data and are nearly impossible to shift quickly. Time-sensitive or consensus-lacking queries trigger grounding—web searches that can be influenced within days. Teams wasting effort on non-grounded queries miss the actionable subset where content and PR can change AI answers.

2. **Predict grounding probability at scale.** Mark identifies practical methods to score grounding likelihood: inspect ChatGPT's `search_prob` field in developer console (threshold ~0.65 on free tier), use Google's Gemini grounding API (~$0.03 per query), or apply Dan Petrovic's public ML models that classify keyword lists as grounded or not. Filtering 500 related queries down to the ~300 that will actually trigger web search saves massive resources.

3. **Generate prompt libraries from ICPs, not Google keywords.** AI search is conversational—users ask multi-aspect questions across long sessions. Mark uses the ChatGPT API with ideal customer profile descriptions plus seed keywords to generate realistic prompts (e.g., a vegan, health-conscious runner asking about cruelty-free shoes). AlsoAsked's PAA data then maps intent-proximity follow-up questions. One hundred traditional keywords can expand to 3,000–4,000 prompts, which are then filtered through grounding prediction.

4. **Target the background searches AI performs, not just final prompts.** Grounded queries trigger consistent web searches on Google or Bing—often 3–4 key phrases per prompt. The goal is presence across the results AI summarizes (typically scanning 10–20 sources), not just ranking #1 for a single keyword. This shifts strategy toward multi-site visibility: review sites, blogs, forums, and PR placements where AI gathers evidence.

5. **Treat AI search as a multi-site brand presence problem.** Even for traditional SEO practitioners, AI visibility requires getting your brand, products, and services discussed across the results AI reads—with positive sentiment. AlsoAsked's PAA data bridges classic intent research and AI query fan-out. Mark remains skeptical of prompt-tracking vanity metrics and emphasizes understanding pre-training vs. post-training effects on how base models perceive brands.

## Relevance to AI-Powered SEO Content Production

Mark Williams-Cook connects AI content production to intent architecture. Before generating articles at scale, his workflow identifies which conversational prompts will actually be grounded, what follow-up questions users ask (via PAA proximity), and which background SERPs need coverage. This prevents AI content teams from publishing into query spaces they cannot influence. AlsoAsked integrates directly into research pipelines—including an MCP server for Claude—making his approach operational for AI-assisted content planning, brief generation, and coverage-gap analysis.

## Practical Takeaways

- Classify target queries as grounded vs. non-grounded before building content plans.
- Use ICP-driven prompt generation, not traditional keyword research, for AI search planning.
- Map PAA follow-up chains to anticipate conversational query sequences.
- Identify the 3–4 background web searches AI performs for each grounded prompt.
- Pursue presence across review sites, blogs, and forums—not just your own domain.
- Monitor sentiment and brand mentions across results AI aggregates.
- Use grounding APIs or community ML tools to filter large keyword lists efficiently.
- Validate long-form content structure with AI assistants against intent proximity patterns.

## Notes

Pragmatic, anti-hype stance—openly skeptical of prompt-tracking tools while offering concrete technical methods. AlsoAsked's growth correlates with AI search adoption, validating PAA data as the bridge between classic SEO and query fan-out. Primary sources include [Majestic SEO in 2026 interview](https://majestic.com/seo-in-2026/mark-williams-cook), [Marketing Speak podcast on AI and SEO](https://www.marketingspeak.com/ai-and-seo-with-mark-williams-cook/), and [Advanced Web Ranking podcast on PAA and AI search](https://www.advancedwebranking.com/blog/from-people-also-ask-to-ai-search). AlsoAsked MCP server enables direct integration with AI coding assistants for intent research automation.
