import streamlit as st
import os
import json
import io
import re
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# PDF Generation Imports
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# 1. SETUP & CUSTOM CSS
load_dotenv()
st.set_page_config(page_title="Shelfie AI | Executive Suite", layout="wide")

st.markdown("""
<style>
    div.stButton > button { width: 100% !important; white-space: nowrap !important; }
    [data-testid="column"] { min-width: 200px !important; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# 2. CORE ENGINES
def split_chapters(text):
    """Regex to find Chapter headings."""
    pattern = re.compile(r'(?i)(?:^|\n)(?:chapter|part|section)\s+(?:[0-9]+|[ivxlcm]+|[a-z]+)', re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches: return [("Full Text", text)]
    chapters = []
    for i in range(len(matches)):
        start, end = matches[i].start(), matches[i+1].start() if i+1 < len(matches) else len(text)
        chapters.append((matches[i].group().strip().title(), text[start:end].strip()))
    return chapters

def analyze_document(text, title):
    """Main AI Brain for full document analysis."""
    system_prompt = (
        "You are an Elite Literary Critic. Return a JSON object with: "
        "'genre', 'sentiment', 'tone', 'safety_level' (Low/Med/High), 'protagonist', 'protagonist_desc', "
        "'summary_v1' (Concise), 'summary_v2' (Detailed), 'summary_v3' (Thematic), 'takeaways'."
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text[:15000]}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return {"error": "API Busy"}

def analyze_chapter_safety(ch_title, content):
    """Granular safety check per chapter."""
    prompt = f"Analyze safety for '{ch_title}'. Return JSON: {{'genre': '', 'safety': 'Low/High', 'profanity_score': 1-10}}"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt + "\nContent: " + content[:4000]}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return {"safety": "Unknown", "profanity_score": 0}

# 3. UI LAYOUT
st.title("Shelfie Bot - Full Intelligence Executive Suite")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("Source Upload")
    user_name = st.text_input("Analyst Name", "M Sharath chandra")
    doc_title = st.text_input("Book Title", placeholder="e.g. The Thirteenth Tale")
    uploaded = st.file_uploader("Upload .txt", type=["txt"])
    
    raw_text = uploaded.read().decode("utf-8") if uploaded else ""
    user_text = st.text_area("Content Window", value=raw_text, height=300)
    
    if st.button("🚀 GENERATE FULL INTELLIGENCE REPORT", use_container_width=True):
        if user_text:
            # Word Count & Reading Time
            words = len(user_text.split())
            read_time = f"{max(1, round(words / 238))} min" 
            
            with st.spinner("Neural Mapping & Chapter Filtration..."):
                main_data = analyze_document(user_text, doc_title)
                chapters = split_chapters(user_text)
                ch_results = []
                for ct, cc in chapters[:8]: # Analyze top 8 chapters for speed
                    ch_results.append(analyze_chapter_safety(ct, cc))
                
                report = {
                    "title": doc_title or "Untitled", "user": user_name, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "word_count": words, "reading_time": read_time, "ch_data": ch_results, **main_data
                }
                st.session_state.active_report = report
                st.session_state.history.append(report)

with col_out:
    if "active_report" in st.session_state:
        r = st.session_state.active_report
        st.subheader(f"Report: {r['title']}")
        
        # TOP METRICS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Words", r['word_count'])
        c2.metric("Reading Time", r['reading_time'])
        c3.metric("Safety", r['safety_level'])
        c4.metric("Tone", r['tone'])

        # PROTAGONIST BOX
        st.info(f"👤 **Protagonist:** {r['protagonist']} \n\n {r['protagonist_desc']}")

        # 3-ITERATION SUMMARY
        tab1, tab2, tab3 = st.tabs(["Concise", "Detailed", "Thematic"])
        with tab1: st.write(r['summary_v1'])
        with tab2: st.write(r['summary_v2'])
        with tab3: st.write(r['summary_v3'])

        # CHAPTER ANALYSIS TABLE
        st.markdown("### 📊 Chapter Filtration")
        ch_df = pd.DataFrame(r['ch_data'])
        st.dataframe(ch_df, use_container_width=True)

        # HEATMAP
        fig = px.line(ch_df, y='profanity_score', title="Narrative Profanity Flow", markers=True)
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.title("📚 Vault")
for i, h in enumerate(reversed(st.session_state.history)):
    st.sidebar.button(f"📄 {h['title']}", key=f"h_{i}")

st.caption("Shelfie AI v2.0 | Full Narrative Intelligence Deployed")