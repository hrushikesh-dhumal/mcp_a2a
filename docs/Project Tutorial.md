# Installation Instructions
These instructions are a sligtly modified version of the [Tutorial](https://google.github.io/A2A/#/tutorials/python/1_introduction).


## Setup your Environment
* Python Environment
We'll be using https://docs.astral.sh/uv/ as our package manager and to set up our project.

The A2A libraries we'll be using require python >= 3.12 which uv can install if you don't already have a matching version. 

**Check** 
```bash
echo 'import sys; print(sys.version)' | uv run -
```  
If you see something similar to the following, you are ready to proceed!  
```bash
3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 13:17:27) [MSC v.1929 64 bit (AMD64)]
```

## Creating A Project
```bash
uv init --package mcp-a2a
cd mcp-a2a
``` 

* Using a Virtual Env
```bash
uv venv .venv
```
For this and any future terminal windows you open, you'll need to source this venv, in case of a linux machine:
```bash
source .venv/bin/activate
```
For Windows powershell:
```bash
.\.venv\Scripts\activate.ps1
```
If you're using a code editor such as VS Code, you'll want to set the Python Interpreter for code completions. In VS Code, press Ctrl-Shift-P and select Python: Select Interpreter. Then select your project my-project followed by the correct python interpreter Python 3.12.3 ('.venv':venv) ./.venv/bin/python
```bash
(base) (.venv) PS mcp-a2a> tree .
Folder PATH listing for volume Windows-SSD
Volume serial number is ###-###
.
├───.venv
│   ├───Lib
│   │   └───site-packages
│   │       └───__pycache__
│   └───Scripts
└───src
    └───mcp_a2a
```

* Adding the Google-A2A Python Libraries
Next we'll add the sample A2A python libraries from Google. If you'd prefer you can instead use the code directly from Google's repository.

```bash
uv add git+https://github.com/google/A2A#subdirectory=samples/python
```

* Setting up the project structure
Let's now create some files we'll later be using
In Unix:
```bash
touch src/my_project/agent.py
touch src/my_project/task_manager.py
```
In Windows:
```bash
New-Item -Path src\mcp_a2a\agent.py -ItemType File
New-Item -Path src\mcp_a2a\task_manager.py -ItemType File
```

* Test Run
If everything is setup correctly, you should now be able to run your application.
```bash
uv run mcp-a2a
```
The output should look something like this.
```bash
    Built mcp-a2a @ file:///~/mcp-a2a
Installed 1 package in 11ms
Hello from mcp-a2a!
```


## Agent Skills
An agent skill is a set of capabilities the agent can perform. Here's an example of what it would look like for our echo agent.

```json
{
  id: "mcp-a2a-echo-skill"
  name: "Echo Tool",
  description: "Echos the input given",
  tags: ["echo", "repeater"],
  examples: ["I will see this echoed back to me"],
  inputModes: ["text"],
  outputModes: ["text"]
}

```

This conforms to the skills section of the [Agent Card](https://google.github.io/A2A/#/documentation?id=representation)

```json
{
  id: string; // unique identifier for the agent's skill
  name: string; //human readable name of the skill
  // description of the skill - will be used by the client or a human
  // as a hint to understand what the skill does.
  description: string;
  // Set of tagwords describing classes of capabilities for this specific
  // skill (e.g. "cooking", "customer support", "billing")
  tags: string[];
  // The set of example scenarios that the skill can perform.
  // Will be used by the client as a hint to understand how the skill can be
  // used. (e.g. "I need a recipe for bread")
  examples?: string[]; // example prompts for tasks
  // The set of interaction modes that the skill supports
  // (if different than the default)
  inputModes?: string[]; // supported mime types for input
  outputModes?: string[]; // supported mime types for output
}
```

* Implementation
Let's create this Agent Skill in code. Open up src/my-project/__init__.py and replace the contents with the following code
```python
from common.types import AgentSkill

def main():
  skill = AgentSkill(
    id="mcp-a2a-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  print(skill)

if __name__ == "__main__":
  main()
```


* Test Run
```bash
uv run mcp-a2a
```
The output should look something like this.
```bash
id='mcp-a2a-echo-skill' name='Echo Tool' description='Echos the input given' tags=['echo', 'repeater'] examples=['I will see this echoed back to me'] inputModes=['text'] outputModes=['text']
```


## Agent Card
Now that we have defined our skills, we can create an Agent Card.

Remote Agents are required to publish an Agent Card in JSON format describing the agent's capabilities and skills in addition to authentication mechanisms. In other words, this lets the world know about your agent and how to interact with it. You can find more details in the [documentation](https://google.github.io/A2A/#/documentation?id=agent-card).


* Implementation
First lets add some helpers for parsing command line arguments. This will be helpful later for starting our server
```bash
uv add click
uv add python-dotenv
```
And update our code
```python
import logging

import click
from dotenv import load_dotenv
from common.types import AgentSkill, AgentCapabilities, AgentCard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
  skill = AgentSkill(
    id="mcp-a2a-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  logging.info(skill)

if __name__ == "__main__":
  main()

```
Next we'll add our Agent Card
```bash
# ...
def main(host, port):
  # ...
  capabilities = AgentCapabilities()
  agent_card = AgentCard(
    name="Echo Agent",
    description="This agent echos the input given",
    url=f"http://{host}:{port}/",
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=capabilities,
    skills=[skill]
  )
  logging.info(agent_card)

if __name__ == "__main__":
  main()

```

* Test Run
Let's give this a run.
```bash
uv run mcp-a2a
```
The output should look something like this.
```bash
INFO:root:id='mcp-a2a-echo-skill' name='Echo Tool' description='Echos the input given' tags=['echo', 'repeater'] examples=['I will see this echoed back to me'] inputModes=['text'] outputModes=['text']
INFO:root:name='Echo Agent' description='This agent echos the input given' url='http://localhost:10002/' provider=None version='0.1.0' documentationUrl=None capabilities=AgentCapabilities(streaming=False, pushNotifications=False, stateTransitionHistory=False) authentication=None defaultInputModes=['text'] defaultOutputModes=['text'] skills=[AgentSkill(id='mcp-a2a-echo-skill', name='Echo Tool', description='Echos the input given', tags=['echo', 'repeater'], examples=['I will see this echoed back to me'], inputModes=['text'], outputModes=['text'])]
```

## Starting A2A Server

We're almost ready to start our server! We'll be using the A2AServer class from Google-A2A which under the hood starts a uvicorn server. However in the future this may change as Google-A2A is still in development.

### Task Manager  
Before we create our server, we need a task manager to handle incoming requests.

We'll be implementing the InMemoryTaskManager interface which requires us to implement two methods

```bash
async def on_send_task(
  self,
  request: SendTaskRequest
) -> SendTaskResponse:
  """
  This method queries or creates a task for the agent.
  The caller will receive exactly one response.
  """
  pass

async def on_send_task_subscribe(
  self,
  request: SendTaskStreamingRequest
) -> AsyncInterable[SendTaskStreamingResponse] | JSONRPCResponse:
  """
  This method subscribes the caller to future updates regarding a task.
  The caller will receive a response and additionally receive subscription
  updates over a session established between the client and the server
  """
  pass
```
Open up `src/mcp_a2a/task_manager.py` and add the following code. We will simply returns a direct echo response and immediately mark the task complete without any sessions or subscriptions

```bash
from typing import AsyncIterable

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
  TaskStatusUpdateEvent,
)

class MyAgentTaskManager(InMemoryTaskManager):
  def __init__(self):
    super().__init__()

  async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
    # Upsert a task stored by InMemoryTaskManager
    await self.upsert_task(request.params)

    task_id = request.params.id
    # Our custom logic that simply marks the task as complete
    # and returns the echo text
    received_text = request.params.message.parts[0].text
    task = await self._update_task(
      task_id=task_id,
      task_state=TaskState.COMPLETED,
      response_text=f"on_send_task received: {received_text}"
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
```

### A2A Server
With a task manager complete, we can now create our server

Open up src/mcp_a2a/__init__.py and add the following code.
```bash
# ...
from common.server import A2AServer
from mcp_a2a.task_manager import MyAgentTaskManager
# ...
def main(host, port):
  # ...

  task_manager = MyAgentTaskManager()
  server = A2AServer(
    agent_card=agent_card,
    task_manager=task_manager,
    host=host,
    port=port,
  )
  server.start()
```

### Test Run
Let's give this a run.
```bash
uv run mcp-a2a
```
The output should look something like this.
```bash
INFO:     Started server process [20840]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:10002 (Press CTRL+C to quit)
```


## Interacting With Your A2A Server
First we'll use Google-A2A's cli tool to send requests to our A2A server. After trying it out, we'll write our own basic client to see how this works under the hood

### Using Google-A2A's cli tool
With your A2A server already running from the previous run
```bash
# This should already be running in your terminal
$ uv run my-project
INFO:     Started server process [20840]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:10002 (Press CTRL+C to quit)
```
Open up a new terminal in the same directory

```bash
source .venv/bin/activate
uv run google-a2a-cli --agent http://localhost:10002
```
For windows:
```bash
.\.venv\Scripts\activate  
uv run google-a2a-cli --agent http://localhost:10002
```
Note: This will only work if you've installed google-a2a from this pull request as the cli was not exposed previously.

Otherwise you'll have to checkout the [Google/A2A](https://github.com/google/A2A/) repository directly, navigate to the samples/python repository and run the cli directly

You can then send messages to your server and pressing Enter

```bash
=========  starting a new task ========

What do you want to send to the agent? (:q or quit to exit): Hello!
```
If everything is working correctly you'll see this in the response

```bash
"message":{"role":"agent","parts":[{"type":"text","text":"on_send_task received: Hello!"}]}
```
To exit type :q and press Enter


## Adding Agent Capabilities
Now that we have a basic A2A server running, let's add some more functionality. We'll explore how A2A can work asynchronously and stream responses.

### Streaming
This allows clients to subscribe to the server and receive multiple updates instead of a single response. This can be useful for long running agent tasks, or where multiple Artifacts may streamed back to the client. See the [Streaming Documentation](https://google.github.io/A2A/#/documentation?id=streaming-support)

First we'll declare our agent as ready for streaming. Open up src/my_project/__init__.py and update AgentCapabilities

```bash

```


```bash

```

```bash

```
```bash

```
```bash

```


```bash

```