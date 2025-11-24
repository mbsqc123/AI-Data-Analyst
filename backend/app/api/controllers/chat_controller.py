from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, and_, text
from sqlalchemy.orm import aliased
from app.utils.chat_utils import (
    execute_workflow, execute_document_chat, save_message)
from app.api.validators.chat_validator import AskQuestion, InitiateCinversaction
from app.config.db_config import DB
from app.config.logging_config import get_logger
from app.api.db.data_sources import DataSources
from app.api.db.chat_history import (Conversations, Messages)
from datetime import datetime
from app.utils.response_utils import create_response
from app.config.llm_config import get_available_models, get_model_info, validate_model
import json

# Set up logging
logger = get_logger(__name__)


async def ask_question(id: int, body: AskQuestion, db: DB):
    try:
        with db.session() as session:
            data_source = session.execute(select(DataSources).where(
                DataSources.id == body.dataset_id)).scalar_one_or_none()

            if not data_source:
                raise HTTPException(status_code=404, detail=create_response(
                    status_code=404,
                    message="Data source not found",
                    data={}
                ))

        save_message(
            conversation_id=body.conversaction_id,
            role="user",
            content={"question": body.question},
            db=db
        )

        if body.type == "url":
            return execute_workflow(
                question=body.question,
                conversation_id=body.conversaction_id,
                db_url=data_source.connection_url,
                table_list=body.selected_tables,
                system_db=db,
                llm_model=body.llm_model
            )
        elif body.type == "spreadsheet":
            return execute_workflow(
                question=body.question,
                conversation_id=body.conversaction_id,
                table_list=[data_source.table_name],
                system_db=db,
                llm_model=body.llm_model
            )
        else:
            print("execure_document_chat")
            return execute_document_chat(
                body.question, "text-embedding-3-large", "speech_81a36223")

    except HTTPException as he:
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="Something went wrong",
            data={"error": str(he)}
        ))

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="Database error occurred",
            data={"error": str(e)}
        ))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="An unexpected error occurred",
            data={"error": str(e)}
        ))


def initiate_convesactions(user_id: int, body: InitiateCinversaction, db: DB):
    try:
        with db.session() as session:
            data_source = session.execute(select(DataSources).where(
                DataSources.id == body.data_source_id)).scalar_one_or_none()

            # Generate name
            current_time = datetime.now()
            formatted_date = current_time.strftime("%Y %b %d %H:%M").lower()
            combined_name = f"{data_source.name} {formatted_date}"

            # Create DataSources entry
            new_data_source = Conversations(
                user_id=user_id,
                data_source_id=data_source.id,
                title=combined_name,
            )

            session.add(new_data_source)
            session.commit()
            session.refresh(new_data_source)

        return JSONResponse(status_code=200, content=create_response(
            status_code=200,
            message="Conversaction initiated",
            data={
                "conversaction_id": new_data_source.id,
                "conversaction_title": new_data_source.title,
                "data_source_id": new_data_source.data_source_id,
            }
        ))

    except HTTPException as he:
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="Something went wrong",
            data={"error": str(he)}
        ))

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="Database error occurred",
            data={"error": str(e)}
        ))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content=create_response(
            status_code=500,
            message="An unexpected error occurred",
            data={"error": str(e)}
        ))


