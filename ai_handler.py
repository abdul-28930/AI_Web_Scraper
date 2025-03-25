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
        SystemMessage(content="""You are a real estate data extraction assistant. 
        For each content section, extract ONLY the following information if present:
        - Location: Specific location/area name
        - Price: Property price or price range
        - Property Type: Type of property (apartment, villa, plot, etc.)
        - Size: Size of the property (sq ft, acres, etc.)
        - Developer: Name of the developer/builder if mentioned
        
        Format your response EXACTLY as:
        Location: <location>
        Price: <price>
        Property Type: <type>
        Size: <size>
        Developer: <developer>
        
        If any field is not found, leave it empty but keep the field name.
        Only extract factual information - no summaries or interpretations."""),
        HumanMessage(content=f"""
        Web Content: {content}
        
        Extract the real estate information from this content.""")
    ]
    
    try:
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error processing content: {str(e)}" 