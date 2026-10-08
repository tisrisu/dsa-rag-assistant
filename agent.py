import config 
import re
from langchain_groq import ChatGroq
from typing import TypedDict , List
from langchain_core.documents import Document
from ask import retriever , llm , format_context , system_prompt
from langgraph.graph import StateGraph , START , END

class GraphState (TypedDict) :
    question : str
    query : str
    attempts : int
    docs : List[Document]
    answer : str
    good_enough : bool 
    repeating : bool

MAX_ATTEMPTS = 3 
DEBUG = True
grader_llm = ChatGroq (
    model= config.GRADER_LLM ,
    max_tokens= 1000 ,
    temperature= 0 ,
    max_retries = 2,
)
def normalize(text: str):
    return " ".join(re.sub(r"[^a-z0-9\s]", "", text.lower()).split())

def after_grade (state : GraphState ) :
    if state ["good_enough"] :
        return "generate"
    elif state ["attempts"] >= MAX_ATTEMPTS :
        return "generate"
    else :
        return "rewrite"
def retrieve (state : GraphState ) :
    docs = retriever.invoke(state["query"])
    if DEBUG :
         print(f"[retrieve] {[d.metadata['source'].split('\\')[-1] for d in docs]}")
    return {"docs": docs}

def generate_answer(state : GraphState ) :
    context = format_context(state ["docs"])
    messages = [ 
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {state['question']}\nContext: {context}\n"}
    ]

    response = llm.invoke(messages)
    return {"answer": response.content}

def grade (state :GraphState ) :
    context = format_context(state ["docs"])
    messages = [
        {"role" : "system", "content": "behave like a dsa expert and judge whether the given context is sufficient to answer the question given. If it is sufficient, respond with 'yes', otherwise respond with 'no' only . should exactly be in one word."},
        {"role" : "user" , "content": f"Question: {state['question']}\nContext: {context}\n"}
    ]
    response = grader_llm.invoke(messages)
    if DEBUG:
        print(f"[grade] raw verdict: {response.content!r}")
    verdict = response.content.strip().lower().startswith("yes")
    return {"good_enough": verdict}

def stalled (state: GraphState ) :
    if state ['repeating'] :
        return "generate"
    else :
        return "retrieve"
    
def rewrite(state: GraphState):
    context = format_context(state["docs"])
    messages = [
        {"role": "system", "content": "the previous query did not retrieve the relevant DSA solutions. Rewrite the user's question into a short, sharper and clearer query. Reply only with the rewritten query and nothing else."},
        {"role": "user", "content": f"Original Question: {state['question']}\nContext: {context}"},
    ]
    response = llm.invoke(messages)
    new_query = response.content.strip() or state["question"]

    repeating = normalize(new_query) == normalize(state["query"])
    attempts = state["attempts"] + 1

    if DEBUG:
        print(f"[rewrite] attempt {attempts}: {new_query!r} | repeating: {repeating}")
    return {"query": new_query, "attempts": attempts, "repeating": repeating}

builder = StateGraph(GraphState)
builder.add_node ("rewrite", rewrite)
builder.add_node ("generate", generate_answer)
builder.add_node ("grade", grade)
builder.add_node ("retrieve", retrieve) 

builder.add_edge (START, "retrieve")
builder.add_edge ("retrieve", "grade")
builder.add_conditional_edges ("grade",after_grade )
builder.add_conditional_edges ("rewrite", stalled)
builder.add_edge ("generate", END)

graph = builder.compile()

if __name__ == "__main__":
    questions = [
        "what is the capital of India?",
        "moving array elements k places to the right",
    ]

    for question in questions :
        print(f"Q: {question}\n")
        result = graph.invoke ({
            "question": question,
            "query": question,
            "attempts": 0,
            "docs": [],
            "answer": "",
            "good_enough": False , 
            "repeating": False
        })
        print(f"final query: {result['query']}\n")
        print(f"Attempts: {result['attempts']}\n")
        print (f"Good Enough: {result['good_enough']}\n")
        print(f"Answer: {result['answer']}\n")    

        print ("\n\n\n\n")