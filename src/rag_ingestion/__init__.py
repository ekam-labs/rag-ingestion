"""Public API for the RAG ingestion package."""

# The implementation module/class retain their original spelling for
# compatibility; export the correctly spelled public API used by callers.
from .ingestion import RAGIngestion

__all__ = ["RAGIngestion"]
