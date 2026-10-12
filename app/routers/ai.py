from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services.ai_service import query_ollama_with_context

router = APIRouter(
    prefix="/api/ai",
    tags=["Ollama AI Extension"]
)


@router.post(
    "/query",
    response_model=schemas.AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask natural language questions about student database records"
)
async def ask_ai_question(
    query_in: schemas.AIQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Answers natural language questions (e.g. 'How many students are enrolled?', 'List students born after 2005.')
    by retrieving grounded SQLite database records as context for the local Ollama LLM.
    """
    # Build safe, grounded database context
    context = crud.get_database_summary_context(db)

    # Execute Ollama query with grounded context
    result = await query_ollama_with_context(
        question=query_in.question,
        context=context,
        model_name=query_in.model or "llama3.2:1b"
    )

    return schemas.AIQueryResponse(
        question=query_in.question,
        answer=result["answer"],
        context_used=context,
        model_used=result["model_used"],
        ollama_status=result["status"]
    )
