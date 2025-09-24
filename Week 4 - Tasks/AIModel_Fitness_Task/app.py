import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="AI Workout Planner", layout="wide")

st.title("💪 AI Workout Planner (Scheduler)")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload your Exercises CSV", type=["csv"])

if uploaded_file is not None:
    try:
        exercises_df = pd.read_csv(uploaded_file)
        st.subheader("📋 Uploaded Exercises")
        st.dataframe(exercises_df)

        # Check if "Exercise" column exists
        if "Exercise" not in exercises_df.columns:
            st.error("CSV must contain a column named 'Exercise'")
        else:
            # --- User Inputs ---
            num_days = st.number_input("Enter number of workout days", min_value=1, max_value=30, step=1)

            # Optional filter if exercise data has categories
            filter_col = st.selectbox("Filter by column (optional)", ["None"] + list(exercises_df.columns))
            filtered_df = exercises_df.copy()
            if filter_col != "None":
                filter_values = st.multiselect(f"Select {filter_col} values", exercises_df[filter_col].unique())
                if filter_values:
                    filtered_df = exercises_df[exercises_df[filter_col].isin(filter_values)]

            # --- Generate Schedule ---
            if st.button("Generate Schedule"):
                if not filtered_df.empty:
                    schedule = []
                    for day in range(1, num_days + 1):
                        exercise = random.choice(filtered_df["Exercise"].tolist())
                        schedule.append({"Day": f"Day {day}", "Exercise": exercise})

                    schedule_df = pd.DataFrame(schedule)
                    st.subheader("🏋️ Workout Schedule")
                    st.table(schedule_df)

                    # --- Download Option ---
                    csv = schedule_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Schedule as CSV",
                        data=csv,
                        file_name="workout_schedule.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No exercises available after filtering!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a CSV file with exercises to continue.")
