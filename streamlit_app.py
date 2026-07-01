import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.errors import EmptyDataError

st.set_page_config(page_title="AI Student Planner",page_icon="🎓",layout="wide")
st.title("🎓 AI Student Planner")
SCHEDULE_FILE="schedules.csv"; REFLECTION_FILE="reflections.csv"
def load_csv(path,cols):
    if not os.path.exists(path): return pd.DataFrame(columns=cols)
    try: return pd.read_csv(path)
    except EmptyDataError: return pd.DataFrame(columns=cols)
menu=st.sidebar.selectbox("Menu",["Dashboard","Add Schedule","AI Recommendation","Reflection"])
if menu=="Dashboard":
    df=load_csv(SCHEDULE_FILE,["Task","Category","Date","Time","Priority"])
    st.dataframe(df) if not df.empty else st.info("No schedule yet.")
elif menu=="Add Schedule":
    task=st.text_input("Task"); cat=st.selectbox("Category",["Class","Assignment","Part-time Job","Club Activity","Job Hunting"]); d=st.date_input("Date",date.today()); t=st.time_input("Time")
    if st.button("Save"):
        df=load_csv(SCHEDULE_FILE,["Task","Category","Date","Time","Priority"]); df.loc[len(df)]=[task,cat,str(d),str(t),"Not Set"]; df.to_csv(SCHEDULE_FILE,index=False); st.success("Saved")
elif menu=="AI Recommendation":
    df=load_csv(SCHEDULE_FILE,["Task","Category","Date","Time","Priority"])
    if df.empty: st.warning("Please add your schedule first.")
    else:
        st.link_button("Open ChatGPT","https://chatgpt.com")
        prompt=f"""I am a university student.\n\nHere is my schedule:\n\n{df.to_string(index=False)}\n\nPlease prioritize my tasks, create a recommended daily schedule, explain the priorities, and suggest the best start time. Keep it concise."""
        st.code(prompt)
        st.text_area("Paste ChatGPT's response here")
        pr=[]
        for i,r in df.iterrows(): pr.append(st.selectbox(r["Task"],["High","Medium","Low"],key=str(i)))
        if st.button("Save Priorities"): df["Priority"]=pr; df.to_csv(SCHEDULE_FILE,index=False); st.success("Saved")
else:
    s=st.slider("Satisfaction",1,5); c=st.text_area("Comment")
    if st.button("Submit"):
        df=load_csv(REFLECTION_FILE,["Satisfaction","Comment"]); df.loc[len(df)]=[s,c]; df.to_csv(REFLECTION_FILE,index=False)
    df=load_csv(REFLECTION_FILE,["Satisfaction","Comment"])
    if not df.empty: st.plotly_chart(px.histogram(df,x="Satisfaction"),use_container_width=True)
