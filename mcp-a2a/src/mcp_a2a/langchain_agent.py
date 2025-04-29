# agent_client.py
import logging
from langgraph.graph.graph import CompiledGraph

# This script demonstrates how to create a LangChain agent that can parse and summarize a PDF file using an MCP server.
import os


from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
from mcp import ClientSession
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


import tracemalloc
tracemalloc.start(25) # Start tracemalloc and store 25 frames

      
async def create_gpt_agent(session: ClientSession = None) -> CompiledGraph:
    # Ensure your API key is set in the environment
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "<your_api_key>")
    logger.info("OpenAI API key loaded from environment")
    print("OpenAI API key loaded from environment")

    tools = await load_mcp_tools(session)
    print("Tools loaded from MCP server: ", tools)

    model_id = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4.1-nano")
    model = ChatOpenAI(model=model_id)
    prompt = ("You are a helpful assistant that can parse PDF files and translate them to English."
                "Return the text in English. Do not add any other information other than the text in English.")
    agent = create_react_agent(
        model=model, 
        tools=tools, 
        prompt=prompt, 
        # config_schema={"configurable": {"thread_id": "pdf123"}},
        checkpointer=MemorySaver()
    )
    print("Open AI PDF summarizing Agent initialized")
    print("Agent type: ", type(agent))
    return agent

  

async def run_gpt_agent(gpt_agent: CompiledGraph, prompt: str):
  logger.info("Running GPT agent with prompt: " + str(prompt))
  print("Running GPT agent with prompt: ", prompt)
  config = {"configurable": {"thread_id": "pdf1"}}
  agent_response = await gpt_agent.ainvoke(
    {"messages": prompt},
    config=config,
  )
  message = agent_response["messages"][-1].content
  logger.info("GPT Agent response: " + str(message))
  print("GPT Agent response: ", str(agent_response))
  return str(message)

    # # Alternative way to create the agent using MultiServerMCPClient
    # async with MultiServerMCPClient({
    #     "pdf": {
    #         "command": "python",
    #         "args": ["mcp_pdf_server.py"],
    #         "transport": "stdio",
    #     }
    # }) as client:
    #     tools = client.get_tools()
    #     print("Tools loaded from MCP server: ", tools)

    #     model = ChatOpenAI(model="gpt-4.1-nano")
    #     agent = create_react_agent(model, tools=tools, prompt="You are a helpful assistant that can parse PDF files and translate them to English. Return the text in English. Do not add any other information other than the text in English.")
    #     agent.memory = None  # Disable memory for this example
    #     print("Agent initialized")
    #     agent_response = await agent.ainvoke({"messages": prompt})
    #     print("Agent response:\n", agent_response)
    #     message = agent_response["messages"][-1].content
    #     return str(message)

@asynccontextmanager
async def _define_pdf_agent() -> CompiledGraph:
    """
    Create the MCP agent with the PDF parsing tool and return it.
    """

    # Ensure your API key is set in the environment
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "<your_api_key>")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_server_path = os.path.join(current_dir, "mcp_pdf_server.py")
    # Connect to the MCP server providing parse_pdf over stdio
    async with MultiServerMCPClient({
        "pdf": {
            "command": "python",
            "args": [pdf_server_path],
            "transport": "stdio",
        }
    }) as client:
        tools = client.get_tools()
        print("Tools loaded from MCP server: ", tools)

        model = ChatOpenAI(model="gpt-4.1-nano")
        agent = create_react_agent(model, tools=tools, 
                                   prompt="You are a helpful assistant that can parse PDF files and translate them to English. Return the text in English. Do not add any other information other than the text in English.")  # MemorySaver() if you want to save memory
        print("Agent initialized")
        # config = {"configurable": {"thread_id": "pdf1"}}
        # result = await agent.ainvoke({"messages": f"Please parse the PDF at 'sample.pdf'"},config=config)
        # print("Agent response:\n", result)
        # print(f"Agent '{agent.name}' STATE: {agent.get_state(config=config)}")
        yield agent
    
async def create_and_run_mcp_agent(message: str)  -> str:
        """
        Create and run the MCP agent with the given message."""

        async with _define_pdf_agent() as agent:
            # config = {"configurable": {"thread_id": "pdf1"}}
            # print(f"Agent '{agent.name}' STATE: {agent.get_state(config=config)}")
            agent_response = await agent.ainvoke({"messages": message})
            print("Agent response:\n", agent_response)
            message = agent_response["messages"][-1].content
            # logger.info("GPT Agent response: " + str(message))
            # print("GPT Agent response: ", str(agent_response))
            return str(message)

# Please parse the pdf at "/c/_Active_projects/mcp_a2a/mcp-a2a/sample.pdf"