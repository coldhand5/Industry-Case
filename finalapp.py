import os
import sys
import streamlit as st
import urllib.parse

# ✅ Ensure dependencies are installed correctly
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

# ✅ Ensure set_page_config is first
st.set_page_config(page_title="Industry Insights", layout="wide")

# ✅ Load API Key
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

# ✅ Fetch News & Industry Insights
def fetch_and_generate_insights(industry, num_articles=10):
    if not industry:
        return "⚠️ No industry provided. Please enter an industry."
    
    base_url = "https://news.google.com/rss/search?q="
    query = urllib.parse.quote(f"{industry} latest trends OR market insights OR innovation news")
    url = base_url + query
    news_feed = feedparser.parse(url)

    if not news_feed.entries:
        return "⚠️ No recent updates found."

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
        [f"**[{item['title']}]({item['link']})**\n\n📅 **Published:** {item['published']}\n\n📰 **Summary:** {item['content']}\n\n" for item in news_data]
    )

    prompt = f"""
    You are an **expert industry analyst, consultant, researcher, and innovator** with deep expertise across multiple domains, including:
    - **📊 Strategic Management:** Industry trends, competitive dynamics, M&A activity.
    - **💰 Financial Analysis:** Investment trends, funding rounds, and financial impact.
    - **🚀 Technology & Innovation:** Breakthroughs in AI, automation, and next-gen technologies.
    - **📦 Product Management:** Adoption barriers, market demand, and product innovation.
    - **🏭 Operations & Supply Chain:** Automation, efficiency, and procurement strategies.
    - **💻 IT & DevOps:** Scalability, infrastructure, security, and cloud adoption.
    - **📈 Business Analysis:** Market research, business model evaluation, and KPI tracking.
    - **🔬 ML Research:** Trends in machine learning, AI models, and experimental breakthroughs.
    - **📡 Digital Transformation:** Implementing technology-driven change across industries.
    - **🛠 Innovation Management:** Identifying and scaling disruptive innovations.
    - **🎯 Marketing & Consumer Insights:** Understanding customer behavior and branding strategies.
    - **🌎 Sustainability & ESG:** Green technologies, ethical investments, and regulatory impacts.
    - **⚡ Energy & Utilities:** Smart grids, renewable energy trends, and efficiency improvements.
    - **📜 Legal & Compliance:** Data privacy laws, intellectual property, and policy changes.
    - **🏥 Healthcare & Biotech:** Medical advancements, biotech research, and digital health.

    ### **📢 Generate Industry Insights**
    Based on the latest industry news and market movements, provide:
    - **💡 Key Trends:** What’s shaping the industry today?
    - **🚧 Challenges & Risks:** What hurdles exist for companies?
    - **📈 Growth Opportunities:** Where are the big wins?
    - **🏆 Competitive Landscape:** Who are the market leaders and challengers?
    - **🔮 Future Outlook:** What does the next 3-5 years look like?

    {formatted_news}
    """

    return model.generate_content(prompt).text

# ✅ Streamlit UI
st.markdown("# 🔍 Industry Insights")

industry = st.text_input("Enter an Industry (e.g., Fintech, Healthcare, AI)", "")

if st.button("Generate Insights Analysis"):
    industry = industry.strip()
    if industry:
        with st.spinner("🔄 Fetching news and analyzing trends..."):
            insights = fetch_and_generate_insights(industry)
        
        if insights:
            st.markdown(insights, unsafe_allow_html=False)
        else:
            st.error("🚨 Failed to generate insights.")
    else:
        st.error("❌ Please enter an industry before generating insights.")

# ✅ Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>🚀 Built by Krishna H | Product | Innovation</p>", unsafe_allow_html=True)
