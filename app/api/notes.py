"""
Notes API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..core.security import get_current_user
from ..models.note import Note, NoteCreate, NoteUpdate, NoteList
from ..services.note_service_optimized import optimized_note_service as note_service

router = APIRouter(prefix="/notes", tags=["notes"], redirect_slashes=False)


@router.post("", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new note.
    
    Args:
        note_data: Note creation data
        current_user: Current authenticated user
        
    Returns:
        Note: Created note
        
    Raises:
        HTTPException: If note creation fails
    """
    try:
        note = await note_service.create_note(note_data, current_user["uid"])
        print(f"🔵 [API] Created note response: {note.dict()}")
        return note
    except Exception as e:
        print(f"🔴 [API] Create note error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note"
        )


@router.get("", response_model=List[Note])
async def get_notes(
    include_deleted: bool = Query(False, description="Include deleted notes"),
    limit: int = Query(20, ge=1, le=100, description="Number of notes to return"),
    offset: int = Query(0, ge=0, description="Number of notes to skip"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all notes for the current user.
    
    Args:
        include_deleted: Whether to include deleted notes
        limit: Maximum number of notes to return
        offset: Number of notes to skip
        current_user: Current authenticated user
        
    Returns:
        List[Note]: List of user's notes
        
    Raises:
        HTTPException: If notes retrieval fails
    """
    try:
        notes = await note_service.get_notes(
            current_user["uid"], 
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notes"
        )


@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific note by ID.
    
    Args:
        note_id: ID of the note to retrieve
        current_user: Current authenticated user
        
    Returns:
        Note: The requested note
        
    Raises:
        HTTPException: If note is not found or doesn't belong to user
    """
    try:
        note = await note_service.get_note(note_id, current_user["uid"])
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve note"
        )


@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a note.
    
    Args:
        note_id: ID of the note to update
        note_data: Updated note data
        current_user: Current authenticated user
        
    Returns:
        Note: Updated note
        
    Raises:
        HTTPException: If note is not found or doesn't belong to user
    """
    try:
        note = await note_service.update_note(note_id, note_data, current_user["uid"])
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note"
        )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Soft delete a note.
    
    Args:
        note_id: ID of the note to delete
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If note is not found or doesn't belong to user
    """
    try:
        success = await note_service.delete_note(note_id, current_user["uid"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note"
        )


# Note: Restore functionality removed to align with case study requirements
# Case study only requires: GET /notes, POST /notes, PUT /notes/{id}, DELETE /notes/{id}
