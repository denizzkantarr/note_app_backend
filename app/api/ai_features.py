"""
AI Features API endpoints for the Notes App.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.security import get_current_user
from ..services.local_ai_service import local_ai_service as ai_service

router = APIRouter(prefix="/ai", tags=["ai-features"])


class AIRequest(BaseModel):
    """Base AI request model."""
    content: str


class AITitleRequest(AIRequest):
    """Request model for AI title generation."""
    pass


class AISummaryRequest(AIRequest):
    """Request model for AI summary generation."""
    pass


class AIImproveRequest(AIRequest):
    """Request model for AI content improvement."""
    pass


class AIResponse(BaseModel):
    """AI response model."""
    result: str
    success: bool = True


@router.post("/generate-title", response_model=AIResponse)
async def generate_title(
    request: AITitleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a title for note content using AI.
    
    Args:
        request: AI title generation request
        current_user: Current authenticated user
        
    Returns:
        AIResponse: Generated title
        
    Raises:
        HTTPException: If title generation fails
    """
    try:
        title = await ai_service.generate_title(request.content)
        return AIResponse(result=title)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate title: {str(e)}"
        )


@router.post("/summarize", response_model=AIResponse)
async def summarize_content(
    request: AISummaryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Summarize note content using AI.
    
    Args:
        request: AI summary request
        current_user: Current authenticated user
        
    Returns:
        AIResponse: Generated summary
        
    Raises:
        HTTPException: If summarization fails
    """
    try:
        summary = await ai_service.summarize_content(request.content)
        return AIResponse(result=summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize content: {str(e)}"
        )


@router.post("/improve-content", response_model=AIResponse)
async def improve_content(
    request: AIImproveRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Improve note content using AI.
    
    Args:
        request: AI content improvement request
        current_user: Current authenticated user
        
    Returns:
        AIResponse: Improved content
        
    Raises:
        HTTPException: If content improvement fails
    """
    try:
        improved_content = await ai_service.improve_content(request.content)
        return AIResponse(result=improved_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to improve content: {str(e)}"
        )


@router.post("/suggest-tags", response_model=AIResponse)
async def suggest_tags(
    request: AIRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Suggest tags for note content using AI.
    
    Args:
        request: AI tag suggestion request
        current_user: Current authenticated user
        
    Returns:
        AIResponse: Suggested tags
        
    Raises:
        HTTPException: If tag suggestion fails
    """
    try:
        tags = await ai_service.suggest_tags(request.content)
        return AIResponse(result=tags)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suggest tags: {str(e)}"
        )


@router.post("/generate-ideas", response_model=AIResponse)
async def generate_ideas(
    request: AIRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate ideas based on note content using AI.
    
    Args:
        request: AI idea generation request
        current_user: Current authenticated user
        
    Returns:
        AIResponse: Generated ideas
        
    Raises:
        HTTPException: If idea generation fails
    """
    try:
        ideas = await ai_service.generate_ideas(request.content)
        return AIResponse(result=ideas)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ideas: {str(e)}"
        )


@router.post("/test/generate-title", response_model=AIResponse)
async def test_generate_title(request: AIRequest):
    """
    Test endpoint for AI title generation (no authentication required).
    """
    try:
        title = await ai_service.generate_title(request.content)
        return AIResponse(result=title)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate title: {str(e)}"
        )


@router.post("/test/improve-content", response_model=AIResponse)
async def test_improve_content(request: AIRequest):
    """
    Test endpoint for AI content improvement (no authentication required).
    """
    try:
        improved_content = await ai_service.improve_content(request.content)
        return AIResponse(result=improved_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to improve content: {str(e)}"
        )


@router.post("/test/generate-ideas", response_model=AIResponse)
async def test_generate_ideas(request: AIRequest):
    """
    Test endpoint for AI idea generation (no authentication required).
    """
    try:
        ideas = await ai_service.generate_ideas(request.content)
        return AIResponse(result=ideas)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ideas: {str(e)}"
        )
