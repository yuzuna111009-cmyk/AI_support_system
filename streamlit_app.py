
# Placeholder complete app template.
# Replace with your full application as needed.
import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import date
import plotly.express as px
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Student Planner", page_icon="🎓", layout="wide")
st.title("🎓 AI Student Planner")

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Add Schedule", "AI Recommendation", "Reflection"]
)

if menu == "Dashboard":
    st.header("Today's Schedule")
    try:
        df = pd.read_csv("schedules.csv")
        if "Time" in df.columns:
            df["DateTime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str))
            df = df.sort_values("DateTime")
            st.dataframe(df[["Task","Category","Date","Time"]])
        else:
            st.dataframe(df)
    except Exception as e:
        st.info(f"No schedule yet. ({e})")

elif menu == "Add Schedule":
    st.header("Add Schedule")
    task = st.text_input("Task")
    category = st.selectbox("Category",
        ["Class","Assignment","Part-time Job","Club Activity","Job Hunting"])
    task_date = st.date_input("Date", date.today())
    task_time = st.time_input("Time")

    if st.button("Save"):
        new_data = pd.DataFrame({
            "Task":[task],
            "Category":[category],
            "Date":[str(task_date)],
            "Time":[str(task_time)]
        })
        try:
            old = pd.read_csv("schedules.csv")
            new_data = pd.concat([old,new_data], ignore_index=True)
        except FileNotFoundError:
            pass
        new_data.to_csv("schedules.csv", index=False)
        st.success("Saved")

elif menu == "AI Recommendation":
    st.header("AI Recommendation")
    try:
        df = pd.read_csv("schedules.csv")
        schedule_text = df.to_string(index=False)
        if st.button("Generate Plan"):
            prompt = f"""You are a university student planner.

Based on the following schedule:

{schedule_text}

Suggest:
1. Priority order
2. Time allocation
3. Productivity advice

Keep response short.
"""
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role":"user","content":prompt}]
            )
            st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")

elif menu == "Reflection":
    st.header("Daily Reflection")
    satisfaction = st.slider("Satisfaction",1,5)
    comment = st.text_area("Comment")

    if st.button("Submit"):
        new = pd.DataFrame({"Satisfaction":[satisfaction],"Comment":[comment]})
        try:
            old = pd.read_csv("reflections.csv")
            new = pd.concat([old,new], ignore_index=True)
        except FileNotFoundError:
            pass
        new.to_csv("reflections.csv", index=False)
        st.success("Saved")

    try:
        df = pd.read_csv("reflections.csv")
        fig = px.histogram(df, x="Satisfaction")
        st.plotly_chart(fig)
    except FileNotFoundError:
        pass
