from app.langgraph.workflows.sql_workflow import WorkflowManager
from app.config.llm_config import LLM
from app.config.db_config import DB, VectorDB
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_core.prompts import PromptTemplate
from typing import List, Optional
from app.config.logging_config import get_logger
from app.api.db.chat_history import Messages, Conversations
from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import json

logger = get_logger(__name__)
llm_instance = LLM()
vectorDB_instance = VectorDB()


def should_use_data_analysis(question: str, has_uploaded_data: bool) -> bool:
    """
    Determine if query needs database analysis or just ChatGPT response.

    Args:
        question: The user's question
        has_uploaded_data: Whether user has uploaded any data

    Returns:
        True if data analysis is needed (SQL query), False for direct chat
    """
    # If no uploaded data, always use direct chat
    if not has_uploaded_data:
        logger.info("No uploaded data - using direct chat mode")
        return False

    question_lower = question.lower()

    # Keywords that explicitly request natural language explanation/summary
    # These should NEVER trigger SQL analysis
    explanation_keywords = [
        'explain', 'describe', 'what is', 'tell me about',
        'summarize', 'summary', 'overview', 'understand',
        'clarify', 'elaborate', 'provide details', 'logic',
        'how does', 'what does', 'meaning of'
    ]

    # If asking for explanation/summary, use direct chat (with data context if needed)
    if any(keyword in question_lower for keyword in explanation_keywords):
        logger.info(f"Explanation/summary request detected - using direct chat mode")
        return False

    # Keywords that REQUIRE SQL/database query
    sql_required_keywords = [
        'how many', 'count', 'sum', 'average', 'mean',
        'show all', 'list all', 'find records where', 'search for',
        'maximum', 'minimum', 'median', 'total',
        'group by', 'order by', 'sort by',
        'top ', 'bottom ', 'highest', 'lowest',
        'greater than', 'less than', 'between',
        'statistics', 'distribution', 'frequency',
        'chart', 'graph', 'visualization', 'plot',
        'filter by', 'where ', 'calculate'
    ]

    # Check if query explicitly needs data calculation/filtering
    if any(keyword in question_lower for keyword in sql_required_keywords):
        logger.info(f"SQL query keywords detected - using SQL workflow")
        return True

    # Default: For ambiguous queries with uploaded data, use direct chat
    # This gives more natural responses and users can be more specific if they need SQL
    logger.info("Ambiguous query with uploaded data - using direct chat mode")
    return False


def execute_workflow(question: str, conversation_id: int, table_list: List[str], llm_model: Optional[str] = "gpt-4o-mini", system_db: Optional[DB] = None, db_url: Optional[str] = None):

    # Initialize db variable
    db: DB


    # Case 1: Use system_db if provided
    if db_url is None:
        logger.info("Using existing DB Connection")
        db = system_db
    # Case 2: Use db_url if provided
    elif db_url is not None:
        logger.info("Creating new SYSTEM DB connection")
        db = DB(db_url)
    else:
        raise ValueError("Either system_db or db_url must be provided")


    # Use the new centralized configuration with automatic fallback
    llm = llm_instance.get_model(llm_model, fallback=True)
    schema = db.get_schemas(table_names=table_list)

    workflow = WorkflowManager(llm, db)
    app = workflow.create_workflow().compile()

    # Define a generator to stream the data from LangGraph
    def event_stream():
        ai_responses = []
        try:
            for event in app.stream({"question": question, "schema": schema}):
                for value in event.values():
                    ai_responses.append(json.dumps(value))
                    # Yield the streamed data as a JSON object
                    yield json.dumps({"data": value}) + "\n"

            # After streaming is complete, save all responses as one message
            try:
                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=json.dumps({"answer":ai_responses}),
                    db=system_db
                )
            except SQLAlchemyError as e:
                logger.error(
                    f"Database error occurred while saving message: {str(e)}")
                yield json.dumps({"error": str(e)}) + "\n"

            except Exception as e:
                logger.error(f"Error occurred while saving message: {str(e)}")
                yield json.dumps({"error": str(e)}) + "\n"

        except Exception as e:
            logger.error(f"Error occurred during streaming: {str(e)}")
            yield json.dumps({"error": str(e)}) + "\n"
        finally:
            # Clean up resources
            if app.stream and hasattr(app.stream, 'close'):
                try:
                    app.stream.close()
                except Exception as e:
                    yield json.dumps({"error": str(e)}) + "\n"
                    logger.error(f"Error closing stream: {str(e)}")
    # Return the streaming response using event_stream generator
    return StreamingResponse(event_stream(), media_type="text/event-stream")


def execute_direct_chat(question: str, conversation_id: int, llm_model: Optional[str] = "gpt-4o-mini", system_db: Optional[DB] = None, data_source_info: Optional[dict] = None):
    """
    Execute direct ChatGPT-style response without SQL queries.
    Can include data context for summaries and explanations.

    Args:
        question: The user's question
        conversation_id: ID of the conversation for history tracking
        llm_model: Model name to use (default: gpt-4o-mini)
        system_db: Database instance for saving messages
        data_source_info: Optional dict with data source context (table_name, sample_data, etc.)

    Returns:
        StreamingResponse with ChatGPT response
    """
    try:
        # Get the LLM model
        llm = llm_instance.get_model(llm_model, fallback=True)
        logger.info(f"Using direct chat mode with model: {llm_model}")

        # Fetch conversation history for context
        conversation_history = []
        if system_db and conversation_id:
            try:
                with system_db.session() as session:
                    query = (
                        select(Messages.role, Messages.content)
                        .where(Messages.conversation_id == conversation_id)
                        .order_by(Messages.created_at.asc())
                        .limit(10)  # Last 10 messages for context
                    )
                    results = session.execute(query).all()

                    for role, content in results:
                        if isinstance(content, dict):
                            # Extract question or answer from content
                            if 'question' in content:
                                conversation_history.append({
                                    "role": "user",
                                    "content": content['question']
                                })
                            elif 'answer' in content:
                                # Try to get the last answer if it's a list
                                answer = content['answer']
                                if isinstance(answer, list) and len(answer) > 0:
                                    # Get the last item and extract text if it's JSON
                                    last_answer = answer[-1]
                                    if isinstance(last_answer, str):
                                        try:
                                            parsed = json.loads(last_answer)
                                            if 'answer' in parsed:
                                                conversation_history.append({
                                                    "role": "assistant",
                                                    "content": parsed['answer']
                                                })
                                        except:
                                            pass
                                else:
                                    conversation_history.append({
                                        "role": "assistant",
                                        "content": str(answer)
                                    })
                            else:
                                # Plain content
                                conversation_history.append({
                                    "role": role,
                                    "content": str(content)
                                })
                        elif isinstance(content, str):
                            conversation_history.append({
                                "role": role,
                                "content": content
                            })
            except Exception as e:
                logger.warning(f"Could not fetch conversation history: {str(e)}")

        # Build messages for the LLM
        # If data source info is provided, create a data-aware system prompt
        if data_source_info:
            system_content = f"""You are an expert data analyst assistant. The user has uploaded a dataset and wants to understand it.

Dataset Information:
- File/Source: {data_source_info.get('name', 'Unknown')}
- Table: {data_source_info.get('table_name', 'N/A')}

{data_source_info.get('data_preview', '')}

Provide clear, comprehensive explanations about the data. Use markdown formatting for better readability:
- Use **bold** for emphasis
- Use bullet points for lists
- Use headers (##) for sections
- Be conversational and helpful

Focus on explaining WHAT the data represents and WHY it matters, not just technical details.
Do NOT write SQL queries unless specifically asked. Provide natural language explanations."""
        else:
            system_content = "You are a helpful AI assistant. Provide clear, comprehensive, and well-structured responses using markdown formatting. Be concise but thorough."

        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })

        # Define a generator to stream the response
        def event_stream():
            try:
                # Get response from LLM
                response = llm.invoke(messages)

                # Extract content from response
                if hasattr(response, 'content'):
                    answer = response.content
                else:
                    answer = str(response)

                # Format response in same structure as workflow for frontend compatibility
                result = {
                    "answer": answer,
                    "mode": "direct_chat",
                    "model_used": llm_model
                }

                # Yield the response
                yield json.dumps({"data": result}) + "\n"

                # Save the response to database
                if system_db and conversation_id:
                    try:
                        save_message(
                            conversation_id=conversation_id,
                            role="assistant",
                            content={"answer": answer, "mode": "direct_chat"},
                            db=system_db
                        )
                    except SQLAlchemyError as e:
                        logger.error(f"Database error while saving message: {str(e)}")
                        yield json.dumps({"error": str(e)}) + "\n"

            except Exception as e:
                logger.error(f"Error during direct chat: {str(e)}")
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error initializing direct chat: {str(e)}")

        def error_stream():
            yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")


