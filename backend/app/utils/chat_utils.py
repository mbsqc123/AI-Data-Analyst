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


    llm = llm_instance.openai(llm_model)
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