import streamlit as st
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0E1117;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Headers */
h1 {
    font-size: 42px;
    font-weight: 700;
    letter-spacing: 1px;
}

h2, h3 {
    font-weight: 600;
    color: #00BFFF;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #00BFFF;
    box-shadow: 0 0 15px rgba(0,191,255,0.3);
}

/* Buttons */
button {
    border-radius: 8px !important;
}

/* Select boxes */
div[data-baseweb="select"] {
    background-color: #161B22 !important;
}

/* Dataframes */
.css-1d391kg {
    background-color: #161B22;
}

</style>
""", unsafe_allow_html=True)
import pandas as pd
import plotly.express as px
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Galaxy Watch Performance System",
    layout="wide"
)

BASE_PATH = "data/"

users = os.listdir(BASE_PATH)
selected_user = st.sidebar.selectbox("Select Athlete", users)
DATA_PATH = f"{BASE_PATH}{selected_user}/"

# -------------------------------------------------
# ROLE THEMES
# -------------------------------------------------
ROLE_THEME = {
    "Athlete": "#1f77b4",
    "Coach": "#2ca02c",
    "Trainer": "#ff7f0e",
    "Team Doctor": "#d62728"
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_available_date_range(dfs):
    valid_dates = []

    for df in dfs:
        if df is not None and not df.empty:
            valid_dates.append(df["timestamp"].min())
            valid_dates.append(df["timestamp"].max())

    if not valid_dates:
        return None, None

    return min(valid_dates).date(), max(valid_dates).date()

def determine_phase(cycle_day):
    if 1 <= cycle_day <= 5:
        return "Menstrual"
    elif 6 <= cycle_day <= 13:
        return "Follicular"
    elif cycle_day == 14:
        return "Ovulation"
    elif 15 <= cycle_day <= 28:
        return "Luteal"
    else:
        return "Unknown"


def validate_date_range(start, end, min_date, max_date):
    if min_date is None:
        return False

    if start > end:
        st.error("❌ Start date cannot be after End date.")
        return False

    if end < min_date or start > max_date:
        st.markdown(
            f"""
            <div style='padding:20px;
                        background-color:#ffe6e6;
                        border-radius:10px;
                        border:2px solid #ff4d4d;'>
    
            <h3 style='color:#cc0000;'>🚫 Date Range Error</h3>
    
            <p style='font-size:16px;'>
            The selected date range is outside the available dataset.
            </p>
    
            <p>
            <b>Available Data:</b><br>
            {min_date} → {max_date}
            </p>
    
            <p>
            Please adjust the date selector in the sidebar.
            </p>
    
            </div>
            """,
            unsafe_allow_html=True
        )
    

        return False

    return True

def role_header(role):
    st.markdown(
        f"""
        <div style="
            padding:20px;
            background: linear-gradient(90deg, #00BFFF, #0066FF);
            border-radius:15px;
            margin-bottom:30px;
            box-shadow: 0 0 20px rgba(0,191,255,0.4);
        ">
            <h1 style='color:white; margin:0;'>
                {role} Performance Dashboard
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

def load_csv(name):
    try:
        df = pd.read_csv(DATA_PATH + name)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except:
        return None

def line_chart(df, column, title):

    fig = px.line(
        df,
        x="timestamp",
        y=column,
        title=title,
        markers=True,
        template="plotly_dark"
    )

    fig.update_traces(
        line=dict(color="#00BFFF", width=3),
        marker=dict(size=6)
    )

    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        hovermode="x unified",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117"
    )

    st.plotly_chart(fig, use_container_width=True)

def metric_row(metrics):
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

def filter_dates(df, start, end):
    if df is None:
        return None
    return df[
        (df["timestamp"].dt.date >= start) &
        (df["timestamp"].dt.date <= end)
    ]

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
calories = load_csv("calories.csv")
activity = load_csv("activity.csv")
heart = load_csv("heart_rate.csv")
sleep = load_csv("sleep.csv")
stress = load_csv("stress.csv")
energy = load_csv("energy.csv")
spo2 = load_csv("spo2.csv")
bp = load_csv("bp.csv")
ecg = load_csv("ecg.csv")
falls = load_csv("falls.csv")
body = load_csv("body_comp.csv")
antiox = load_csv("antioxidants.csv")
menstrual = load_csv("menstrual_cycle.csv")
if menstrual is not None and not menstrual.empty:
    menstrual["calculated_phase"] = menstrual["cycle_day"].apply(determine_phase)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown("""
<h2 style='color:#00BFFF;'>System Controls</h2>
""", unsafe_allow_html=True)

role = st.sidebar.selectbox(
    "Select Role",
    ["Athlete", "Coach", "Trainer", "Team Doctor"]
)

