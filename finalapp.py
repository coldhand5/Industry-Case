import os
import sys
import streamlit as st
import urllib.parse
import openai

# ✅ Install dependencies in Streamlit Cloud
os.system("pip install --no-cache-dir --upgrade --force-reinstall feedparser newspaper3k lxml==4.9.3 beautifulsoup4 requests google-generativeai openai")
sys.path.append("/home/appuser/.local/lib/python3.12/site-packages")

# ✅ Import necessary libraries
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

# ✅ Load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

if not GEMINI_API_KEY or not OPENAI_API_KEY:
    st.error("❌ API Keys not found. Set GEMINI_API_KEY and OPENAI_API_KEY in Streamlit Cloud Secrets.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    openai.api_key = OPENAI_API_KEY

# ✅ Gemini Model Configuration
gemini_model = genai.GenerativeModel(
    model_name="gemini-2",
    generation_config={"temperature": 0.9, "top_p": 0.95, "top_k": 64, "max_output_tokens": 10000}
)

# ✅ Fetch News & Generate Detailed Report Using Gemini
def fetch_and_generate_detailed_report(industry, num_articles=10):
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

    gemini_prompt = f"""
    You are an **expert industry researcher** with deep expertise across multiple domains, including:
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
    - **🌎 Sustainability & ESG:** Green technologies, ethical investments, and regulatory impacts.
    - **⚡ Energy & Utilities:** Smart grids, renewable energy trends, and efficiency improvements.
    - **📜 Legal & Compliance:** Data privacy laws, intellectual property, and policy changes.

    Generate an **executive-level industry report** for **{industry}**, covering:
    - **💡 Key Trends** shaping the industry today.
    - **🚧 Challenges & Risks** that businesses must overcome.
    - **📈 Growth Opportunities** and strategic investment areas.
    - **🏆 Competitive Landscape:** Who are the dominant players, and who are the challengers?
    - **🔮 Future Outlook:** What changes will impact this industry over the next 3-5 years?

    {formatted_news}
    """

    return gemini_model.generate_content(gemini_prompt).text

# ✅ Summarize Report Using GPT-3.5 Turbo
def summarize_with_gpt(detailed_text):
    summary_prompt = f"""
    You are a **senior industry consultant** at McKinsey, BCG, or Forrester.
    Your role is to transform **detailed research reports** into **high-level executive summaries**.

    📌 **Executive Summary Requirements:**
    - 🏆 **Key Takeaways (3-5 strategic insights)** – Business impact, cost savings, market trends.
    - 🚧 **Market Risks & Challenges** – Regulatory, operational, or competitive risks.
    - 📈 **Opportunities for Growth & Expansion** – High-impact investment areas.
    - 🏅 **Competitive & Market Positioning** – Market leaders vs. disruptors.
    - 🔮 **Industry Predictions (3-5 years)** – Where is the industry heading?

    📖 **Research Report (from Gemini AI):**
    {detailed_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": summary_prompt}]
    )

    return response['choices'][0]['message']['content']

# ✅ Streamlit UI
st.markdown("# 🔍 Industry Insights")
industry = st.text_input("Enter an Industry (e.g., Fintech, Healthcare, AI)", "")

if st.button("Generate Insights Analysis"):
    industry = industry.strip()
    if industry:
        with st.spinner("🔄 Fetching news and analyzing trends..."):
            detailed_report = fetch_and_generate_detailed_report(industry)
            summary_report = summarize_with_gpt(detailed_report)

        if summary_report:
            st.markdown("## 📑 Executive Summary")
            st.markdown(summary_report, unsafe_allow_html=False)

            st.markdown("## 📖 Full Report (Gemini AI)")
            st.markdown(detailed_report, unsafe_allow_html=False)
        else:
            st.error("🚨 Failed to generate insights.")
    else:
        st.error("❌ Please enter an industry before generating insights.")

# ✅ Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>🚀 Built by Krishna H | Product | Innovation</p>", unsafe_allow_html=True)
