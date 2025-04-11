from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from config import AGENT_MODEL, AGENT_TEMPERATURE, ROLES
from knowledge.warehouse_docs import WarehouseKnowledgeBase
from typing import List, Dict, Any

class BaseWarehouseAgent:
    """Base agent class for all warehouse roles"""
    
    def __init__(self, role: str, tools: List):
        """Initialize the agent with role-specific tools and knowledge"""
        if role not in ROLES:
            raise ValueError(f"Role {role} not recognized. Available roles: {list(ROLES.keys())}")
        
        self.role = role
        self.role_description = ROLES[role]["description"]
        self.tools = tools
        
        # Initialize the knowledge base
        self.knowledge_base = WarehouseKnowledgeBase()
        
        # Create the agent
        self._create_agent()
    
    def _create_agent(self):
        """Create the LangChain agent with appropriate tools and knowledge"""
        # Initialize the LLM
        llm = ChatOpenAI(
            model=AGENT_MODEL,
            temperature=AGENT_TEMPERATURE
        )
        
        # Create system message
        system_message = f"""You are an AI assistant working in a warehouse management system as a {self.role}.
        {self.role_description}
        
        Follow these guidelines:
        1. Only use the tools available to you for your role.
        2. If you don't have the necessary permissions or tools for a request, explain what the user needs to do instead.
        3. When providing information, try to be specific and actionable.
        4. If you're unsure about something, check the knowledge base first.
        5. Always maintain data security and only share information appropriate to the user's role.
        
        Current date: 2023-04-06
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create conversation memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create the agent
        agent = create_openai_functions_agent(llm, self.tools, prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            coroutine=self.tools,  # Use async run method for tools
        )
    
    async def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """Process a user message and return a response"""
        # Check if we should query the knowledge base
        kb_results = self.knowledge_base.query_knowledge_base(message)
        kb_context = "\n".join([doc.page_content for doc in kb_results])
        
        # Combine the message with knowledge base results
        enriched_message = f"""
        User message: {message}
        
        Relevant information from knowledge base:
        {kb_context}
        """
        
        # Run the agent
        response = await self.agent_executor.ainvoke({
            "input": enriched_message
        })
        
        return {
            "response": response["output"],
            "role": self.role,
            "user_id": user_id
        }