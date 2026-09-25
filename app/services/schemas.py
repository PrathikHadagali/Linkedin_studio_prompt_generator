from pydantic import BaseModel

class Paper(BaseModel):
    title: str
    authors: str
    published: str
    url: str
    relevance: str

class GitHubRepo(BaseModel):
    name: str
    url: str
    stars: int
    description: str
    relevance: str

class Source(BaseModel):
    title: str
    url: str
    source_type: str
    date: str

class ResearchPack(BaseModel):
    topic: str
    summary: str
    key_facts: list[str]
    engineering_takeaways: list[str]
    current_trends: list[str]
    caveats: list[str]

class LinkedInContent(BaseModel):
    title: str
    hook: str
    caption: str
    hashtags: list[str]
    call_to_action: str
    audience_fit: str

class CompleteGeneration(BaseModel):
    research: ResearchPack
    content: LinkedInContent
    image_prompt: str
    sources: list[Source]

class FinalPackage(BaseModel):
    research: ResearchPack
    content: LinkedInContent
    image_prompt: str
    papers: list[Paper]
    github: list[GitHubRepo]
    sources: list[Source]
