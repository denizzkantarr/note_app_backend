"""
Firebase Firestore database configuration and utilities.
"""
import firebase_admin
from firebase_admin import firestore
from typing import Optional, Dict, Any, List
import logging

from .config import settings

# Initialize Firestore client
try:
    if not firebase_admin._apps:
        cred = firebase_admin.credentials.Certificate(settings.firebase_credentials)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
except Exception as e:
    logging.error(f"Failed to initialize Firestore client: {e}")
    db = None


class FirestoreService:
    """Service class for Firestore operations."""
    
    def __init__(self):
        self.db = db
    
    async def get_collection(self, collection_name: str) -> firestore.CollectionReference:
        """Get a Firestore collection reference."""
        if not self.db:
            raise Exception("Firestore client not initialized")
        return self.db.collection(collection_name)
    
    async def get_document(self, collection_name: str, document_id: str) -> firestore.DocumentReference:
        """Get a Firestore document reference."""
        if not self.db:
            raise Exception("Firestore client not initialized")
        return self.db.collection(collection_name).document(document_id)
    
    async def create_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document in Firestore."""
        try:
            doc_ref = await self.get_document(collection_name, document_id)
            doc_ref.set(data)
            return {"id": document_id, **data}
        except Exception as e:
            logging.error(f"Error creating document: {e}")
            raise
    
    async def get_document_data(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document data from Firestore."""
        try:
            doc_ref = await self.get_document(collection_name, document_id)
            doc = doc_ref.get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logging.error(f"Error getting document: {e}")
            raise
    
    async def update_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in Firestore."""
        try:
            doc_ref = await self.get_document(collection_name, document_id)
            doc_ref.update(data)
            updated_doc = await self.get_document_data(collection_name, document_id)
            return updated_doc
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            raise
    
    async def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from Firestore."""
        try:
            doc_ref = await self.get_document(collection_name, document_id)
            doc_ref.delete()
            return True
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            raise
    
    async def query_collection(self, collection_name: str, filters: List[tuple] = None, order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query a collection with optional filters."""
        try:
            collection = await self.get_collection(collection_name)
            query = collection
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logging.error(f"Error querying collection: {e}")
            raise

    async def get_subcollection(self, collection_name: str, document_id: str, subcollection_name: str) -> firestore.CollectionReference:
        """Get a Firestore subcollection reference."""
        if not self.db:
            raise Exception("Firestore client not initialized")
        return self.db.collection(collection_name).document(document_id).collection(subcollection_name)
    
    async def create_subcollection_document(self, collection_name: str, document_id: str, subcollection_name: str, subdocument_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document in a subcollection."""
        try:
            subcollection = await self.get_subcollection(collection_name, document_id, subcollection_name)
            doc_ref = subcollection.document(subdocument_id)
            doc_ref.set(data)
            return {"id": subdocument_id, **data}
        except Exception as e:
            logging.error(f"Error creating subcollection document: {e}")
            raise
    
    async def get_subcollection_document(self, collection_name: str, document_id: str, subcollection_name: str, subdocument_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from a subcollection."""
        try:
            subcollection = await self.get_subcollection(collection_name, document_id, subcollection_name)
            doc_ref = subcollection.document(subdocument_id)
            doc = doc_ref.get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logging.error(f"Error getting subcollection document: {e}")
            raise
    
    async def update_subcollection_document(self, collection_name: str, document_id: str, subcollection_name: str, subdocument_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in a subcollection."""
        try:
            subcollection = await self.get_subcollection(collection_name, document_id, subcollection_name)
            doc_ref = subcollection.document(subdocument_id)
            doc_ref.update(data)
            updated_doc = await self.get_subcollection_document(collection_name, document_id, subcollection_name, subdocument_id)
            return updated_doc
        except Exception as e:
            logging.error(f"Error updating subcollection document: {e}")
            raise
    
    async def delete_subcollection_document(self, collection_name: str, document_id: str, subcollection_name: str, subdocument_id: str) -> bool:
        """Delete a document from a subcollection."""
        try:
            subcollection = await self.get_subcollection(collection_name, document_id, subcollection_name)
            doc_ref = subcollection.document(subdocument_id)
            doc_ref.delete()
            return True
        except Exception as e:
            logging.error(f"Error deleting subcollection document: {e}")
            raise
    
    async def query_subcollection(self, collection_name: str, document_id: str, subcollection_name: str, filters: List[tuple] = None, order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query a subcollection with optional filters."""
        try:
            subcollection = await self.get_subcollection(collection_name, document_id, subcollection_name)
            query = subcollection
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logging.error(f"Error querying subcollection: {e}")
            raise


# Global Firestore service instance
firestore_service = FirestoreService()