def get_convesactions(user_id: int, db: DB):
    try:
        with db.session() as session:
            # Create a subquery to get first message for each conversation
            first_messages_subquery = (
                select(
                    Messages.conversation_id,
                    Messages.content,
                    func.row_number().over(
                        partition_by=Messages.conversation_id,
                        order_by=Messages.created_at
                    ).label('rn')
                )
                .where(Messages.role == 'user')
                .subquery()
            )

            # Filter for only the first message (rn = 1)
            first_message = aliased(first_messages_subquery)

            # Main query combining conversations and their first messages
            query = (
                select(
                    Conversations.id,
                    first_message.c.content.label('title'),
                    func.to_char(Conversations.created_at,
                                 'YYYY-MM-DD').label('created_at')
                )
                .outerjoin(
                    first_message,
                    and_(
                        Conversations.id == first_message.c.conversation_id,
                        first_message.c.rn == 1
                    )
                )
                .where(Conversations.user_id == user_id)
                .order_by(Conversations.created_at.desc())
            )

            result = session.execute(query).mappings().all()

            conversations_list = []
            for row in result:
                conv_dict = dict(row)

                # Process the title from the message content
                content = conv_dict['title']

                if content:
                    if isinstance(content, dict) and 'question' in content:
                        title = str(content['question'])[:100]
                    else:
                        title = str(content)[:100]
                else:
                    title = "Untitled Conversation"

                conversations_list.append({
                    'id': conv_dict['id'],
                    'title': title,
                    'created_at': conv_dict['created_at']
                })

            return JSONResponse(
                status_code=200,
                content=create_response(
                    status_code=200,
                    message="Conversations fetched successfully",
                    data={"conversations": conversations_list}
                )
            )
    except HTTPException as he:
        logger.error(f"HTTP error: {str(he)}")
        return JSONResponse(
            status_code=he.status_code,
            content=create_response(
                status_code=he.status_code,
                message="Request failed",
                data={"error": str(he)}
            )
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="Database error occurred",
                data={"error": str(e)}
            )
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="An unexpected error occurred",
                data={"error": str(e)}
            )
        )


def get_conversaction_history(conversaction_id: int, db: DB):
    try:
        with db.session() as session:
            query = (
                select(
                    Messages.id,
                    Messages.role,
                    Messages.content,
                    func.to_char(Messages.created_at,
                                 'YYYY-MM-DD HH24:MI:SS').label('created_at'),
                    func.to_char(Messages.updated_at,
                                 'YYYY-MM-DD HH24:MI:SS').label('updated_at')
                )
                .where(Messages.conversation_id == conversaction_id)
                .order_by(Messages.created_at.asc())
            )

            result = session.execute(query).mappings().all()

            messages = []
            for row in result:
                message_dict = dict(row)

                # Ensure content is JSON serializable
                content = message_dict['content']
                if isinstance(content, str):
                    try:
                        message_dict['content'] = json.loads(content)
                    except json.JSONDecodeError:
                        message_dict['content'] = content

                messages.append(message_dict)

            return JSONResponse(
                status_code=200,
                content=create_response(
                    status_code=200,
                    message="Messages fetched successfully",
                    data={"messages": messages}
                )
            )

    except HTTPException as he:
        logger.error(f"HTTP error: {str(he)}")
        return JSONResponse(
            status_code=he.status_code,
            content=create_response(
                status_code=he.status_code,
                message="Request failed",
                data={"error": str(he)}
            )
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="Database error occurred",
                data={"error": str(e)}
            )
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="An unexpected error occurred",
                data={"error": str(e)}
            )
        )


def get_available_llm_models():
    """
    Get a list of all available LLM models with their metadata.

    Returns:
        JSONResponse with list of models and their details
    """
    try:
        models = get_available_models()
        return JSONResponse(
            status_code=200,
            content=create_response(
                status_code=200,
                message="Available models fetched successfully",
                data={"models": models}
            )
        )
    except Exception as e:
        logger.error(f"Error fetching available models: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="Failed to fetch available models",
                data={"error": str(e)}
            )
        )


def get_llm_model_info(model_name: str):
    """
    Get detailed information about a specific LLM model.

    Args:
        model_name: Name of the model to get info for

    Returns:
        JSONResponse with model details or error
    """
    try:
        model_info = get_model_info(model_name)

        if model_info is None:
            return JSONResponse(
                status_code=404,
                content=create_response(
                    status_code=404,
                    message=f"Model '{model_name}' not found",
                    data={}
                )
            )

        return JSONResponse(
            status_code=200,
            content=create_response(
                status_code=200,
                message="Model info fetched successfully",
                data={"model": model_info}
            )
        )
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_response(
                status_code=500,
                message="Failed to fetch model info",
                data={"error": str(e)}
            )
        )
