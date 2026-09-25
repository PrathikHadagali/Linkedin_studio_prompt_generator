import streamlit as st
from dotenv import load_dotenv
from app.services.content_engine import generate_content
from app.services.groq_service import GroqQuotaError

load_dotenv()

st.set_page_config(page_title="Agentic LinkedIn Studio — Groq", page_icon="🤖", layout="wide")
st.title("🤖 Agentic LinkedIn Studio")
st.caption("Real-time research → LinkedIn post → ChatGPT image prompt | GROQ ONLY")

with st.sidebar:
    st.header("Content Strategy")
    category = st.selectbox("Category", [
        "Latest Agentic AI", "AI Agents", "LLM Applications", "RAG",
        "MCP / Tool Use", "Multimodal AI", "AI Engineering", "Research Paper",
        "Computer Vision + AI", "XR + AI", "AI Evaluation", "AI Infrastructure"
    ])
    author_name = st.text_input("Your name", "Your Name")
    author_role = st.text_input("Your role", "MS by Research | IIIT Sri City")
    target_audience = st.text_area(
        "Target audience",
        "AI Engineers, AI Solution Engineers, LLM Engineers, Applied AI Researchers, Technical Recruiters and Hiring Managers",
        height=100
    )
    depth = st.select_slider("Research depth", ["Quick", "Standard", "Deep"], value="Standard")
    st.divider()
    use_web = st.checkbox("Groq Browser Search", True)
    use_arxiv = st.checkbox("Search arXiv", True)
    use_github = st.checkbox("Search GitHub", True)

topic = st.text_input("Topic", placeholder="Example: LLM vs AI Agent")

angles = st.multiselect(
    "Research angles",
    [
        "Latest news and announcements", "Recent research papers",
        "Open-source implementations", "Architecture", "Tools and frameworks",
        "Engineering trade-offs", "Evaluation and benchmarks",
        "Practical project ideas", "Hiring / career relevance"
    ],
    default=[
        "Latest news and announcements", "Recent research papers",
        "Architecture", "Engineering trade-offs", "Hiring / career relevance"
    ],
)

if st.button("🚀 Research & Generate", type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("Enter a topic first.")
        st.stop()

    with st.status("Running Agentic AI research pipeline...", expanded=True) as status:
        try:
            st.write("🔎 Groq Browser Search...")
            st.write("📚 arXiv...")
            st.write("💻 GitHub...")
            st.write("🧠 Groq structured synthesis...")
            st.write("🎨 Image prompt generation...")

            result = generate_content(
                topic.strip(), category, angles, depth,
                author_name, author_role, target_audience,
                use_web, use_arxiv, use_github
            )

            status.update(label="Generation completed", state="complete")

        except GroqQuotaError as exc:
            status.update(label="Groq quota/rate limit reached", state="error")
            st.error(str(exc))
            st.stop()

        except Exception as exc:
            status.update(label="Generation failed", state="error")
            st.exception(exc)
            st.stop()

    tabs = st.tabs([
        "LinkedIn Post", "Image Prompt", "Research",
        "Papers", "GitHub", "Sources", "JSON"
    ])

    with tabs[0]:
        st.subheader(result.content.title)
        st.markdown("### Hook")
        st.markdown(result.content.hook)
        st.markdown(result.content.caption)
        st.markdown("### CTA")
        st.markdown(result.content.call_to_action)
        st.subheader("Hashtags")
        st.code(" ".join(result.content.hashtags))
        st.caption(result.content.audience_fit)

    with tabs[1]:
        st.info("Copy this complete prompt into ChatGPT image generation.")
        st.text_area("ChatGPT Image Generation Prompt", result.image_prompt, height=800)

    with tabs[2]:
        st.subheader("Summary")
        st.markdown(result.research.summary)
        for title, values in [
            ("Key facts", result.research.key_facts),
            ("Engineering takeaways", result.research.engineering_takeaways),
            ("Current trends", result.research.current_trends),
            ("Caveats", result.research.caveats),
        ]:
            st.subheader(title)
            for item in values:
                st.markdown(f"- {item}")

    with tabs[3]:
        for p in result.papers:
            st.markdown(f"**{p.title}**")
            st.write(f"{p.authors} | {p.published}")
            st.write(p.url)
            st.caption(p.relevance)
            st.divider()

    with tabs[4]:
        for r in result.github:
            st.markdown(f"**{r.name}** ⭐ {r.stars}")
            st.write(r.description)
            st.write(r.url)
            st.caption(r.relevance)
            st.divider()

    with tabs[5]:
        for s in result.sources:
            st.markdown(f"- [{s.title}]({s.url}) — {s.source_type}")

    with tabs[6]:
        st.json(result.model_dump())
