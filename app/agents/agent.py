from app.infrastructure.llm import llm
from app.infrastructure.graph import graph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
from tools.utils import get_session_id
from tools.vector import get_clause_similarity
from tools.cypher import cypher_qa

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a legal assistant helping with analysis of startup-related contracts such as NDAs, partnership agreements, IP transfers, and investment agreements. Answer user questions using the tools provided. If you need to search for similar clauses or relationship insights, use the appropriate tool."),
        ("human", "{input}"),
    ]
)

legal_chat = chat_prompt | llm | StrOutputParser()

tools = [
    Tool.from_function(
        name="General Clause Chat",
        description="Use this for general clause discussions or legal questions when no retrieval or graph is required.",
        func=legal_chat.invoke,
    ),

    Tool.from_function(
        name="Similar Clause Search",
        description="Use this when you want to find clauses that are semantically similar to a user query or another clause.",
        func=get_clause_similarity,
    ),

    Tool.from_function(
        name="Clause Database Lookup",
        description="Use this to query legal clause data using Cypher over the graph database.",
        func=cypher_qa.invoke
    )
]

def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

agent_prompt = PromptTemplate.from_template("""
You are a legal assistant helping with the analysis of startup-related contracts such as NDAs, partnership agreements, IP assignments, and investment agreements.

Use the tools provided to answer user questions. These tools include:
- Clause Similarity Search: Use this when the user asks to find similar or related clauses.
- Clause Database Lookup: Use this when the user asks structured questions that can be answered from the graph.
- General Legal Chat: For everything else.

Do not answer questions based on pre-trained knowledge alone. Only use tool output and conversation context.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
Thought: Do I need to use a tool? No
Final Answer: [your response here]
                                            
Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, agent_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def generate_response(user_input):
    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},
    )
    return response['output']
