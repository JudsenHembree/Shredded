from dotenv import dotenv_values
from langchain import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

config = dotenv_values(".env")
openai_key = str(config['OPENAI_KEY'])
MODEL = "gpt-3.5-turbo"

template = """You are a chatbot talking with one to many human participants.

        {History}
        {Message}
        AI: """

chat_prompt_template = PromptTemplate(
        input_variables=["History", "Message"],
        template=template,
        )

chat_gpt = ChatOpenAI(openai_api_key=openai_key, model_name=MODEL, \
        temperature=0.9)
chain = LLMChain(
        llm=chat_gpt, 
        prompt=chat_prompt_template,
        verbose=True,
        memory=ConversationSummaryBufferMemory(memory_key="History", llm=OpenAI(openai_api_key=openai_key, temperature=0))
        )

dict_of_chains = {}

def spawn_chain(thread):
    """Spawn a chain"""
    if thread.id not in dict_of_chains:
        dict_of_chains[thread.id] = chain
    else:
        print("Chain already exists")
    return dict_of_chains[thread.id]

def check_for_thread(channel_id):
    """Check if thread exists"""
    if channel_id in dict_of_chains:
        print("Thread exists")
        return True, dict_of_chains[channel_id]
    return False, None
