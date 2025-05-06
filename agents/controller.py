import os
import operator
from typing import TypedDict, Annotated, List
from functools import partial

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from agents.web_agent.web_tool import web_search

from agents.rag_agent.rag_tool import vector_search
from agents.snowflake_agent.snowflake_tool import (
    snowflake_stress_analysis,
    snowflake_job_satisfaction_vs_stress,
    snowflake_education_vs_stress,
    snowflake_income_vs_stress,
    snowflake_cognition_vs_stress,
    snowflake_primarycare_vs_stress
)

# Load environment
load_dotenv()

# 🔐 Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------
# 📆 Define Agent State
# ---------------------------
class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    intermediate_steps: Annotated[List[AgentAction], operator.add]

# ---------------------------
# 🧐 Create Oracle
# ---------------------------
def init_rag_oracle():
    system_prompt = """
    You are a healthcare assistant with access to two types of tools:
    1. A Pinecone-powered vector search that contains healthcare reports and a detailed document on stress-related chart analysis and frameworks.
    2. A Snowflake-powered structured data agent that visualizes U.S. population trends via bar and scatter charts.

    Use only one tool per query. Follow these rules:

    - If the user asks for a chart, metric comparison, or correlation, prefer the **Snowflake tools**.
    - If the user asks **why a metric is high or low**, or **how to improve it**, or **what frameworks exist**, use the **vector_search tool**.
    - Use vector_search to retrieve guidance from embedded documents, especially the one containing chart-based frameworks and solutions (e.g., additional2_0).
    - Summarize clearly, and include actionable steps or known models (e.g., PERMA Model, CBT, PCMH) if available in retrieved context.
    - If no relevant data is found, respond with "No relevant context found."

    Be precise, helpful, and research-backed.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("assistant", "scratchpad: {scratchpad}"),
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )

    def create_scratchpad(intermediate_steps: List[AgentAction]) -> str:
        scratch = []
        for step in intermediate_steps:
            scratch.append(f"Tool: {step.tool}, input: {step.tool_input}\nOutput: {step.log}")
        return "\n---\n".join(scratch)

    oracle = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: x["chat_history"],
            "scratchpad": lambda x: create_scratchpad(x["intermediate_steps"]),
        }
        | prompt
        | llm.bind_tools([
            vector_search,
            snowflake_stress_analysis,
            snowflake_job_satisfaction_vs_stress,
            snowflake_education_vs_stress,
            snowflake_income_vs_stress,
            snowflake_cognition_vs_stress,
            snowflake_primarycare_vs_stress,
            web_search
        ], tool_choice="any")
    )
    return oracle

# ---------------------------
# 🔀 LangGraph Nodes
# ---------------------------
def run_oracle(state: AgentState, oracle):
    print("🚀 Running Oracle with query:", state["input"])
    output = oracle.invoke(state)

    tool_name = output.tool_calls[0]["name"]
    tool_args = output.tool_calls[0]["args"]

    return {
        **state,
        "intermediate_steps": [
            AgentAction(tool=tool_name, tool_input=tool_args, log="TBD")
        ]
    }

def run_tool(state: AgentState):
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input or {}

    if tool_name == "vector_search":
        output = vector_search.invoke(input=tool_args)
    elif tool_name == "snowflake_stress_analysis":
        output = snowflake_stress_analysis.invoke(input=tool_args)
    elif tool_name == "snowflake_job_satisfaction_vs_stress":
        output = snowflake_job_satisfaction_vs_stress.invoke(input=tool_args)
    elif tool_name == "snowflake_education_vs_stress":
        output = snowflake_education_vs_stress.invoke(input=tool_args)
    elif tool_name == "snowflake_income_vs_stress":
        output = snowflake_income_vs_stress.invoke(input=tool_args)
    elif tool_name == "snowflake_cognition_vs_stress":
        output = snowflake_cognition_vs_stress.invoke(input=tool_args)
    elif tool_name == "snowflake_primarycare_vs_stress":
        output = snowflake_primarycare_vs_stress.invoke(input=tool_args)
    elif tool_name == "web_search":
        output = web_search.invoke(input=tool_args)
    else:
        output = "Tool not recognized."

    print(f"[TOOL] {tool_name}.invoke({tool_args}) =>\n{output}\n")

    return {
        **state,
        "intermediate_steps": [
            AgentAction(tool=tool_name, tool_input=tool_args, log=output)
        ]
    }

def router(state: AgentState):
    if isinstance(state["intermediate_steps"], list):
        return state["intermediate_steps"][-1].tool
    return "vector_search"

# ---------------------------
# 🧠 Build Graph
# ---------------------------
def create_rag_graph():
    oracle = init_rag_oracle()
    graph = StateGraph(AgentState)

    graph.add_node("oracle", partial(run_oracle, oracle=oracle))
    graph.add_node("vector_search", run_tool)
    graph.add_node("snowflake_stress_analysis", run_tool)
    graph.add_node("snowflake_job_satisfaction_vs_stress", run_tool)
    graph.add_node("snowflake_education_vs_stress", run_tool)
    graph.add_node("snowflake_income_vs_stress", run_tool)
    graph.add_node("snowflake_cognition_vs_stress", run_tool)
    graph.add_node("snowflake_primarycare_vs_stress", run_tool)
    graph.add_node("web_search", run_tool)

    graph.set_entry_point("oracle")
    graph.add_conditional_edges("oracle", router)
    graph.add_edge("vector_search", END)
    graph.add_edge("snowflake_stress_analysis", END)
    graph.add_edge("snowflake_job_satisfaction_vs_stress", END)
    graph.add_edge("snowflake_education_vs_stress", END)
    graph.add_edge("snowflake_income_vs_stress", END)
    graph.add_edge("snowflake_cognition_vs_stress", END)
    graph.add_edge("snowflake_primarycare_vs_stress", END)
    graph.add_edge("web_search", END)

    return graph.compile()

# ---------------------------
# 🏁 Run Entry Function
# ---------------------------
def run_rag_agent(query: str):
    graph = create_rag_graph()
    final_state = graph.invoke({
        "input": query,
        "chat_history": [],
        "intermediate_steps": []
    })
    return final_state["intermediate_steps"][-1].log

def run_snowflake_agent():
    return snowflake_stress_analysis.invoke(input={})

def run_snowflake_job_satis_agent():
    return snowflake_job_satisfaction_vs_stress.invoke(input={})

def run_snowflake_education_vs_stress_agent():
    return snowflake_education_vs_stress.invoke(input={})

def run_snowflake_income_vs_stress_agent():
    return snowflake_income_vs_stress.invoke(input={})

def run_snowflake_cognition_vs_stress():
    return snowflake_cognition_vs_stress.invoke(input={})

def run_snowflake_primarycare_vs_stress_agent():
    return snowflake_primarycare_vs_stress.invoke(input={})

def run_web_search_agent(query: str):
    return web_search.invoke(input={"query": query})

if __name__ == "__main__":
    question = "What is the stress level across income groups?"
    answer = run_rag_agent(question)
    print("\n🧠 Final Answer:\n", answer)