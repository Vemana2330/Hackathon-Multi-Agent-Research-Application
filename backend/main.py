from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import LangGraph controllers
from agents.controller import (
    run_rag_agent,
    run_snowflake_agent,
    run_snowflake_job_satis_agent,
    run_snowflake_education_vs_stress_agent,
    run_snowflake_income_vs_stress_agent,
    run_snowflake_cognition_vs_stress,
    run_snowflake_primarycare_vs_stress_agent,
    run_web_search_agent
    
)

app = FastAPI()

# 🌐 Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- 📦 RAG Agent -----------
class RAGQueryRequest(BaseModel):
    query: str

@app.post("/rag_query")
async def rag_query(request: RAGQueryRequest):
    result = run_rag_agent(request.query)
    return {"response": result}

# ----------- ❄️ Snowflake Agents -----------

@app.get("/snowflake/stress")
async def snowflake_stress():
    result = run_snowflake_agent()
    return result  # {"chart": ..., "summary": ...}

@app.get("/snowflake/job_satisfaction_vs_stress")
async def snowflake_job_vs_stress():
    result = run_snowflake_job_satis_agent()
    return result

@app.get("/snowflake/education_vs_stress")
async def snowflake_education_vs_stress():
    result = run_snowflake_education_vs_stress_agent()
    return result

@app.get("/snowflake/income_vs_stress")
async def snowflake_income_vs_stress():
    result = run_snowflake_income_vs_stress_agent()  
    return result

@app.get("/snowflake/cognition_vs_stress")
async def cognition_vs_stress():
    result = run_snowflake_cognition_vs_stress()
    return result

@app.get("/snowflake/primarycare_vs_stress")
async def primarycare_vs_stress():
    result = run_snowflake_primarycare_vs_stress_agent()
    return result

@app.post("/web/search")
async def web_search_endpoint(request: RAGQueryRequest):
    result = run_web_search_agent(request.query)
    return {"response": result}

