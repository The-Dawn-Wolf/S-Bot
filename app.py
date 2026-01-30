import streamlit as st
import json
import re
from groq import Groq
from supabase import create_client
from fpdf import FPDF

# --- 1. THEME: WHITE & CYAN BLUE ---
st.set_page_config(page_title="Shelfie | Lab Edition", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1A1A1A; }
    .auth-container {
        max-width: 450px;
        margin: 80px auto;
        padding: 40px;
        background: #F0F9FF;
        border: 2px solid #00E5FF;
        border-radius: 20px;
        text-align: center;
    }
    .stButton>button {
        background: #00B8D9;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #00E5FF;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNECTIONS ---
@st.cache_resource
def init_connections():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return client, supabase

groq_client, supabase = init_connections()

# --- 3. LOGIC FUNCTIONS ---
def get_sentiment_emoji(arc):
    if not arc: return "😐"
    avg = sum(arc) / len(arc)
    if avg > 5: return "😊"
    if avg > 2: return "🙂"
    if avg < -5: return "😱"
    if avg < -2: return "😨"
    return "😐"

def split_into_chapters(text):
    chapters = re.split(r'(?i)(?=chapter|part|prologue)', text)
    return [c.strip() for c in chapters if len(c.strip()) > 100]

# --- 4. SEPARATE LOGIN SHEET LOGIC ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.title("💠 Shelfie Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("LOG IN"):
            # Check Supabase for user
            user = supabase.table("users").select("*").eq("email", l_email).eq("password", l_pass).execute()
            if user.data:
                st.session_state.authenticated = True
                st.session_state.user_email = l_email
                st.rerun()
            else:
                st.error("Invalid email or password.")
                
    with tab2:
        s_email = st.text_input("New Email", key="s_email")
        s_pass = st.text_input("New Password", type="password", key="s_pass")
        if st.button("CREATE ACCOUNT"):
            try:
                supabase.table("users").insert({"email": s_email, "password": s_pass}).execute()
                st.success("Account created! You can now login.")
            except:
                st.error("User already exists or database error.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. MAIN APP ---
def analyze_text(text, title):
    prompt = ("Return JSON: 'genre', 'summary', 'profanity_level', 'romance_score', "
              "'horror_score', 'comedy_score', 'reading_level', 'emotional_arc': [5 ints]")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": f"Title: {title}\nText: {text[:15000]}"}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# SIDEBAR
with st.sidebar:
    st.title("📂 Vault")
    st.write(f"Logged in: {st.session_state.user_email}")
    if st.button("Sign Out"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()
    res = supabase.table("book_history").select("*").eq("user_email", st.session_state.user_email).order("created_at", desc=True).execute()
    for b in res.data:
        if st.button(f"📄 {b['book_title']}", key=b['id'], use_container_width=True):
            st.session_state.current_data = b

# UI CONTENT
st.title("🧪 Shelfie Intelligence Lab")
col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    book_title = st.text_input("Novel Name")
    uploaded_file = st.file_uploader("Upload Manuscript (.txt)", type=['txt'])
    
    if uploaded_file:
        full_text = uploaded_file.read().decode("utf-8")
        chapters = split_into_chapters(full_text)
        choice = st.selectbox("Select Chapter", range(len(chapters)), format_func=lambda x: f"Chapter {x+1}")
        text_to_process = chapters[choice]
    else:
        text_to_process = st.text_area("Or Paste Excerpt", height=200)

    if st.button("🔬 RUN NEURAL SCAN"):
        with st.spinner("Analyzing..."):
            data = analyze_text(text_to_process, book_title)
            data['book_title'] = book_title
            supabase.table("book_history").insert({
                "user_email": st.session_state.user_email, "book_title": book_title,
                "genre": data.get('genre'), "summary": data.get('summary'),
                "profanity_level": data.get('profanity_level'), "emotional_arc": data.get('emotional_arc'),
                "reading_level": data.get('reading_level')
            }).execute()
            st.session_state.current_data = data
            st.rerun()

with col_out:
    if 'current_data' in st.session_state:
        d = st.session_state.current_data
        emoji = get_sentiment_emoji(d.get('emotional_arc'))
        
        st.header(f"{emoji} {d.get('book_title')}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Genre", d.get('genre'))
        m2.metric("Safety", d.get('profanity_level'))
        m3.metric("Level", d.get('reading_level'))
        
        st.write("### Emotional Arc")
        st.line_chart(d.get('emotional_arc'))
        st.write(d.get('summary'))