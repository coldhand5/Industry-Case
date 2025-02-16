import os
import sys
import streamlit as st
import urllib.parse
import re

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
        [f"**[{item['title']}]({item['link']})**\n\n📅 Published: {item['published']}\n\n**Summary:** {item['content']}\n\n" for item in news_data]
    )

    news_references = {i+1: item for i, item in enumerate(news_data)}

    prompt = f"""
    You are an **expert industry analyst, consultant, researcher, and innovator** with deep expertise across multiple domains, including:
    - **📊 Strategic Management:** Industry trends, competitive dynamics, M&A activity.
    - **💰 Financial Analysis:** Investment trends, funding rounds, and financial impact.
    - **🚀 Technology & Innovation:** Breakthroughs in AI, automation, and next-gen technologies.
    - **📦 Product Management:** Adoption barriers, market demand, and product innovation.
    - **🏭 Operations & Supply Chain:** Automation, efficiency, and procurement strategies.
    - **💻 IT & DevOps:** Scalability, infrastructure, security, and cloud adoption.
    
    Generate an **executive-level industry analysis** for **{industry}**, similar to insights from **Gartner, Forrester, McKinsey, and BCG**. 
    Your analysis should include **detailed explanations**, not just bullet points, with clear **business context, market impact, and strategic recommendations.**
    
    {formatted_news}
    
    ### **🔍 1. Market Landscape & Competitive Dynamics**
    - 🏆 **Industry Leaders:** Which companies are driving innovation, and what gives them a competitive edge?
    - ⚔ **Emerging Disruptors:** What startups or new entrants are challenging established players?
    - 🤝 **Mergers & Acquisitions:** What recent deals are shaping industry consolidation?
    - 🌍 **Regional Market Variations:** How does this industry differ across key global markets?
    
    ### **🚀 2. Key Innovations & Adoption Barriers**
    - 🔬 **Major Innovations:** What are the latest breakthroughs impacting this industry?
    - 🚧 **Challenges to Growth:** What barriers (costs, regulations, supply chain) are limiting expansion?
    - 📊 **Business Impact:** How do these innovations translate into profits, market share, or efficiency gains?
    
    ### **📈 3. Economic & Financial Implications**
    - 💰 **Revenue & Profit Trends:** What are the most profitable business models in this industry?
    - 📉 **Risks & Disruptions:** What market forces could impact profitability in the short and long term?
    - 🏦 **Investor Sentiment:** Where is venture capital and private equity investment flowing?
    
    **Provide detailed, structured insights with industry-backed reasoning.**
    """
    
    response = model.generate_content(prompt).text
    
    st.markdown(response, unsafe_allow_html=True)

st.markdown("# 🔍 Tech Innovation")

industry = st.text_input("Enter an Industry (e.g., AI, Fintech, Blockchain)", "")

if st.button("Generate Insights Analysis"):
    industry = industry.strip()
    if industry:
        with st.spinner("Fetching news and analyzing trends..."):
            fetch_and_generate_insights(industry)
    else:
        st.error("❌ Please enter an industry before generating AI insights.")

st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 10px; border-top: 1px solid #e5e7eb;'>
    Developed by <b>Krishna H</b> | Product | Innovation
</div>
""", unsafe_allow_html=True)