# Get global available date range
min_date, max_date = get_available_date_range([
    calories, activity, heart, sleep, stress,
    energy, spo2, bp, ecg, falls, body, antiox
])

if min_date is None:
    st.error("No valid data found.")
    st.stop()

start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

if not validate_date_range(start_date, end_date, min_date, max_date):
    st.stop()


# Apply filtering
calories = filter_dates(calories, start_date, end_date)
activity = filter_dates(activity, start_date, end_date)
heart = filter_dates(heart, start_date, end_date)
sleep = filter_dates(sleep, start_date, end_date)
stress = filter_dates(stress, start_date, end_date)
energy = filter_dates(energy, start_date, end_date)
spo2 = filter_dates(spo2, start_date, end_date)
bp = filter_dates(bp, start_date, end_date)
ecg = filter_dates(ecg, start_date, end_date)
falls = filter_dates(falls, start_date, end_date)
body = filter_dates(body, start_date, end_date)
antiox = filter_dates(antiox, start_date, end_date)

# -------------------------------------------------
# DASHBOARDS
# -------------------------------------------------

role_header(role)

# =====================
# ATHLETE
# =====================
if role == "Athlete":

    metric_row([
        ("Energy Score", int(energy["energy_score"].iloc[-1]) if energy is not None else 0),
        ("Calories", int(calories["calories"].iloc[-1]) if calories is not None else 0),
        ("Active Minutes", int(activity["active_minutes"].iloc[-1]) if activity is not None else 0)
    ])

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    if sleep is not None:
        sleep["sleep_score"] = sleep[["deep","light","rem"]].sum(axis=1)
        line_chart(sleep, "sleep_score", "Sleep Quality")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    if stress is not None:
        line_chart(stress, "stress_score", "Stress Trend")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    if menstrual is not None and not menstrual.empty:
    
        # Find row matching selected end_date
        selected_row = menstrual[
            menstrual["timestamp"].dt.date == end_date
        ]
    
        if not selected_row.empty:
            current_phase = selected_row["calculated_phase"].iloc[0]
    
            st.markdown("### 🔷 Menstrual Cycle Phase")
            st.success(f"Current Phase (as of {end_date}): {current_phase}")
    
        else:
            st.info("No menstrual data available for selected end date.")

# =====================
# COACH
# =====================
elif role == "Coach":

    if energy is not None and energy["energy_score"].iloc[-1] < 65:
        st.warning("⚠️ Athlete may be under-recovered.")

    line_chart(calories, "calories", "Calories Burned")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    line_chart(activity, "active_minutes", "Active Minutes")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    line_chart(heart, "bpm", "Heart Rate")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    line_chart(energy, "energy_score", "Readiness Score")

# =====================
# TRAINER
# =====================
elif role == "Trainer":

    if heart is not None:
        heart["zone"] = pd.cut(
            heart["bpm"],
            bins=[0,100,120,140,160,220],
            labels=["Z1","Z2","Z3","Z4","Z5"]
        )
        zone_counts = heart["zone"].value_counts().sort_index()
        fig = px.bar(zone_counts, title="Heart Rate Zones")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    if body is not None:
        line_chart(body, "body_fat", "Body Fat %")
        line_chart(body, "muscle_mass", "Muscle Mass")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    if sleep is not None:
        fig = px.area(
            sleep,
            x="timestamp",
            y=["deep","light","rem"],
            title="Sleep Stages"
        )
        st.plotly_chart(fig, use_container_width=True)

# =====================
# TEAM DOCTOR
# =====================
elif role == "Team Doctor":

    if spo2 is not None and spo2["oxygen_percent"].min() < 92:
        st.error("⚠️ Low SpO₂ detected.")

    if ecg is not None:
        st.metric("ECG Abnormal Events", int(ecg["abnormal_flag"].sum()))

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    line_chart(heart, "bpm", "Heart Rate")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    line_chart(spo2, "oxygen_percent", "Blood Oxygen")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    if bp is not None:
        fig = px.line(
            bp,
            x="timestamp",
            y=["systolic","diastolic"],
            title="Blood Pressure"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)

    if menstrual is not None:
        st.subheader("Menstrual Cycle Monitoring")
        fig = px.line(
            menstrual,
            x="timestamp",
            y="symptom_score",
            title="Symptom Severity Trend"
        )
        st.plotly_chart(fig, use_container_width=True)
    elif menstrual is None:
        pass  # File not provided → show nothing
    else:
        st.info("No menstrual data available for selected date range.")

    st.markdown("""
    <hr style="border:1px solid #00BFFF; opacity:0.3;">
    """, unsafe_allow_html=True)
    
    if falls is not None:
        st.subheader("Fall Events")
        st.dataframe(falls[falls["fall_detected"] == 1])

# -------------------------------------------------
st.markdown("---")
st.caption("Galaxy Watch Performance System • Full Upgrade Version")
