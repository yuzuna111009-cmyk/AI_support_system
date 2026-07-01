import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.errors import EmptyDataError

# ==========================
# 画面設定
# ==========================

st.set_page_config(
    page_title="AI Student Planner",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Student Planner")

# ==========================
# ファイル名
# ==========================

SCHEDULE_FILE = "schedules.csv"
REFLECTION_FILE = "reflections.csv"

# ==========================
# スケジュールCSV読み込み
# ==========================

def load_schedule():

    columns = [
        "Task",
        "Category",
        "Date",
        "Time",
        "Priority"
    ]

    # CSVが無い場合
    if not os.path.exists(SCHEDULE_FILE):

        df = pd.DataFrame(columns=columns)

        df.to_csv(
            SCHEDULE_FILE,
            index=False
        )

        return df

    try:

        df = pd.read_csv(SCHEDULE_FILE)

    except (EmptyDataError, FileNotFoundError):

        df = pd.DataFrame(columns=columns)

    # 古いCSVでも対応
    for col in columns:

        if col not in df.columns:

            df[col] = ""

    return df[columns]

# ==========================
# Reflection読み込み
# ==========================

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

    except (EmptyDataError, FileNotFoundError):

        df = pd.DataFrame(columns=columns)

    return df

# ==========================
# サイドバー
# ==========================

menu = st.sidebar.selectbox(

    "メニュー",

    [
        "Dashboard",
        "Add Schedule",
        "AI Recommendation",
        "Reflection"
    ]

)
# ============================================
# Dashboard
# ============================================

if menu == "Dashboard":

    st.header("📅 スケジュール一覧")

    df = load_schedule()

    if df.empty:

        st.info("まだ予定が登録されていません。")

    else:

        try:

            df["日時"] = pd.to_datetime(
                df["Date"] + " " + df["Time"]
            )

            df = df.sort_values("日時")

        except:
            pass

        priority_icon = {
            "高": "🔴",
            "中": "🟡",
            "低": "🟢",
            "": "⚪",
            "Not Set": "⚪"
        }

        df["優先"] = df["Priority"].map(priority_icon)

        st.dataframe(

            df[
                [
                    "優先",
                    "Task",
                    "Category",
                    "Date",
                    "Time",
                    "Priority"
                ]
            ],

            use_container_width=True

        )

# ============================================
# Add Schedule
# ============================================

elif menu == "Add Schedule":

    st.header("➕ 予定を追加")

    task = st.text_input(
        "タスク名"
    )

    category = st.selectbox(

        "カテゴリー",

        [
            "授業",
            "課題",
            "アルバイト",
            "サークル",
            "就職活動",
            "その他"
        ]

    )

    task_date = st.date_input(
        "日付",
        date.today()
    )

    task_time = st.time_input(
        "時間"
    )

    if st.button("予定を保存"):

        if task == "":

            st.warning("タスク名を入力してください。")

        else:

            df = load_schedule()

            new_row = pd.DataFrame({

                "Task":[task],

                "Category":[category],

                "Date":[str(task_date)],

                "Time":[str(task_time)],

                "Priority":["未設定"]

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

            st.success("予定を保存しました！")

            st.dataframe(df)
            # ============================================
# AI Recommendation
# ============================================

elif menu == "AI Recommendation":

    st.header("🤖 AIによるスケジュール提案")

    df = load_schedule()

    if df.empty:

        st.warning("先にスケジュールを登録してください。")

    else:

        st.markdown("""
### 使い方

① 「ChatGPTを開く」をクリックします。

② 下のプロンプトをコピーします。

③ ChatGPTへ貼り付けて送信します。

④ ChatGPTが提案したスケジュールを確認します。

⑤ AIの提案を参考に、この画面で優先度を設定します。
""")

        # ChatGPTボタン
        st.link_button(
            "🤖 ChatGPTを開く",
            "https://chatgpt.com"
        )

        # --------------------------
        # プロンプト
        # --------------------------

        schedule_text = df[
            [
                "Task",
                "Category",
                "Date",
                "Time"
            ]
        ].to_string(index=False)

        prompt = f"""
私は大学生です。

以下が私のスケジュールです。

{schedule_text}

次の内容を日本語で回答してください。

① タスクの優先順位

② 1日のおすすめスケジュール

③ それぞれ何時から始めるべきか

④ なぜその優先順位なのか

⑤ 効率よく過ごすためのアドバイス

表形式で分かりやすく回答してください。
"""

        st.subheader("📋 ChatGPTへ貼り付けるプロンプト")

        st.code(prompt)

        # --------------------------
        # ChatGPT回答
        # --------------------------

        ai_answer = st.text_area(
            "📄 ChatGPTの回答を貼り付けてください",
            height=250,
            placeholder="ここにChatGPTの回答を貼り付けます。"
        )

        if ai_answer:

            st.success("AIの提案を参考に優先度を設定してください。")

        st.divider()

        # --------------------------
        # 優先度設定
        # --------------------------

        st.subheader("⭐ タスクの優先度")

        priority_list = []

        options = [
            "高",
            "中",
            "低"
        ]

        for i, row in df.iterrows():

            priority = st.selectbox(

                f"{row['Task']}",

                options,

                index=1,

                key=f"priority_{i}"

            )

            priority_list.append(priority)

        # --------------------------
        # 保存
        # --------------------------

        if st.button("💾 優先度を保存"):

            df["Priority"] = priority_list

            df.to_csv(
                SCHEDULE_FILE,
                index=False
            )

            st.success("優先度を保存しました！")

            st.balloons()
            # ============================================
# Reflection
# ============================================

elif menu == "Reflection":

    st.header("📝 今日の振り返り")

    st.write("今日の生活を振り返り、満足度と感想を記録しましょう。")

    satisfaction = st.slider(
        "今日の満足度",
        min_value=1,
        max_value=5,
        value=3
    )

    comment = st.text_area(
        "今日の感想・反省・改善点"
    )

    if st.button("保存"):

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

        st.success("保存しました！")

    st.divider()

    st.subheader("📊 満足度の記録")

    df = load_reflection()

    if df.empty:

        st.info("まだ振り返りがありません。")

    else:

        fig = px.histogram(
            df,
            x="Satisfaction",
            nbins=5,
            title="満足度の分布"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("📝 過去のコメント")

        st.dataframe(
            df,
            use_container_width=True
        )

# ============================================
# フッター
# ============================================

st.sidebar.markdown("---")
st.sidebar.write("🎓 AI Student Planner")
st.sidebar.write("Version 1.0")
