import logging

import click
from dotenv import load_dotenv
from common.types import AgentSkill, AgentCapabilities, AgentCard
from common.server import A2AServer
from mcp_a2a.langchain_task_manager import PDF2EnglishTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
  skill = AgentSkill(
    id="mcp-a2a-pdf-parser",
    name="PDF Tool",
    description="Parses PDF files and returns their text content.",
    tags=["pdf", "parse", "extract"],
    examples=["Parse this PDF file: <file_path>"],
    inputModes=["text"],
    outputModes=["text"],
  )
  logging.info(skill)
  capabilities = AgentCapabilities(
    streaming=False # We'll leave streaming capabilities out for now
  )
  agent_card = AgentCard(
    name="PDF to English Agent",
    description="This agent reads pdf files and returns English text",
    url=f"http://{host}:{port}/",
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=capabilities,
    skills=[skill]
  )
  logging.info(agent_card)
  task_manager = PDF2EnglishTaskManager()

  server = A2AServer(
    agent_card=agent_card,
    task_manager=task_manager,
    host=host,
    port=port,
  )

# If you uncomment the following lines, you will get the error: ClosedResource
# https://github.com/langchain-ai/langchain-mcp-adapters/issues/78
#   @server.app.on_event("startup")
#   async def setup_tools():
#     await task_manager.setup_tools()

  server.start()

if __name__ == "__main__":
  main()
