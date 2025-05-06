# Hackathon-Multi-Agent-Research-Application

## Live Application Links

[![codelab](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=1DWXwiNrqbh9kzsL6N7HQ_l1Vuv3GJ-h8tar_hWyhF6E#0)
* Streamlit App(not live): http://192.241.155.93:8501
* FastAPI Docs(not live): http://192.241.155.93:8000/docs

## Technologies Used

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Tavily](https://img.shields.io/badge/Tavily-007ACC?style=for-the-badge&logo=internetexplorer&logoColor=white)](https://www.tavily.com/)
[![Snowflake](https://img.shields.io/badge/Snowflake-56B9EB?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-6A4CBB?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![MistralAI](https://img.shields.io/badge/MistralAI-4C75A3?style=for-the-badge&logo=mistralai&logoColor=white)](https://www.mistral.ai/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-000000?style=for-the-badge&logo=matplotlib&logoColor=white)](https://matplotlib.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-008000?style=for-the-badge&logo=python&logoColor=white)](https://docs.pydantic.dev/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)](https://www.digitalocean.com/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)

## Overview

This project builds a multi-agent Retrieval-Augmented Generation (RAG) assistant to analyze stress through the lens of Social Determinants of Health (SDOH), including income, education, employment, and healthcare access. By combining structured datasets from Snowflake, contextual document embeddings via Pinecone, and real-time news through Tavily, the system dynamically generates comprehensive, data-backed reports with visualizations and policy frameworks to support healthcare decision-making.

## Problem Statement

Stress is a growing public health concern influenced by numerous social and economic factors, yet health systems often lack integrated tools to analyze its multifaceted origins. This project addresses the gap by creating a scalable, multi-agent assistant that synthesizes structured metrics, unstructured mental health literature, and real-time policy insights—allowing hospitals, policymakers, and researchers to generate actionable stress reports tailored to diverse population groups.

## Project Goals

- Build a multi-agent RAG assistant to analyze stress through structured, unstructured, and real-time data
- Query health indicators from Snowflake and retrieve policy documents using Pinecone + LangChain
- Integrate Tavily for live web data on mental health and stress
- Generate comprehensive reports with visualizations, summaries, and frameworks
- Orchestrate agents using LangGraph and deploy the system via Docker on DigitalOcean

## Architecture Diagram

![Editor _ Mermaid Chart-2025-04-05-151537](https://github.com/user-attachments/assets/7a11dc8c-cb20-48ed-ae01-505686ccacea)

## Directory Structure
```
Hackathon-Multi-Agent-Research-Application/  
├── .gitignore
├── .env  
├── README.md  
├── docker-compose.yaml  
├── requirements.txt  
├── sdoh_research_report.md  

├── agents/  
│   ├── __init__.py  
│   ├── controller.py  
│   ├── rag_agent/  
│   │   ├── __init__.py  
│   │   ├── pinecone_utils.py  
│   │   ├── rag_tool.py  
│   ├── snowflake_agent/  
│   │   ├── __init__.py  
│   │   ├── snowflake_tool.py  
│   ├── web_agent/  
│       ├── __init__.py  
│       ├── web_tool.py  

├── backend/  
│   ├── Dockerfile  
│   ├── main.py  
│   ├── requirements.txt  

├── frontend/  
│   ├── .streamlit/  
│   │   └── config.toml  
│   ├── Dockerfile  
│   ├── app.py  
│   ├── requirements.txt  

├── parsing_chunks/  
│   ├── chunking.py  
│   ├── mistral_parser.py  
│   ├── pdf_to_s3.py  
```

## Generated Report
- https://github.com/Vemana2330/Hackathon-Multi-Agent-Research-Application/blob/main/sdoh_research_report.md

## Application Workflow

1. The user enters a stress-related query in the Streamlit UI, such as:
  - "Generate a report about the stress levels, how to overcome, frameworks and charts"

2. Agent Selection - The user selects one or more agents:
  - Snowflake Agent: Queries structured health indicators (e.g., income, job satisfaction, primary care visits)
  - RAG Agent: Retrieves insights from embedded mental health and policy documents
  - Web Agent: Pulls real-time news and trends using Tavily APIs

3. Orchestration with LangGraph
  - LangGraph handles the agent routing based on selected inputs and ensures parallel or sequential execution of agents.

4. Data Processing & Aggregation
- Structured data is filtered and visualized (e.g., bar charts, scatter plots)
- Unstructured data is summarized from relevant document chunks
- Web results are ranked, parsed, and de-duplicated for quality

5. Report Generation
  - All outputs—charts, text summaries, insights, and public health frameworks—are compiled into a clean, Markdown-based report format.

6. Display & Download
  - The final report is rendered interactively in Streamlit for viewing and available for download as a complete summary.

## Prerequisites

- Python: Ensure Python is installed on your system. Python 3.8+ is recommended.
- Docker: Ensure Docker Desktop is installed and running.
- Docker Resources: Allocate at least 4 CPUs and 8 GB RAM for smooth execution of Streamlit, FastAPI, and other containers.
- API Keys: Add your OpenAI, Pinecone, and Tavily keys to a .env file in the root directory.
- Streamlit Knowledge: Familiarity with Streamlit will help in understanding and customizing the financial assistant UI.
- FastAPI Knowledge: Understanding FastAPI will assist in debugging backend agent routes and API validation logic.
- LangGraph Orchestration: Basic understanding of how LangGraph handles multi-agent workflows will help in extending the system.
- Vector Database Concepts: Knowledge of semantic search, embeddings, and metadata filtering will be useful when working with Pinecone.
- Snowflake Basics: Knowing how to query structured data from Snowflake will help in modifying or scaling the financial metrics pipeline.
- Git: Required for cloning and managing version control of the repository.
- Open Ports:
  - 8501 for the Streamlit UI
  - 8000 for the FastAPI backend
 
## How to run this Application locally

1. Clone the Repository
```
git clone https://github.com/your-username/Multi-Agent-RAG-Research-Assistant.git
cd Multi-Agent-RAG-Research-Assistant
```

2. Set Up Environment Configuration:
```
AWS_BUCKET_NAME=your_bucket_name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=your_pinecone_index
TAVILY_API_KEY=your_tavily_key
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_REGION=your_snowflake_region
SNOWFLAKE_ROLE=your_snowflake_role
SNOWFLAKE_DATABASE=your_snowflake_database
SNOWFLAKE_SCHEMA=your_snowflake_schema
SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse
SNOWFLAKE_STAGE=your_snowflake_stage
```

3. Create and Activate a Virtual Environment
```
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```
4. Install Required Packages
```
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

5. Build and Start All Services: Make sure Docker is running, then execute:
```
docker-compose up --build
```
This starts:
  - Streamlit Frontend → http://localhost:8501
  - FastAPI Backend → http://localhost:8000/docs

6. Use the Application
  - Open the Streamlit UI
  - Ask your query (e.g., “How does job satisfaction affect stress levels?”)
  - Select agents (RAG / Snowflake / Web)
  - View or download the automatically generated stress report


## REFERENCES

- https://langchain-ai.github.io/langgraph/
- https://colab.research.google.com/github/pinecone-io/examples/blob/master/learn/generation/langchain/langgraph/01-gpt-4o-research-agent.ipynb
- https://docs.pinecone.io/  
- https://docs.pinecone.io/docs/metadata-filtering
- https://docs.snowflake.com/  
- https://docs.snowflake.com/en/user-guide/python-connector  
- https://quickstarts.snowflake.com/
- https://tavily.com/
- https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/
- https://fastapi.tiangolo.com/tutorial/sql-databases/](https://fastapi.tiangolo.com/tutorial/sql-databases/
- https://docs.streamlit.io/](https://docs.streamlit.io/
- https://docs.docker.com
- https://docs.github.com/en](https://docs.github.com/en
