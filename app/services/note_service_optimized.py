"""
High-performance note service with caching and connection pooling.
Optimized for 1M+ users with async operations and Redis caching.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
import logging

from ..core.database import firestore_service
from ..core.cache import cache_service
from ..models.note import Note, NoteCreate, NoteUpdate


class OptimizedNoteService:
    """High-performance service class for note operations with caching."""
    
    async def create_note(self, note_data: NoteCreate, user_id: str) -> Note:
        """
        Create a new note in user's notes subcollection with caching.
        """
        try:
            # Generate note ID (using timestamp for simplicity)
            note_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow()
            
            # Create note data for Firestore (no need for user_id in subcollection)
            note_data_dict = {
                "title": note_data.title,
                "content": note_data.content,
                "is_deleted": False,
                "is_pinned": note_data.is_pinned,
                "format": note_data.format,
                "color": note_data.color,
                "created_at": now,
                "updated_at": now
            }
            
            # Create note in user's notes subcollection
            created_note = await firestore_service.create_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id,
                data=note_data_dict
            )
            
            # Convert to response model
            note = Note(
                id=created_note["id"],
                title=created_note["title"],
                content=created_note["content"],
                is_deleted=created_note["is_deleted"],
                is_pinned=created_note.get("is_pinned", False),
                format=created_note.get("format", "text"),
                color=created_note.get("color", "primary"),
                user_id=user_id,  # Use the provided user_id
                created_at=created_note["created_at"],
                updated_at=created_note["updated_at"]
            )
            
            # Debug: Log the note data
            logging.info(f"Created note: {note.dict()}")
            
            # Cache the new note
            await cache_service.set_note(note.dict())
            
            # Invalidate user's notes list cache
            await cache_service.invalidate_user_notes(user_id)
            
            # Increment notes count in cache
            await cache_service.increment_notes_count(user_id, include_deleted=False)
            
            return note
            
        except Exception as e:
            logging.error(f"Error creating note: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to create note. Please check your input and try again. Error: {str(e)}"
            )
    
    async def get_note(self, note_id: str, user_id: str) -> Optional[Note]:
        """
        Get a note by ID from user's notes subcollection with caching.
        """
        try:
            # Try cache first
            cached_note = await cache_service.get_note(note_id, user_id)
            if cached_note:
                return Note(**cached_note)
            
            # If not in cache, get from user's notes subcollection
            note_data = await firestore_service.get_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id
            )
            
            # Security check: Ensure note exists (already secured by subcollection structure)
            if not note_data:
                logging.warning(f"Note {note_id} not found for user {user_id}")
                return None
            
            note = Note(
                id=note_data["id"],
                title=note_data["title"],
                content=note_data["content"],
                is_deleted=note_data["is_deleted"],
                is_pinned=note_data.get("is_pinned", False),
                format=note_data.get("format", "text"),
                color=note_data.get("color", "primary"),
                user_id=user_id,  # Use the provided user_id
                created_at=note_data["created_at"],
                updated_at=note_data["updated_at"]
            )
            
            # Cache the note
            await cache_service.set_note(note.dict())
            
            return note
            
        except Exception as e:
            logging.error(f"Error getting note: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to retrieve note. Please try again later. Error: {str(e)}"
            )
    
    async def get_notes(
        self,
        user_id: str,
        include_deleted: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Note]:
        """
        Get notes for a user from their notes subcollection with caching and pagination.
        """
        try:
            # Try cache first
            cached_notes = await cache_service.get_notes(user_id, include_deleted, limit, offset)
            if cached_notes:
                return [Note(**note_data) for note_data in cached_notes]
            
            # If not in cache, get from user's notes subcollection
            # Security: Data isolation is automatic with subcollection structure
            filters = []
            if not include_deleted:
                filters.append(("is_deleted", "==", False))
            
            # Query without order_by to avoid composite index requirement
            note_data_list = await firestore_service.query_subcollection(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                filters=filters,
                limit=limit + offset  # We'll handle offset manually
            )
            
            # Sort manually by updated_at
            note_data_list.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
            
            # Apply offset manually (Firestore doesn't support offset directly)
            if offset > 0:
                note_data_list = note_data_list[offset:]
            
            # Apply limit
            note_data_list = note_data_list[:limit]
            
            notes = [
                Note(
                    id=note_data["id"],
                    title=note_data["title"],
                    content=note_data["content"],
                    is_deleted=note_data["is_deleted"],
                    is_pinned=note_data.get("is_pinned", False),
                    format=note_data.get("format", "text"),
                    color=note_data.get("color", "primary"),
                    user_id=user_id,  # Use the provided user_id
                    created_at=note_data["created_at"],
                    updated_at=note_data["updated_at"]
                )
                for note_data in note_data_list
            ]
            
            # Cache the notes list
            await cache_service.set_notes(
                user_id, 
                [note.dict() for note in notes], 
                include_deleted, 
                limit, 
                offset
            )
            
            return notes
            
        except Exception as e:
            logging.error(f"Error getting notes: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to retrieve your notes. Please check your connection and try again. Error: {str(e)}"
            )
    
    async def get_notes_count(self, user_id: str, include_deleted: bool = False) -> int:
        """
        Get total count of notes in user's notes subcollection with caching.
        """
        try:
            # Try cache first
            cached_count = await cache_service.get_notes_count(user_id, include_deleted)
            if cached_count is not None:
                return cached_count
            
            # If not in cache, get from user's notes subcollection
            filters = []
            if not include_deleted:
                filters.append(("is_deleted", "==", False))
            
            note_data_list = await firestore_service.query_subcollection(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                filters=filters
            )
            
            count = len(note_data_list)
            
            # Cache the count
            await cache_service.set_notes_count(user_id, count, include_deleted)
            
            return count
            
        except Exception as e:
            logging.error(f"Error getting notes count: {e}")
            return 0
    
    async def update_note(
        self,
        note_id: str,
        note_data: NoteUpdate,
        user_id: str
    ) -> Optional[Note]:
        """
        Update a note in user's notes subcollection with cache invalidation.
        """
        try:
            # Security check: First verify note exists in user's subcollection
            existing_note = await firestore_service.get_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id
            )
            if not existing_note:
                logging.warning(f"Update attempt on non-existent note {note_id} by user {user_id}")
                return None
            
            # Prepare update data
            update_data = {"updated_at": datetime.utcnow()}
            if note_data.title is not None:
                update_data["title"] = note_data.title
            if note_data.content is not None:
                update_data["content"] = note_data.content
            if note_data.is_deleted is not None:
                update_data["is_deleted"] = note_data.is_deleted
            if note_data.is_pinned is not None:
                update_data["is_pinned"] = note_data.is_pinned
            if note_data.format is not None:
                update_data["format"] = note_data.format
            if note_data.color is not None:
                update_data["color"] = note_data.color
            
            # Update note in user's notes subcollection
            updated_note_data = await firestore_service.update_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id,
                data=update_data
            )
            
            if not updated_note_data:
                return None
            
            note = Note(
                id=updated_note_data["id"],
                title=updated_note_data["title"],
                content=updated_note_data["content"],
                is_deleted=updated_note_data["is_deleted"],
                is_pinned=updated_note_data.get("is_pinned", False),
                format=updated_note_data.get("format", "text"),
                color=updated_note_data.get("color", "primary"),
                user_id=user_id,  # Use the provided user_id
                created_at=updated_note_data["created_at"],
                updated_at=updated_note_data["updated_at"]
            )
            
            # Update cache
            await cache_service.set_note(note.dict())
            
            # Invalidate user's notes list cache
            await cache_service.invalidate_user_notes(user_id)
            
            return note
            
        except Exception as e:
            logging.error(f"Error updating note: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to update note. Please check your input and try again. Error: {str(e)}"
            )
    
    async def delete_note(self, note_id: str, user_id: str) -> bool:
        """
        Soft delete a note in user's notes subcollection with cache invalidation.
        """
        try:
            # Security check: First verify note exists in user's subcollection
            existing_note = await firestore_service.get_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id
            )
            if not existing_note:
                logging.warning(f"Delete attempt on non-existent note {note_id} by user {user_id}")
                return False
            
            # Soft delete by updating is_deleted field
            update_data = {
                "is_deleted": True,
                "updated_at": datetime.utcnow()
            }
            
            success = await firestore_service.update_subcollection_document(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                subdocument_id=note_id,
                data=update_data
            )
            
            if success:
                # Invalidate caches
                await cache_service.invalidate_note(note_id, user_id)
                await cache_service.invalidate_user_notes(user_id)
                
                # Decrement notes count in cache
                await cache_service.increment_notes_count(user_id, include_deleted=False, increment=-1)
                await cache_service.increment_notes_count(user_id, include_deleted=True, increment=1)
            
            return bool(success)
            
        except Exception as e:
            logging.error(f"Error deleting note: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to delete note. Please try again later. Error: {str(e)}"
            )
    
    # Note: restore_note method removed to align with case study requirements
    # Case study only requires: GET /notes, POST /notes, PUT /notes/{id}, DELETE /notes/{id}
    
    async def search_notes(
        self,
        user_id: str,
        search_term: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Note]:
        """
        Search notes in user's notes subcollection with full-text search.
        """
        try:
            # Get all notes from user's subcollection and filter by search term
            # Note: Firestore doesn't support full-text search natively
            # This is a simple implementation - for production, consider using Algolia or Elasticsearch
            note_data_list = await firestore_service.query_subcollection(
                collection_name="users",
                document_id=user_id,
                subcollection_name="notes",
                filters=[("is_deleted", "==", False)]
            )
            
            # Sort manually by updated_at
            note_data_list.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
            
            # Filter by search term (case-insensitive)
            search_term_lower = search_term.lower()
            filtered_notes = [
                note_data for note_data in note_data_list
                if (search_term_lower in note_data.get("title", "").lower() or
                    search_term_lower in note_data.get("content", "").lower())
            ]
            
            # Apply offset and limit
            if offset > 0:
                filtered_notes = filtered_notes[offset:]
            filtered_notes = filtered_notes[:limit]
            
            return [
                Note(
                    id=note_data["id"],
                    title=note_data["title"],
                    content=note_data["content"],
                    is_deleted=note_data["is_deleted"],
                    is_pinned=note_data.get("is_pinned", False),
                    format=note_data.get("format", "text"),
                    color=note_data.get("color", "primary"),
                    user_id=user_id,
                    created_at=note_data["created_at"],
                    updated_at=note_data["updated_at"]
                )
                for note_data in filtered_notes
            ]
            
        except Exception as e:
            logging.error(f"Error searching notes: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search notes"
            )


# Global optimized note service instance
optimized_note_service = OptimizedNoteService()
