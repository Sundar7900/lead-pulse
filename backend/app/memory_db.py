"""Memory-based database fallback for development without MongoDB."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


class InMemoryDB:
    """Simple in-memory database for development testing."""
    
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            "leads": [],
            "activities": [],
            "alerts": [],
            "users": []
        }
    
    def get_collection(self, name: str):
        return InMemoryCollection(self.collections[name])
    
    def list_collection_names(self) -> List[str]:
        return list(self.collections.keys())
    
    def create_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = []


class InMemoryCollection:
    """In-memory collection that mimics MongoDB collection behavior."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data
    
    def insert_one(self, document: Dict[str, Any]) -> Any:
        """Insert a single document."""
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        document["createdAt"] = datetime.utcnow()
        document["updatedAt"] = datetime.utcnow()
        self._data.append(document)
        
        class Result:
            inserted_id = document["_id"]
        
        return Result()
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> Any:
        """Insert multiple documents."""
        inserted_ids = []
        for doc in documents:
            if "_id" not in doc:
                doc["_id"] = str(uuid.uuid4())
            doc["createdAt"] = datetime.utcnow()
            doc["updatedAt"] = datetime.utcnow()
            self._data.append(doc)
            inserted_ids.append(doc["_id"])
        
        class Result:
            inserted_ids = inserted_ids
        
        return Result()
    
    def find(self, query: Dict[str, Any] = None) -> "InMemoryCursor":
        """Find documents matching query."""
        query = query or {}
        results = []
        for doc in self._data:
            if self._matches(doc, query):
                results.append(doc.copy())
        return InMemoryCursor(results)
    
    def find_one(self, query: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        query = query or {}
        for doc in self._data:
            if self._matches(doc, query):
                return doc.copy()
        return None
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """Update a single document."""
        for i, doc in enumerate(self._data):
            if self._matches(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])
                elif "$inc" in update:
                    for key, val in update["$inc"].items():
                        doc[key] = doc.get(key, 0) + val
                doc["updatedAt"] = datetime.utcnow()
                self._data[i] = doc
                
                class Result:
                    modified_count = 1
                    matched_count = 1
                
                return Result()
        
        class EmptyResult:
            modified_count = 0
            matched_count = 0
        
        return EmptyResult()
    
    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """Update multiple documents."""
        matched = 0
        for i, doc in enumerate(self._data):
            if self._matches(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])
                doc["updatedAt"] = datetime.utcnow()
                self._data[i] = doc
                matched += 1
        
        class Result:
            modified_count = matched
            matched_count = matched
        
        return Result()
    
    def delete_one(self, query: Dict[str, Any]) -> Any:
        """Delete a single document."""
        for i, doc in enumerate(self._data):
            if self._matches(doc, query):
                del self._data[i]
                
                class Result:
                    deleted_count = 1
                
                return Result()
        
        class EmptyResult:
            deleted_count = 0
        
        return EmptyResult()
    
    def count_documents(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching query."""
        query = query or {}
        count = 0
        for doc in self._data:
            if self._matches(doc, query):
                count += 1
        return count
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple aggregation pipeline implementation."""
        results = [doc.copy() for doc in self._data]
        
        for stage in pipeline:
            if "$match" in stage:
                match_query = stage["$match"]
                results = [doc for doc in results if self._matches(doc, match_query)]
            elif "$group" in stage:
                group_spec = stage["$group"]
                group_field = group_spec.get("_id")
                if isinstance(group_field, str) and group_field.startswith("$"):
                    group_key_name = group_field[1:]
                else:
                    group_key_name = group_field
                
                accumulations = {}
                for doc in results:
                    val = doc.get(group_key_name) if group_key_name else None
                    if val not in accumulations:
                        accumulations[val] = {"_id": val}
                        for field in group_spec:
                            if field != "_id":
                                accumulations[val][field] = 0
                    
                    for field, op in group_spec.items():
                        if field == "_id":
                            continue
                        if isinstance(op, dict) and "$sum" in op:
                            sum_spec = op["$sum"]
                            if isinstance(sum_spec, (int, float)):
                                accumulations[val][field] += sum_spec
                            elif isinstance(sum_spec, str) and sum_spec.startswith("$"):
                                doc_val = doc.get(sum_spec[1:], 0)
                                if isinstance(doc_val, (int, float)):
                                    accumulations[val][field] += doc_val
                
                results = list(accumulations.values())
        
        return results
    
    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query."""
        for key, value in query.items():
            if key == "_id":
                if doc.get("_id") != value:
                    return False
            elif key == "status":
                if doc.get("status") not in (value if isinstance(value, list) else [value]):
                    return False
            elif key == "priority":
                if doc.get("priority") != value:
                    return False
            elif key == "assignedTo":
                if doc.get("assignedTo") != value:
                    return False
            elif key == "type":
                if doc.get("type") != value:
                    return False
            elif key == "isRead":
                if doc.get("isRead") != value:
                    return False
            elif isinstance(value, dict):
                doc_val = doc.get(key)
                if "$in" in value:
                    if doc_val not in value["$in"]:
                        return False
                elif "$nin" in value:
                    if doc_val in value["$nin"]:
                        return False
                elif "$gt" in value:
                    if doc_val is None or doc_val <= value["$gt"]:
                        return False
                elif "$lt" in value:
                    if doc_val is None or doc_val >= value["$lt"]:
                        return False
                elif "$gte" in value:
                    if doc_val is None or doc_val < value["$gte"]:
                        return False
                elif "$lte" in value:
                    if doc_val is None or doc_val > value["$lte"]:
                        return False
            else:
                if doc.get(key) != value:
                    return False
        return True


class InMemoryCursor:
    """Cursor for iterating over results."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data
        self._skip = 0
        self._limit = 0
    
    def skip(self, count: int) -> "InMemoryCursor":
        self._skip = count
        return self
    
    def limit(self, count: int) -> "InMemoryCursor":
        self._limit = count
        return self
    
    def sort(self, key: str, direction: int = 1) -> "InMemoryCursor":
        reverse = direction == -1
        def sort_key(x):
            v = x.get(key)
            if v is None:
                return (0, "")
            if isinstance(v, (int, float)):
                return (1, v)
            if isinstance(v, datetime):
                return (2, v.isoformat())
            return (3, str(v))
        self._data.sort(key=sort_key, reverse=reverse)
        return self
    
    def list(self) -> List[Dict[str, Any]]:
        if self._limit > 0:
            return self._data[self._skip:self._skip + self._limit]
        return self._data[self._skip:]
    
    def __iter__(self):
        return iter(self.list())
    
    def __len__(self):
        return len(self._data)


# Global memory database instance
memory_db = InMemoryDB()
