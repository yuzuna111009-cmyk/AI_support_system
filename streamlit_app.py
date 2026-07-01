import os
from datetime import date
import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError

# -----------------------------
# Page Setting
# -----------------------------
st.set_page_config(
    page_title="AI Student Planner",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Student Planner")

# -----------------------------
# File Names
# -----------------------------
SCHEDULE_FILE = "schedules.csv"
REFLECTION_FILE = "reflections.csv"

# -----------------------------
# Create Schedule File
# -----------------------------
def load_schedule():

    columns = [
        "Task",
        "Category",
        "Date",
        "Time",
        "Priority"
    ]

    if not os.path.exists(SCHEDULE_FILE):

        df = pd.DataFrame(columns=columns)

        df.to_csv(
            SCHEDULE_FILE,
            index=False
        )

        return df

    try:

        df = pd.read_csv(SCHEDULE_FILE)

    except EmptyDataError:

        df = pd.DataFrame(columns=columns)

    # 古いCSVでも列を追加
    for col in columns:

        if col not in df.columns:

            df[col] = ""

    return df[columns]

# -----------------------------
# Create Reflection File
# -----------------------------
def load_reflection():

    columns = [
        "Satisfaction",
        "Comment"
    ]

    if not os.path.exists(REFLECTION_FILE):

        df = pd.DataFrame(columns=columns)

        df.to_csv(
            REFLECTION_FILE,
            index=False
        )

        return df

    try:

        df = pd.read_csv(REFLECTION_FILE)

    except EmptyDataError:

        df = pd.DataFrame(columns=columns)

    return df

# -----------------------------
# Sidebar
# -----------------------------
menu = st.sidebar.selectbox(

    "Menu",

    [
        "Dashboard",
        "Add Schedule",
        "AI Recommendation",
        "Reflection"
    ]

)

# ==================================================
# Dashboard
# ==================================================

if menu == "Dashboard":

    st.header("📅 Today's Schedule")

    df = load_schedule()

    if df.empty:

        st.info("No schedule yet.")

    else:

        try:

            df["DateTime"] = pd.to_datetime(
                df["Date"].astype(str)
                + " "
                + df["Time"].astype(str)
            )

            df = df.sort_values("DateTime")

        except:

            pass

        st.dataframe(

            df[
                [
                    "Task",
                    "Category",
                    "Date",
                    "Time",
                    "Priority"
                ]
            ],

            use_container_width=True

        )

# ==================================================
# Add Schedule
# ==================================================

elif menu == "Add Schedule":

    st.header("➕ Add Schedule")

    task = st.text_input(
        "Task"
    )

    category = st.selectbox(

        "Category",

        [
            "Class",
            "Assignment",
            "Part-time Job",
            "Club Activity",
            "Job Hunting"
        ]

    )

    task_date = st.date_input(

        "Date",

        date.today()

    )

    task_time = st.time_input(

        "Time"

    )

    if st.button("Save"):

        df = load_schedule()

        new_row = pd.DataFrame({

            "Task":[task],

            "Category":[category],

            "Date":[str(task_date)],

            "Time":[str(task_time)],

            "Priority":["Not Set"]

        })

        df = pd.concat(

            [
                df,
                new_row
            ],

            ignore_index=True

        )

        df.to_csv(

            SCHEDULE_FILE,

            index=False

        )

        st.success("Schedule Saved!")
        # ==================================================
# AI Recommendation
# ==================================================

elif menu == "AI Recommendation":

    st.header("🤖 AI Recommendation")

    df = load_schedule()

    if df.empty:

        st.warning("Please add your schedule first.")

    else:

        st.write("""
This feature uses ChatGPT to help you organize your schedule.

### How to use

1. Click **Open ChatGPT**
2. Copy the prompt below.
3. Paste it into ChatGPT.
4. Copy the AI's recommendation.
5. Set the priority of each task below.
""")

        st.link_button(
            "🚀 Open ChatGPT",
            "https://chatgpt.com"
        )

        prompt = f"""
I am a university student.

Here is my schedule.

{df[['Task','Category','Date','Time']].to_string(index=False)}

Please:

1. Prioritize all tasks.
2. Create an optimized daily schedule.
3. Suggest the best starting time.
4. Explain why each task has that priority.
5. Give advice to improve productivity.

Please answer in a simple table.
"""

        st.subheader("📋 Copy this Prompt")

        st.code(
            prompt,
            language="text"
        )

        ai_answer = st.text_area(
            "📄 Paste ChatGPT's Recommendation Here",
            height=220
        )

        st.divider()

        st.subheader("⭐ Task Priority")

        priority_list = []

        options = [
            "⭐⭐⭐ High",
            "⭐⭐ Medium",
            "⭐ Low"
        ]

        for i, row in df.iterrows():

            priority = st.selectbox(

                row["Task"],

                options,

                index=1,

                key=f"priority_{i}"

            )

            priority_list.append(priority)

        if st.button("💾 Save Priority"):

            df["Priority"] = priority_list

            df.to_csv(
                SCHEDULE_FILE,
                index=False
            )

            st.success("Priority Saved!")

# ==================================================
# Reflection
# ==================================================

elif menu == "Reflection":

    st.header("📝 Daily Reflection")

    satisfaction = st.slider(

        "Satisfaction",

        1,

        5

    )

    comment = st.text_area(

        "Comment"

    )

    if st.button("Submit"):

        df = load_reflection()

        new_row = pd.DataFrame({

            "Satisfaction":[satisfaction],

            "Comment":[comment]

        })

        df = pd.concat(

            [

                df,

                new_row

            ],

            ignore_index=True

        )

        df.to_csv(

            REFLECTION_FILE,

            index=False

        )

        st.success("Reflection Saved!")

    df = load_reflection()

    if not df.empty:

        import plotly.express as px

        fig = px.histogram(

            df,

            x="Satisfaction",

            title="Satisfaction Distribution"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )
