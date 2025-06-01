from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from langchain_community.chat_models import ChatOllama
from app.database import get_db
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest, Conversation as ConversationSchema, Message as MessageSchema
from app.auth.auth import get_current_user
from app.models.user import User
from agent.kb_agent import run_custom_agent, initialize_ollama, initialize_embeddings, create_retriever_tool, create_web_search_tool
from langchain.chains import RetrievalQA

router = APIRouter()

# Initialize KB Agent components
try:
    print("[DEBUG] Initializing Ollama...")
    initialize_ollama()
    print("[DEBUG] Ollama initialized.")
    print("[DEBUG] Initializing embeddings...")
    vectorstore = initialize_embeddings()
    print(f"[DEBUG] Vectorstore: {vectorstore}")
    print("[DEBUG] Setting up retriever...")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    print(f"[DEBUG] Retriever: {retriever}")
    print("[DEBUG] Loading LLM...")
    llm = ChatOllama(model="llama2", temperature=0)
    print(f"[DEBUG] LLM: {llm}")
    print("[DEBUG] Setting up retrieval chain...")
    retrieval_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    print(f"[DEBUG] Retrieval chain: {retrieval_chain}")
    retriever_tool = create_retriever_tool(retrieval_chain)
    print(f"[DEBUG] Retriever tool: {retriever_tool}")
    web_search_tool = create_web_search_tool()
    print(f"[DEBUG] Web search tool: {web_search_tool}")
    tools = [retriever_tool, web_search_tool]
    print("[DEBUG] Knowledge Base Agent initialized successfully.")
except Exception as e:
    print(f"[ERROR] Error initializing KB Agent: {str(e)}")
    tools = None
    llm = None
    retriever = None

def generate_title(message: str) -> str:
    """Generate a title for the conversation using Ollama."""
    try:
        llm = ChatOllama(model="llama2", temperature=0)
        prompt = f"""Generate a short, concise title (max 5 words) for this conversation based on the first message.
        Message: {message}
        Title:"""
        
        response = llm.invoke(prompt)
        title = response.content.strip()
        
        # Clean up the title (remove quotes, extra spaces, etc.)
        title = title.replace('"', '').replace("'", "").strip()
        
        # If the title is too long, take the first 5 words
        words = title.split()
        if len(words) > 5:
            title = " ".join(words[:5])
            
        return title if title else "New Conversation"
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return "New Conversation"

@router.post("/chat")
async def chat(
    request: Request,
    message: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle chat messages and return AI responses."""
    try:
        # Check if KB Agent components are initialized
        if not tools or not llm or not retriever:
            print("[ERROR] KB Agent components not initialized")
            raise HTTPException(
                status_code=500,
                detail="The AI system is not properly initialized. Please try again in a few moments."
            )

        # Get or create conversation
        try:
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            else:
                conversation = Conversation(user_id=current_user.id)
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
        except Exception as e:
            print(f"[ERROR] Database error while handling conversation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error accessing conversation history. Please try again."
            )

        # Create user message
        try:
            user_message = Message(
                conversation_id=conversation.id,
                content=message,
                role="user"
            )
            db.add(user_message)
            db.commit()
        except Exception as e:
            print(f"[ERROR] Database error while saving user message: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error saving your message. Please try again."
            )

        # Get AI response
        try:
            response = run_custom_agent(
                message,
                tools,
                llm,
                retriever
            )
        except Exception as e:
            print(f"[ERROR] AI response generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="The AI system encountered an error while processing your question. Please try rephrasing your question or try again later."
            )

        # Extract content from response
        try:
            print(f"[DEBUG] Response type: {type(response)}")
            print(f"[DEBUG] Response attributes: {dir(response)}")
            print(f"[DEBUG] Response: {response}")
            
            if isinstance(response, dict):
                # Extract content from dictionary response
                if 'answer' in response:
                    answer_obj = response['answer']
                    if hasattr(answer_obj, 'content'):
                        answer = answer_obj.content
                    else:
                        answer = str(answer_obj)
                elif 'content' in response:
                    answer = response['content']
                else:
                    # Try to find content in nested structures
                    for key, value in response.items():
                        if isinstance(value, dict) and 'content' in value:
                            answer = value['content']
                            break
                        elif isinstance(value, str) and value.strip():
                            answer = value
                            break
                    else:
                        answer = str(response)
                sources = response.get('sources', [])
            else:
                # Handle LangChain message object
                if hasattr(response, 'content'):
                    print(f"[DEBUG] Response content type: {type(response.content)}")
                    print(f"[DEBUG] Response content: {response.content}")
                    # Handle different content types
                    if isinstance(response.content, str):
                        answer = response.content
                    elif hasattr(response.content, 'content'):
                        answer = response.content.content
                    else:
                        answer = str(response.content)
                else:
                    print(f"[DEBUG] No content attribute found, using str(response)")
                    answer = str(response)
                sources = []

            print(f"[DEBUG] Extracted answer: {answer}")
            print(f"[DEBUG] Answer type: {type(answer)}")

            if not answer:
                raise ValueError("Empty response from AI system")

        except Exception as e:
            print(f"[ERROR] Error processing AI response: {str(e)}")
            print(f"[ERROR] Error type: {type(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail="Error processing the AI response. Please try again."
            )

        # Create AI message
        try:
            ai_message = Message(
                conversation_id=conversation.id,
                content=answer,
                role="assistant",
                sources=sources
            )
            db.add(ai_message)
            db.commit()
        except Exception as e:
            print(f"[ERROR] Database error while saving AI response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error saving the AI response. Please try again."
            )

        # Generate title if this is the first message
        if len(conversation.messages) == 2:  # User message + AI response
            try:
                title_prompt = f"Generate a short, descriptive title (max 5 words) for this conversation:\nUser: {message}\nAssistant: {answer}"
                title_response = llm.invoke(title_prompt)
                
                # Extract just the title text from the response
                if isinstance(title_response, dict):
                    title = title_response.get('answer', '')
                elif hasattr(title_response, 'content'):
                    title = title_response.content
                else:
                    title = str(title_response)
                    
                # Clean up the title
                title = title.replace('"', '').replace("'", "").strip()
                # Remove any content= prefix if present
                title = title.replace('content=', '').strip()
                # Remove any additional_kwargs or response_metadata if present
                title = title.split('additional_kwargs')[0].strip()
                
                # If the title is too long, take the first 5 words
                words = title.split()
                if len(words) > 5:
                    title = " ".join(words[:5])
                    
                # Ensure title is not empty
                if not title:
                    title = "New Conversation"
                    
                # Truncate to 100 characters to ensure it fits in the database
                title = title[:100]
                
                conversation.title = title
                db.commit()
            except Exception as e:
                print(f"[ERROR] Error generating title: {str(e)}")
                conversation.title = "New Conversation"
                db.commit()

        return {
            "conversation_id": conversation.id,
            "message": answer,
            "sources": sources
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user."""
    try:
        # Get conversations ordered by most recent
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).all()
        
        # Ensure all conversations have a title
        for conv in conversations:
            if not conv.title:
                conv.title = "New Conversation"
                db.commit()
        
        return conversations
    except Exception as e:
        print(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving conversations"
        )

@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation by ID."""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Ensure conversation has a title
        if not conversation.title:
            conversation.title = "New Conversation"
            db.commit()
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving conversation"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific conversation."""
    try:
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        return messages
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving messages"
        ) 