from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

def init_openai():
    return ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def process_content_with_ai(content, user_query):
    chat = init_openai()
    
    messages = [
        SystemMessage(content="""You are a helpful assistant that analyzes web content. 
        Extract and summarize relevant information based on the user's query."""),
        HumanMessage(content=f"""
        Web Content: {content}
        
        User Query: {user_query}
        
        Please analyze the content and provide relevant information based on the query.""")
    ]
    
    try:
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error processing content: {str(e)}" 