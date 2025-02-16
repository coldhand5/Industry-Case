import os
import sys
import streamlit as st
import urllib.parse  # ✅ Ensure urllib is imported

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
    You are an AI analyst. Based on the following recent industry news articles, generate a **detailed report** on key trends, emerging technologies, economic impact, challenges, and predictions for the future.

    {formatted_news}

    **🔍 Industry Leaders:** List **top innovators** in this field, e.g., "OpenAI, Anthropic, DeepSeek, Mistral leading next-gen LLMs."
    
    **🚀 Recent Breakthroughs:** Summarize **key technological advancements** shaping the sector.
    
    **🏢 Enterprise Adoption:** Highlight major corporations integrating these innovations.
    
    **⚖️ Regulatory Risks:** Discuss global **policy & compliance challenges** affecting adoption.
    
    **🔮 Future Outlook:** Predict **upcoming technologies, economic shifts, and market movements.**
    
    Format using emojis & structured points for easy reading.
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
