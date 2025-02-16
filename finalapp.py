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
        [f"**Title:** {item['title']}\n\n**Summary:** {item['content']}\n\n[Read more]({item['link']})\n\n(Source: {item['link']})\n\n" for item in news_data]
    )

    prompt = f"""
    You are an **expert AI analyst, consultant, researcher, and innovator** with deep expertise across multiple domains, including:
    - **Strategic Management:** Industry trends, competitive dynamics, M&A activity.
    - **Financial Analysis:** Investment trends, funding rounds, and financial impact.
    - **Technology & Innovation:** Breakthroughs in AI, automation, and next-gen technologies.
    - **Product Management:** Adoption barriers, market demand, and product innovation.
    - **Operations & Supply Chain:** Automation, efficiency, and procurement strategies.
    - **IT & DevOps:** Scalability, infrastructure, security, and cloud adoption.

    Generate an **executive-level industry analysis** with **Gartner/Forrester/McKinsey/BCG-style insights** that are **comprehensive and not just surface-level trends.**
    
    Your insights should include **detailed explanations**, not just 3-4 word bullet points. Each insight must provide **business context, potential impact, and strategic recommendations.**

    {formatted_news}

    ### **🔍 1. Market Landscape & Competitive Dynamics**
    - 🏆 **Industry Leaders:** Which companies are leading AI innovation, and how are they differentiating themselves?
    - ⚔ **Emerging Challengers:** What startups or mid-tier companies are disrupting incumbents?
    - 🤝 **M&A Trends:** How are acquisitions and partnerships shaping the competitive AI landscape?
    - 🌍 **Sector-Wise Adoption:** How is AI adoption varying across finance, healthcare, retail, and logistics?

    ### **🚀 2. Breakthrough Innovations & Adoption Barriers**
    - 🔬 **AI Advancements:** What are the most disruptive AI breakthroughs?
    - 🚧 **Enterprise Challenges:** What are the biggest barriers to adoption, such as compute constraints, risk mitigation, or data challenges?
    - 📊 **Business Impact:** How do these advancements translate into real-world profitability and efficiency?

    ### **📈 3. Economic & Business Model Disruptions**
    - 💰 **AI-Driven Profitability:** How is AI reshaping cost structures and revenue models?
    - 📉 **Economic Risks:** What industries face decline due to automation, and what reskilling is required?
    - 🏦 **Investor Trends:** Where is VC and private equity investment flowing in AI?

    ### **⚖️ 4. Regulatory & Ethical Considerations**
    - 📜 **Policy Impact:** How do global AI regulations impact different business models?
    - 🏛 **Legal & Compliance Risks:** What are the hidden risks for enterprises deploying AI?
    - 🛡 **AI Governance Strategies:** How should enterprises build AI responsibly to mitigate bias and risk?

    ### **🔮 5. Future Outlook & Strategic Recommendations**
    - 🌟 **Future AI Scenarios:** What are the **3 most likely industry scenarios over the next 5 years?**
    - 🔍 **Strategic Moves for Leaders:**
      - 👨‍💼 **CEOs & Board Members:** Competitive positioning & AI-driven expansion.
      - 🛠 **Tech Leaders & Product Managers:** How to build AI-first products.
      - 💸 **Investors & VCs:** Where to place high-ROI AI investments.
      - 🏢 **Enterprise AI Adoption Teams:** Best practices & risk mitigation.

    **Format insights using structured takeaways and industry-backed reasoning.**
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


