import os
import sys
import streamlit as st

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
st.set_page_config(page_title="Tech Stack Insights", layout="wide")

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

# ✅ Inject Custom CSS for Styling
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f9;
        }
        .header {
            font-size: 30px;
            font-weight: bold;
            color: #0056b3;
            text-align: center;
            margin-bottom: 20px;
        }
        .news-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out;
        }
        .news-card:hover {
            transform: scale(1.02);
        }
        .section-header {
            font-size: 22px;
            font-weight: bold;
            color: #004085;
            margin-top: 20px;
            border-bottom: 3px solid #0078D4;
            padding-bottom: 8px;
        }
        .insights-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }
        .news-source-link {
            color: #0078D4;
            text-decoration: none;
            font-weight: bold;
        }
        .news-source-link:hover {
            color: #005A9E;
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Fetch News & AI Insights
def fetch_and_generate_insights(industry, num_articles=10):
    base_url = "https://news.google.com/rss/search?q="
    query = urllib.parse.quote(industry + " technology OR innovation OR AI news")
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
        [f"""
        <div class="news-card">
            <b>Title:</b> {item['title']}<br>
            <b>Summary:</b> {item['content']}<br>
            <b>Source:</b> <a class='news-source-link' href='{item['link']}' target='_blank'>Read more</a>
        </div>
        """ for item in news_data]
    )

    prompt = f"""
    You are an AI analyst. Based on the following recent industry news articles, generate a **detailed report** on key trends, emerging technologies, challenges, and predictions for the future.

    {formatted_news}

    **Output:**
    <div class='section-header'>1. Key Trends</div>
    - List at least **5 major trends** shaping this industry, with detailed explanations and examples.
    
    <div class='section-header'>2. Challenges & Risks</div>
    - Discuss **critical barriers** including regulatory, ethical, and technological concerns.
    
    <div class='section-header'>3. Future Predictions</div>
    - Forecast **how this industry will evolve** over the next 5 years. Highlight upcoming **technologies, business models, and trends**.
    
    Format your response with **bold** for key insights.
    """

    return model.generate_content(prompt).text

# ✅ Streamlit UI
st.markdown("<div class='header'>🔍 AI-Powered Tech Stack & Industry Insights</div>", unsafe_allow_html=True)

industry = st.text_input("Enter an Industry (e.g., AI, Fintech, Blockchain)", "")

if st.button("Fetch & Generate Insights"):
    if industry:
        with st.spinner("Fetching news and analyzing trends..."):
            insights = fetch_and_generate_insights(industry)
        
        if insights:
            st.markdown(f"<div class='insights-container'>{insights}</div>", unsafe_allow_html=True)
        else:
            st.error("Failed to generate insights.")
    else:
        st.error("❌ Please enter an industry before generating AI insights.")

st.sidebar.info("🚀 Uses Google Gemini AI + Google News RSS")
