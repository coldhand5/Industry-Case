import os
import sys
import streamlit as st
import urllib.parse

# ✅ Ensure dependencies are installed correctly in Streamlit Cloud
os.system("pip install --no-cache-dir --upgrade --force-reinstall feedparser newspaper3k lxml==4.9.3 beautifulsoup4 requests google-generativeai")
sys.path.append("/home/appuser/.local/lib/python3.12/site-packages")

try:
    import feedparser
except ModuleNotFoundError:
    os.system("pip install --no-cache-dir --upgrade --force-reinstall feedparser")
    import feedparser

try:
    from newspaper import Article
except ModuleNotFoundError:
    os.system("pip install --no-cache-dir --upgrade --force-reinstall newspaper3k lxml==4.9.3 beautifulsoup4 requests")
    from newspaper import Article

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    os.system("pip install --no-cache-dir --upgrade --force-reinstall google-generativeai")
    import google.generativeai as genai

# ✅ Ensure `set_page_config` is the first command
st.set_page_config(page_title="Tech Innovation", layout="wide")

# ✅ Load API Key from Environment Variable
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API Key not found. Set GEMINI_API_KEY in Streamlit Cloud Secrets.")
else:
    genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 10000
}

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config
)

# ✅ Fetch News & AI Insights
def fetch_and_generate_insights(industry, num_articles=10):
    if not industry:
        return "⚠ No industry provided. Please enter an industry."
    
    base_url = "https://news.google.com/rss/search?q="
    query = urllib.parse.quote(f"{industry} technology OR innovation OR AI news")
    url = base_url + query
    news_feed = feedparser.parse(url)

    if not news_feed.entries:
        return "⚠ No recent updates found."

    news_data = []
    for i, entry in enumerate(news_feed.entries[:num_articles]):
        try:
            article = Article(entry.link)
            article.download()
            article.parse()
            news_data.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "content": article.text[:1500] + "..."
            })
        except:
            continue

    formatted_news = "\n\n".join(
        [f"**Title:** {item['title']}\n\n**Summary:** {item['content']}\n\n[Read more]({item['link']})\n\n" for item in news_data]
    )

    prompt = f"""
    You are an **expert AI analyst** with deep expertise across multiple domains, including:
    - **Strategic Management:** Industry trends, competitive dynamics, M&A activity.
    - **Financial Analysis:** Investment trends, funding rounds, and financial impact.
    - **Technology & Innovation:** Breakthroughs in AI, automation, and next-gen technologies.
    - **Product Management:** Adoption barriers, market demand, and product innovation.
    - **Operations & Supply Chain:** Automation, efficiency, and procurement strategies.
    - **IT & DevOps:** Scalability, infrastructure, security, and cloud adoption.

    Generate an **executive-level industry analysis** with **Gartner/Forrester/McKinsey/BCG-style insights** covering:

    {formatted_news}

    ### 1️⃣ Market Landscape & Competitive Dynamics
    - Who are the **dominant players, emerging challengers, and disruptors?**
    - How are major **tech giants evolving their AI strategies?**
    - What **M&A trends, partnerships, or ecosystem shifts** are reshaping the industry?

    ### 2️⃣ Breakthrough Innovations & Adoption Barriers
    - What are the **most significant AI breakthroughs**?
    - What **real-world bottlenecks** hinder deployment?
    - How do these breakthroughs **translate into competitive advantages**?

    ### 3️⃣ Economic & Business Model Disruptions
    - How are **AI-driven efficiencies** reshaping cost structures?
    - What **new revenue models** are emerging due to AI-driven transformations?
    - Where are we seeing **VC & private equity investments shifting**?

    ### 4️⃣ Regulatory & Ethical Considerations
    - How do **global AI regulations** impact enterprises?
    - What **legal liabilities & ethical risks** should companies be aware of?
    - How are regulatory constraints **shaping innovation strategies**?

    ### 5️⃣ Future Outlook & Strategic Recommendations
    - How will this industry **evolve over the next 3–5 years?**
    - What **high-impact scenarios** should leaders prepare for?
    - Provide strategic recommendations for:
      - **CEOs & Board Members** (Competitive positioning & M&A strategy)
      - **Product & Tech Leaders** (Product roadmap & AI integration)
      - **Investors & VCs** (Where to deploy capital in AI & automation)
      - **Enterprise AI Adoption Teams** (Best practices & risk mitigation)

    Format using **bold formatting** for key insights and structured takeaways.
    """

    return model.generate_content(prompt).text

# ✅ Streamlit UI
st.markdown("# 🔍 Tech Innovation")

industry = st.text_input("Enter an Industry (e.g., AI, Fintech, Blockchain)", "")

if st.button("Generate Insights Analysis"):
    industry = industry.strip()
    if industry:
        with st.spinner("Fetching news and analyzing trends..."):
            insights = fetch_and_generate_insights(industry)
        
        if insights:
            st.markdown(insights, unsafe_allow_html=False)
        else:
            st.error("Failed to generate insights.")
    else:
        st.error("❌ Please enter an industry before generating AI insights.")

st.sidebar.info("🚀 Uses Google Gemini AI + Google News RSS")