def serialize_document(doc):
    """Helper function to serialize a Document object"""
    return {
        "page_content": doc.page_content,
        "metadata": doc.metadata
    }


# DISABLED: This function uses deprecated RetrievalQA which is not available
# PDF/Text document analysis is not integrated in frontend yet anyway
def execute_document_chat(question: str, embedding_model: str, table_name: str):
    """
    CURRENTLY DISABLED - Uses deprecated langchain RetrievalQA
    This feature is not integrated in the frontend yet according to README
    """
    raise NotImplementedError("Document chat feature is currently disabled due to dependency issues")

# ORIGINAL COMMENTED OUT CODE BELOW:
#     try:
#         # Initialize embedding
#         vectorDB_instance.initialize_embedding(embedding_model)
#
#         # Get vector store
#         vector_store = vectorDB_instance.get_vector_store(table_name)
#
#         # Initialize LLM
#         llm = llm_instance.openai("gpt-4o-mini")
#
#         # Create a prompt template
#         prompt_template = """You are Lumin, an advanced data analysis assistant, analyze the following context to answer the question. Follow these guidelines:
#
#         1. Use only the information provided in the context.
#         2. If the context doesn't contain enough information, state that clearly.
#         3. Provide data-driven insights when possible.
#         4. Be concise but comprehensive in your response.
#         5. If applicable, mention any trends, patterns, or anomalies in the data.
#
#         Context:
#         {context}
#
#         Question: {question}
#
#         Analysis:
#         """
#
#         PROMPT = PromptTemplate(
#             template=prompt_template, input_variables=["context", "question"]
#         )
#
#         # Create a RetrievalQA chain
#         qa = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
#             return_source_documents=True,
#             chain_type_kwargs={"prompt": PROMPT}
#         )
#
#         # Execute the chain
#         result = qa({"query": question})
#
#         # Serialize the source documents
#         serialized_docs = [serialize_document(
#             doc) for doc in result.get('source_documents', [])]
#
#         return JSONResponse(status_code=200, content={
#             "answer": result['result'],
#             "source_documents": serialized_docs
#         })
#
#     except Exception as e:
#         print(f"Error in simple_document_chat: {str(e)}")
#         raise ValueError(f"Failed to execute document chat: {str(e)}")


def save_message(conversation_id: int, role: str, content: JSON, db: DB):
    try:
        with db.session() as session:
            # Create DataSources entry
            new_data_source = Messages(
                conversation_id=conversation_id,
                role=role,
                content=content,
            )

            session.add(new_data_source)
            session.commit()
            session.refresh(new_data_source)

        return {
            "id": new_data_source.id,
            "role": new_data_source.role
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "message": "Database error occurred",
            "error": str(e)
        })
    except Exception as e:
        # Catch all other errors and raise HTTP exception
        logger.error(f"Something went wrong: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "message": "Database error occurred",
            "error": str(e)
        })