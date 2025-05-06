import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from dotenv import load_dotenv
from langchain_core.tools import tool
import snowflake.connector

load_dotenv()

# ✅ Load Snowflake connection info
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_REGION = os.getenv("SNOWFLAKE_REGION")
FULL_ACCOUNT = f"{SNOWFLAKE_ACCOUNT}.{SNOWFLAKE_REGION}"

# ✅ Helper: Connect to Snowflake and run a SQL query
def query_snowflake(sql: str) -> pd.DataFrame:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=FULL_ACCOUNT,
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


# ─────────────────────────────────────────────
# 📊 1. State-wise Stress Chart
# ─────────────────────────────────────────────

def fetch_state_stress_data():
    query = """
        SELECT STATE, AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        GROUP BY STATE
        ORDER BY AVG_STRESS DESC
    """
    return query_snowflake(query)

def plot_state_stress_chart(df):
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values(by="AVG_STRESS", ascending=False)
    plt.bar(df_sorted["STATE"], df_sorted["AVG_STRESS"])
    plt.xticks(rotation=90)
    plt.xlabel("State")
    plt.ylabel("Avg Stress (1 = Low, 7 = High)")
    plt.title("📊 Stress Levels by State")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    return image_base64

def summarize_state_stress(df):
    top = df.sort_values("AVG_STRESS", ascending=False).head(3)
    bottom = df.sort_values("AVG_STRESS", ascending=True).head(3)
    return (
        f"Most stressed states: {', '.join(top['STATE'])}. "
        f"Least stressed states: {', '.join(bottom['STATE'])}."
    )

@tool
def snowflake_stress_analysis():
    """
    Analyzes stress levels across US states from Snowflake SDoH data.
    Returns a base64-encoded bar chart image and a textual summary.
    """
    df = fetch_state_stress_data()
    chart = plot_state_stress_chart(df)
    summary = summarize_state_stress(df)
    return {"chart": chart, "summary": summary}


# ─────────────────────────────────────────────
# 📉 2. Job Satisfaction vs Stress Correlation
# ─────────────────────────────────────────────

@tool
def snowflake_job_satisfaction_vs_stress():
    """
    Compares job satisfaction and stress levels across states from Snowflake SDoH data.
    Returns a base64-encoded scatter plot and a brief interpretation summary.
    """
    query = """
        SELECT STATE, 
               AVG(HW_JOB_SATIS) AS AVG_JOB_SATISFACTION, 
               AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        GROUP BY STATE
    """
    df = query_snowflake(query)

    # 📈 Scatter Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df["AVG_JOB_SATISFACTION"], df["AVG_STRESS"])
    plt.xlabel("Average Job Satisfaction (1 = Low, 7 = High)")
    plt.ylabel("Average Stress Level (1 = Low, 7 = High)")
    plt.title("💼 Job Satisfaction vs 😟 Stress Levels")
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # 🧠 Summary
    correlation = df["AVG_JOB_SATISFACTION"].corr(df["AVG_STRESS"])
    if correlation < -0.4:
        interpretation = "There is a moderate negative correlation: lower job satisfaction tends to associate with higher stress."
    elif correlation > 0.4:
        interpretation = "There is a moderate positive correlation: higher job satisfaction also shows higher stress, which is unusual."
    else:
        interpretation = "There's little to no correlation between job satisfaction and stress."

    summary = f"Correlation: {correlation:.2f}. {interpretation}"

    return {"chart": chart_base64, "summary": summary}


@tool
def snowflake_education_vs_stress():
    """
    Compares stress levels across different education levels.
    Returns a base64-encoded bar chart and a summary.
    """
    query = """
        SELECT 
            AIQ_EDUCATION_V2,
            AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        WHERE AIQ_EDUCATION_V2 IS NOT NULL
        GROUP BY AIQ_EDUCATION_V2
        ORDER BY AVG_STRESS DESC
    """
    df = query_snowflake(query)

    # 📊 Bar Chart
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values(by="AVG_STRESS", ascending=False)
    plt.bar(df_sorted["AIQ_EDUCATION_V2"], df_sorted["AVG_STRESS"])
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Education Level")
    plt.ylabel("Average Stress Level")
    plt.title("🎓 Education Level vs 😟 Stress")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # 🧠 Summary
    top = df_sorted.head(3)
    bottom = df_sorted.tail(3)
    summary = (
        f"Education levels with highest stress: {', '.join(top['AIQ_EDUCATION_V2'])}. "
        f"Lowest stress: {', '.join(bottom['AIQ_EDUCATION_V2'])}."
    )

    return {"chart": chart_base64, "summary": summary}

# ─────────────────────────────────────────────
# 💰 3. Income vs Stress Analysis
# ─────────────────────────────────────────────

