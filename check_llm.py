import config
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(dotenv_path=config.BASE_DIR / ".env")

llm = ChatGroq(
    model = config.LLM_MODEL , 
    temperature = 0 , 
    max_tokens = 500 ,
    max_retries=2 ,
    reasoning_format="parsed" 
)

message = [{
    "role" : "system" , 
    "content" : "you are a helpful dsa assistant that can answer questions about data structures and algorithms , you have access to array based solutions of many problems" , 
} , 
    {"role" : "human" , 
    "content" : "greet me in one line"
    }]

response = llm.invoke(message)

print (f"thinking = {response.additional_kwargs}\n\n")
print (response.content )
