# after
from mcp_a2a.langchain_agent import create_gpt_agent, run_gpt_agent, create_and_run_mcp_agent
from langgraph.graph.graph import CompiledGraph

import typing
from typing import AsyncIterable
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from common.server.task_manager import InMemoryTaskManager
from common.types import (
  Artifact,
  JSONRPCResponse,
  Message,
  SendTaskRequest,
  SendTaskResponse,
  SendTaskStreamingRequest,
  SendTaskStreamingResponse,
  Task,
  TaskState,
  TaskStatus,
)



class PDF2EnglishTaskManager(InMemoryTaskManager):
  def __init__(self):
    super().__init__()
    self.gpt_agent: typing.Union[None, CompiledGraph] = None
    # self.gpt_agent = create_gpt_agent()
    # print("GPT agent initialized", type(self.gpt_agent), self.gpt_agent)

  async def setup_tools(self):
    print("Inside MyAgentTaskManager.setup_tools")
    # Ideally want to define the agent here but MCP_Langchain gives an error: https://github.com/langchain-ai/langchain-mcp-adapters/issues/78
    # the work around is to create the agent in the on_send_task method: https://github.com/langchain-ai/langchain-mcp-adapters/issues/14#issuecomment-2718782959
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_server_path = os.path.join(current_dir, "mcp_pdf_server.py")
    server_params = StdioServerParameters(
        command="python",
        # Make sure to update to the full absolute path to your mcp_pdf_server.py file
        args=[pdf_server_path],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
      async with ClientSession(
        read_stream=read_stream,
        write_stream=write_stream,
      ) as session:
        print("Inside MyAgentTaskManager.setup_tools.stdio_client")
        await session.initialize()
        print("Session initialized, loading GPT agent")
        self.gpt_agent = await create_gpt_agent(session= session)

    # Ensure your API key is set in the environment
    # load_dotenv()
    # os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "<your_api_key>")
    # # Connect to the MCP server providing parse_pdf over stdio
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # pdf_server_path = os.path.join(current_dir, "mcp_pdf_server.py")
    # async with MultiServerMCPClient({
    #     "pdf": {
    #         "command": "python",
    #         "args": [pdf_server_path],
    #         "transport": "stdio",
    #     }
    # }) as client:
    #     tools = client.get_tools()
    #     print("Tools loaded from MCP server: ", tools)

    #     model = ChatOpenAI(model="gpt-4.1-nano")
    #     self.gpt_agent = create_react_agent(model, tools=tools, prompt="You are a helpful assistant that can parse PDF files and translate them to English. Return the text in English. Do not add any other information other than the text in English.", checkpointer=MemorySaver())
    #     print("Agent initialized")
        # text = """
        # The PDF contains a lot of information about the latest advancements in biomedical research.
        # It discusses various topics including gene therapy, CRISPR technology, and the latest findings in cancer research.
        # """ 
        # result = await agent.ainvoke({"messages": f"Please parse the PDF at '{pdf_path}'"})
        # print("Agent response:\n", result)

  async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
    # Upsert a task stored by InMemoryTaskManager
    await self.upsert_task(request.params)

    task_id = request.params.id
    # Our custom logic that simply marks the task as complete
    # and returns the echo text
    received_text = request.params.message.parts[0].text
    response_text = f"on_send_task received: {received_text}"
    if self.gpt_agent is not None:
      response_text = await run_gpt_agent(gpt_agent=self.gpt_agent, prompt=received_text)
    else:
      response_text = await create_and_run_mcp_agent(message=received_text)
      # load_dotenv()
      # os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "<your_api_key>")
      # # Connect to the MCP server providing parse_pdf over stdio
      # current_dir = os.path.dirname(os.path.abspath(__file__))
      # pdf_server_path = os.path.join(current_dir, "mcp_pdf_server.py")
      # async with MultiServerMCPClient({
      #   "pdf": {
      #       "command": "python",
      #       "args": [pdf_server_path],
      #       "transport": "stdio",
      #   }
      # }) as client:
      #   tools = client.get_tools()
      #   print("Tools loaded from MCP server: ", tools)

      #   model = ChatOpenAI(model="gpt-4.1-nano")
      #   self.gpt_agent = create_react_agent(model, tools=tools, prompt="You are a helpful assistant that can parse PDF files and translate them to English. Return the text in English. Do not add any other information other than the text in English.")
      #   print("Agent initialized")
      #   agent_response = await self.gpt_agent.ainvoke({"messages": received_text})
      #   print("Agent response:\n", agent_response)
      #   response_text = agent_response["messages"][-1].content
    
    task = await self._update_task(
      task_id=task_id,
      task_state=TaskState.COMPLETED,
      response_text=response_text
    )

    # Send the response
    return SendTaskResponse(id=request.id, result=task)

  async def on_send_task_subscribe(
    self,
    request: SendTaskStreamingRequest
  ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
    pass

  async def _update_task(
    self,
    task_id: str,
    task_state: TaskState,
    response_text: str,
  ) -> Task:
    task = self.tasks[task_id]
    agent_response_parts = [
      {
        "type": "text",
        "text": response_text,
      }
    ]
    task.status = TaskStatus(
      state=task_state,
      message=Message(
        role="agent",
        parts=agent_response_parts,
      )
    )
    task.artifacts = [
      Artifact(
        parts=agent_response_parts,
      )
    ]
    return task