@tool
def snowflake_income_vs_stress():
    """
    Analyzes how stress levels vary across income brackets.
    Returns a base64-encoded bar chart and a textual summary.
    """
    query = """
        SELECT 
            CASE 
                WHEN INCOMEIQ_PLUS_V3 BETWEEN 0 AND 100 THEN 'Low Income'
                WHEN INCOMEIQ_PLUS_V3 BETWEEN 101 AND 250 THEN 'Lower-Middle Income'
                WHEN INCOMEIQ_PLUS_V3 BETWEEN 251 AND 450 THEN 'Middle Income'
                WHEN INCOMEIQ_PLUS_V3 BETWEEN 451 AND 650 THEN 'Upper-Middle Income'
                WHEN INCOMEIQ_PLUS_V3 > 650 THEN 'High Income'
                ELSE 'Unknown'
            END AS INCOME_GROUP,
            AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        WHERE INCOMEIQ_PLUS_V3 IS NOT NULL
        GROUP BY INCOME_GROUP
        ORDER BY AVG_STRESS DESC
    """
    df = query_snowflake(query)

    # 📊 Bar Chart
    plt.figure(figsize=(10, 6))
    df_sorted = df.sort_values(by="AVG_STRESS", ascending=False)
    plt.bar(df_sorted["INCOME_GROUP"], df_sorted["AVG_STRESS"])
    plt.xlabel("Income Group")
    plt.ylabel("Average Stress Level (1 = Low, 7 = High)")
    plt.title("💰 Income Group vs 😟 Stress Level")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # 🧠 Summary
    top = df_sorted.head(1)
    bottom = df_sorted.tail(1)
    summary = (
        f"Highest stress observed in '{top.iloc[0]['INCOME_GROUP']}' group. "
        f"Lowest stress in '{bottom.iloc[0]['INCOME_GROUP']}' group."
    )

    return {"chart": chart_base64, "summary": summary}

# ─────────────────────────────────────────────
# 🧠 4. Need for Cognition vs Stress Correlation
# ─────────────────────────────────────────────

@tool
def snowflake_cognition_vs_stress():
    """
    Analyzes the relationship between Need for Cognition and Stress levels.
    Returns a base64-encoded scatter plot and a correlation summary.
    """
    query = """
        SELECT 
            STATE,
            AVG(HW_NEED_FOR_COGNITION) AS AVG_COGNITION,
            AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        WHERE HW_NEED_FOR_COGNITION IS NOT NULL
        GROUP BY STATE
    """
    df = query_snowflake(query)

    # 📈 Scatter Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df["AVG_COGNITION"], df["AVG_STRESS"])
    plt.xlabel("Avg Need for Cognition (1 = Low, 7 = High)")
    plt.ylabel("Avg Stress Level (1 = Low, 7 = High)")
    plt.title("🧠 Need for Cognition vs 😟 Stress")
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # 🔍 Correlation Summary
    correlation = df["AVG_COGNITION"].corr(df["AVG_STRESS"])
    if correlation < -0.4:
        interpretation = "Higher cognitive engagement is associated with lower stress."
    elif correlation > 0.4:
        interpretation = "Higher cognitive engagement may lead to more stress due to overthinking."
    else:
        interpretation = "There's little to no correlation between cognition and stress."

    summary = f"Correlation: {correlation:.2f}. {interpretation}"
    return {"chart": chart_base64, "summary": summary}


@tool
def snowflake_primarycare_vs_stress():
    """
    Compares stress levels across different levels of primary care visits.
    Returns a base64-encoded bar chart and a summary.
    """
    query = """
        SELECT 
            HW_PRIMARY_CARE_VISITS_SC AS VISITS,
            AVG(HW_STRESS_V2) AS AVG_STRESS
        FROM SDOH_SAMPLE
        WHERE HW_PRIMARY_CARE_VISITS_SC IS NOT NULL
        GROUP BY VISITS
        ORDER BY VISITS
    """
    df = query_snowflake(query)

    # 📊 Bar Chart
    plt.figure(figsize=(12, 6))
    plt.bar(df["VISITS"], df["AVG_STRESS"])
    plt.xlabel("Primary Care Visits Score")
    plt.ylabel("Average Stress Level (1 = Low, 7 = High)")
    plt.title("🩺 Primary Care Visits vs 😟 Stress")
    plt.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # 🧠 Summary
    min_stress = df.loc[df["AVG_STRESS"].idxmin()]
    max_stress = df.loc[df["AVG_STRESS"].idxmax()]
    summary = (
        f"Lowest stress (Avg: {min_stress['AVG_STRESS']:.2f}) was seen for visits score {min_stress['VISITS']}. "
        f"Highest stress (Avg: {max_stress['AVG_STRESS']:.2f}) occurred at score {max_stress['VISITS']}."
    )

    return {"chart": chart_base64, "summary": summary}

