import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

def get_chat_response(question:str)->str:
    """
    return research-oriented answer using groq and langchain
    """
    q=(question or "").strip()
    if not q:
        return "please ask question about diabetes research"
    
    api_key=os.getenv("GROQ_API_KEY")

    llm=ChatGroq(model="llama-3.1-8b-instant",api_key=api_key,temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a healthcare research assistant focused on diabetes. "
            "Provide concise, evidence-informed answers for general education. "
            "Avoid medical diagnosis or personalized treatment. If asked for medical advice, "
            "recommend consulting a licensed clinician. If uncertain, say you don't know."
        )),
        ("user", "{question}"),
    ])

    chain=prompt | llm | StrOutputParser()

    try:
        return chain.invoke({"question": q})
    except Exception as e:
        return f"Chat error: {e}"   

# result=get_chat_response("what is diabetes")
# print(result)