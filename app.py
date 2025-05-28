import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Set wide layout
st.set_page_config(page_title="Job Market Dashboard", layout="wide")

# ---------- THEME TOGGLE ----------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# Top-left toggle button
mode_col, _ = st.columns([1, 5])
with mode_col:
    toggle = st.toggle("🌞/🌙", help="Switch Theme")
st.session_state.theme = "Dark" if toggle else "Light"

# ---------- APPLY CSS THEMING ----------
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
            <style>
            .main {
                background-color: #2E073F;
                color: #f1f1f1;
            }
            body, h1, h2, h3, h4, h5, h6, p {
                color: #f1f1f1;
                font-family: 'Segoe UI', sans-serif;
            }

            /* Sidebar - Distinct Color */
            section[data-testid="stSidebar"] {
                background-color: #7A1CAC;
                color: #f1f1f1;
                border-right: 1px solid #333;
            }
            .css-1lcbmhc, .css-1lcbmhc > * {
                color: #f1f1f1 !important;
            }

            /* Buttons */
            .stButton > button, .stDownloadButton > button {
                background-color: #00f5d4 !important;
                color: #000 !important;
                border-radius: 6px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .stDownloadButton > button:hover {
                background-color: #26ffe6 !important;
                transform: scale(1.03);
            }

            /* DataFrames */
            .stDataFrame, .css-1v0mbdj, .css-1aumxhk {
                background-color: #1e1e1e !important;
                color: white;
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .main {
                background-color: #DBFFCB;
                color: #000000;
            }
            body, h1, h2, h3, h4, h5, h6, p {
                color: #212529;
                font-family: 'Segoe UI', sans-serif;
            }

            /* Sidebar - Distinct Color */
            section[data-testid="stSidebar"] {
                background-color: #BEE4D0;
                color: #000000;
                border-right: 1px solid #ddd;
            }
            .css-1lcbmhc, .css-1lcbmhc > * {
                color: #212529 !important;
            }

            /* Buttons */
            .stButton > button, .stDownloadButton > button {
                background-color: #0d6efd !important;
                color: white !important;
                border-radius: 6px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .stDownloadButton > button:hover {
                background-color: #3399ff !important;
                transform: scale(1.03);
            }

            /* DataFrames */
            .stDataFrame {
                background-color: #f8f9fa !important;
                color: #000;
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)


apply_theme()

# ---------- TITLE ----------
emoji = "🌙" if st.session_state.theme == "Dark" else "🌞"
st.title(f"{emoji} Job Market Analysis Dashboard ({st.session_state.theme} Mode)")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data(uploaded_file):
    return pd.read_csv(uploaded_file)

uploaded_file = st.file_uploader("📤 Upload your scraped job CSV file", type=["csv"])

if uploaded_file:
    try:
        df = load_data(uploaded_file)

        # Validate required columns
        if 'Location' not in df.columns or 'Summary' not in df.columns:
            st.error("⚠️ CSV must contain 'Location' and 'Summary' columns.")
        else:
            # Preview Data
            st.markdown("## 📝 Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Sidebar Filters
            st.sidebar.header("🔍 Filter by Location")
            locations = df['Location'].dropna().unique().tolist()
            selected_locations = st.sidebar.multiselect("🌍 Locations", locations, default=locations)

            filtered_df = df[df['Location'].isin(selected_locations)]

            # Job count by location
            st.markdown("## 📍 Top Job Locations")
            top_locs = filtered_df['Location'].value_counts().head(10)
            st.bar_chart(top_locs)

            # Skill analysis
            st.markdown("## 🧠 In-Demand Skills")
            text = ' '.join(filtered_df['Summary'].dropna().str.lower())
            skills = ['python', 'sql', 'excel', 'power bi', 'tableau', 'r', 'aws', 'communication', 'statistics', 'machine learning']
            skill_counts = {skill: text.count(skill) for skill in skills if skill in text}

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📈 Skill Frequencies")
                st.bar_chart(skill_counts)

            with col2:
                st.markdown("### ☁️ WordCloud")
                wc = WordCloud(
                    width=500,
                    height=300,
                    background_color='black' if st.session_state.theme == "Dark" else 'white',
                    colormap='cool' if st.session_state.theme == "Dark" else 'viridis'
                ).generate(text)
                st.image(wc.to_array(), use_column_width=True)

            # Salary data
            if 'Salary' in df.columns:
                st.markdown("## 💰 Salary Overview")
                st.dataframe(filtered_df[['Title', 'Company', 'Salary']].head(10), use_container_width=True)

            # Download button
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Filtered Data", csv, "filtered_jobs.csv", mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
