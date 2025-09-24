import streamlit as st
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/exercise_dataset.csv")
    df.fillna("", inplace=True)
    return df

df = load_data()

# -----------------------------
# App Title
# -----------------------------
st.set_page_config(page_title="🤖 NLP-Powered Exercise Planner", layout="wide")
st.title("🤖 NLP-Powered Exercise Planner")
st.markdown("""
Generate a **custom workout plan** and explore exercises with **natural language search**  
(e.g., *beginner core exercises with dumbbells*).
""")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🎯 User Preferences")
n_days = st.sidebar.number_input("Workout Days", min_value=1, max_value=30, value=4, step=1)
exercises_per_day = st.sidebar.slider("Exercises per Day", 3, 10, 5)
goal = st.sidebar.selectbox("Training Goal", ["General Fitness", "Strength", "Weight Loss", "Endurance"])
difficulty_pref = st.sidebar.multiselect("Preferred Difficulty", df["Difficulty"].unique())
category_pref = st.sidebar.multiselect("Exercise Type", df["Type"].unique())
shuffle_plan = st.sidebar.checkbox("Shuffle Plan Each Day", value=True)

# -----------------------------
# NLP Search
# -----------------------------
st.subheader("🔎 Natural Language Search")
query = st.text_input("Search exercises (e.g., 'beginner cardio with no equipment')")

if query:
    # Create corpus for TF-IDF
    corpus = (
        df["Exercise Name"] + " " +
        df["Type"] + " " +
        df["Difficulty"] + " " +
        df["Target Body Part"] + " " +
        df["Equipment"]
    ).str.lower()

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(corpus)
    q_vec = vectorizer.transform([query.lower()])
    sims = cosine_similarity(q_vec, X).flatten()
    top_idx = sims.argsort()[-10:][::-1]

    st.write(f"Top matches for **'{query}'**:")
    st.dataframe(df.iloc[top_idx][["Exercise Name", "Type", "Difficulty", "Target Body Part", "Equipment"]].reset_index(drop=True))

st.markdown("---")

# -----------------------------
# Smart Plan Generator
# -----------------------------
if st.button("⚡ Generate My Workout Plan"):
    plan_df = df.copy()

    # Apply filters
    if difficulty_pref:
        plan_df = plan_df[plan_df["Difficulty"].isin(difficulty_pref)]
    if category_pref:
        plan_df = plan_df[plan_df["Type"].isin(category_pref)]

    # Goal-based adjustment
    if goal == "Weight Loss":
        plan_df = pd.concat([plan_df, df[df["Type"] == "Cardio"]]).drop_duplicates()
    elif goal == "Strength":
        plan_df = pd.concat([plan_df, df[df["Type"] == "Strength"]]).drop_duplicates()

    # Generate plan
    st.subheader(f"💪 {n_days}-Day Workout Plan for {goal}")
    for day in range(1, n_days + 1):
        day_plan = plan_df.sample(exercises_per_day) if shuffle_plan else plan_df.head(exercises_per_day)

        with st.expander(f"📅 Day {day}"):
            for idx, row in day_plan.iterrows():
                st.markdown(f"**{row['Exercise Name']}**  |  🏷️ {row['Type']}  |  ⭐ {row['Difficulty']}  |  💪 {row['Target Body Part']}  |  ⏱️ {row['Duration(min)']} min")
        
st.markdown("---")

# -----------------------------
# Full Dataset Display
# -----------------------------
st.subheader("📊 Full Exercise Dataset")
st.dataframe(df)

