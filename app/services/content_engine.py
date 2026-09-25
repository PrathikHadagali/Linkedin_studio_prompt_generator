from .groq_service import GroqService
from .research_sources import search_arxiv, search_github
from .schemas import CompleteGeneration, FinalPackage

def generate_content(
    topic, category, angles, depth, author_name, author_role,
    target_audience, use_web=True, use_arxiv=True, use_github=True
):
    groq = GroqService()

    web_research = ""
    if use_web:
        web_research = groq.browser_search(f'''
Research this topic for a technical LinkedIn post:

TOPIC: {topic}
CATEGORY: {category}
ANGLES: {", ".join(angles)}
DEPTH: {depth}

Find current Agentic AI developments, recent research, official announcements,
technical articles, open-source projects and engineering discussions.

Prefer primary/official sources. Return concise findings, source URLs, and caveats.
Never invent sources, dates, statistics, benchmarks or product capabilities.
''')

    papers = search_arxiv(topic, 6) if use_arxiv else []
    github = search_github(topic, 6) if use_github else []

    paper_text = "\n".join(
        f"TITLE: {p.title}\nAUTHORS: {p.authors}\nDATE: {p.published}\nURL: {p.url}"
        for p in papers
    ) or "No arXiv results."

    github_text = "\n".join(
        f"REPO: {r.name}\nSTARS: {r.stars}\nDESCRIPTION: {r.description}\nURL: {r.url}"
        for r in github
    ) or "No GitHub results."

    prompt = f'''
Create a complete professional LinkedIn content package.

AUTHOR: {author_name}
ROLE: {author_role}
TARGET AUDIENCE: {target_audience}

TOPIC: {topic}
CATEGORY: {category}
DEPTH: {depth}
ANGLES: {", ".join(angles)}

=== CURRENT WEB RESEARCH ===
{web_research or "Disabled"}

=== ARXIV ===
{paper_text}

=== GITHUB ===
{github_text}

RESEARCH RULES:
- Separate established facts, recent developments, research findings and interpretation.
- Never invent benchmarks, dates, paper findings, repositories, URLs or personal experiences.
- Prefer current, primary and official sources.

LINKEDIN RULES:
Create a credible technical post demonstrating AI engineering, Agentic AI,
LLM, architecture and practical engineering understanding.
Include a strong hook, explanation, architecture/workflow insight, example,
trade-offs, future direction, discussion question and 5-10 focused hashtags.
Do not claim the post guarantees employment or falsely claim personal implementation.

IMAGE PROMPT:
Create a complete prompt that can be pasted into ChatGPT image generation.
Make it a 4:5 professional technical infographic with:
- premium technical editorial style
- modern AI engineering aesthetic
- clean dark professional background
- restrained blue/green accents
- readable typography
- architecture/workflow diagram where useful
- 3-6 clear visual sections
- topic title, core concept, important components and practical takeaway
- small author footer

Do not include fake metrics, fake logos, social-media UI or invented technical claims.

SOURCE AUDIT:
Only list URLs present in the supplied research or clearly verified.
Return only JSON matching the schema.
'''

    result = groq.structured(prompt, CompleteGeneration)

    return FinalPackage(
        research=result.research,
        content=result.content,
        image_prompt=result.image_prompt,
        papers=papers,
        github=github,
        sources=result.sources,
    )
