import streamlit as st
import requests
import os
import base64
from dotenv import load_dotenv

# Load environment
load_dotenv()

# 🛠️ Configurable FastAPI backend URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Streamlit App Config
st.set_page_config(page_title="SDoH Research Assistant", layout="wide")

# ------------------------
# 🚀 Landing Page
# ------------------------
st.title("📊 Social Determinants of Health (SDoH) Research Assistant")

st.markdown("""
Welcome to the **SDoH Research Assistant**.
This tool helps you retrieve, explore, and generate summaries on key reports from:
- 🏥 CDC & WHO reports on Health Equity  
- 📚 Social and Public Health Determinants  
- 🔍 Embedded documents stored in Pinecone  
- ❄️ Snowflake-hosted structured health data  

It is powered by **LangGraph**, **OpenAI GPT-4**, **Pinecone**, and **Snowflake**.
""")

st.divider()

# ------------------------
# 🛠️ Query Interface
# ------------------------
st.subheader("💬 Ask a Research Question")

query = st.text_input("Type your question below:", placeholder="e.g., What did the CDC say about SDoH in 2023?")

st.markdown("**Select Research Agents to Use:**")

rag_agent_selected = st.checkbox("📦 RAG Agent (Pinecone)", value=True)
snowflake_agent_selected = st.checkbox("❄️ Snowflake Agent (Structured Data)", value=False)
web_agent_selected = st.checkbox("🌐 Web Search Agent (Real-Time Insights)", value=False)

submit = st.button("🔍 Run Research")

# ------------------------
# 🚀 Call FastAPI Backend
# ------------------------
if submit:
    if not query.strip() and not snowflake_agent_selected:
        st.warning("Please enter a question or enable an agent.")
    else:
        # 📦 RAG Agent Output
        if rag_agent_selected:
            st.subheader("📦 RAG Agent Output")
            with st.spinner("Querying vector database..."):
                try:
                    response = requests.post(f"{FASTAPI_URL}/rag_query", json={"query": query})
                    data = response.json()
                    st.success("✅ RAG Complete")
                    st.markdown("### 🧠 Final Answer:")
                    st.write(data["response"])
                except Exception as e:
                    st.error(f"❌ RAG Agent failed: {e}")

        # ❄️ Snowflake Agent Output
        if snowflake_agent_selected:
            st.subheader("❄️ Snowflake Agent Output")

            # 📊 Chart 1: Stress by State
            with st.spinner("Fetching stress-level data from Snowflake..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/stress")
                    data = response.json()
                    st.success("✅ Stress Analysis Complete")

                    st.markdown("### 📊 Stress Levels by State")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to fetch Stress Chart: {e}")

            # 📊 Chart 2: Job Satisfaction vs Stress
            with st.spinner("Fetching job satisfaction vs stress data..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/job_satisfaction_vs_stress")
                    data = response.json()
                    st.success("✅ Job Satisfaction Analysis Complete")

                    st.markdown("### 💼 Job Satisfaction vs 😟 Stress")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to fetch Job Satisfaction Chart: {e}")

            # 📊 Chart 3: Education vs Stress
            with st.spinner("Fetching education vs stress data..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/education_vs_stress")
                    data = response.json()
                    st.success("✅ Education Analysis Complete")

                    st.markdown("### 🎓 Education Level vs 😟 Stress")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to fetch Education Chart: {e}")

            # 📊 Chart 4: Income vs Stress
            with st.spinner("Fetching income vs stress data..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/income_vs_stress")
                    data = response.json()
                    st.success("✅ Income Analysis Complete")

                    st.markdown("### 💰 Income Level vs 😟 Stress")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to fetch Income Chart: {e}")

            # 📊 Chart 5: Cognition vs Stress
            with st.spinner("Fetching cognition vs stress data..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/cognition_vs_stress")
                    data = response.json()
                    st.success("✅ Cognition Analysis Complete")

                    st.markdown("### 🧠 Need for Cognition vs 😟 Stress")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to fetch Cognition Chart: {e}")

            # 📊 Chart 6: Primary Care Visits vs Stress
            with st.spinner("Fetching primary care vs stress data..."):
                try:
                    response = requests.get(f"{FASTAPI_URL}/snowflake/primarycare_vs_stress")
                    data = response.json()
                    st.success("✅ Primary Care Analysis Complete")

                    st.markdown("### 🩺 Primary Care Visits vs 😟 Stress")
                    st.markdown(data["summary"])
                    st.image(base64.b64decode(data["chart"]), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Failed to fetch Primary Care Chart: {e}")

        if web_agent_selected:
            st.subheader("🌐 Web Search Agent Output")
            with st.spinner("Searching the web for real-time updates..."):
                try:
                    response = requests.post(f"{FASTAPI_URL}/web/search", json={"query": query})
                    data = response.json()
                    st.success("✅ Web Search Complete")
                    st.markdown("### 🌐 Top 10 Relevant Web Sources:")
                    st.write(data["response"])
                except Exception as e:
                    st.error(f"❌ Web Agent failed: {e}")


