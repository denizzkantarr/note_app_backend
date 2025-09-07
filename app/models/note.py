"""
Note model for the Notes App.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base note model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    is_pinned: bool = Field(default=False, description="Pin flag")
    format: str = Field(default="text", description="Note format: text, todo, bullet")
    color: str = Field(default="primary", description="Note color: primary, secondary, tertiary")


class NoteCreate(NoteBase):
    """Model for creating a new note."""
    pass


class NoteUpdate(BaseModel):
    """Model for updating an existing note."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, min_length=1, description="Note content")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")
    is_pinned: Optional[bool] = Field(None, description="Pin flag")
    format: Optional[str] = Field(None, description="Note format: text, todo, bullet")
    color: Optional[str] = Field(None, description="Note color: primary, secondary, tertiary")


class NoteInDB(NoteBase):
    """Model for note stored in database."""
    id: str = Field(..., description="Note ID")
    user_id: str = Field(..., description="User ID who owns the note")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class Note(NoteInDB):
    """Model for note response."""
    pass


class NoteList(BaseModel):
    """Model for note list response."""
    notes: list[Note] = Field(..., description="List of notes")
    total: int = Field(..., description="Total number of notes")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Number of notes per page")
