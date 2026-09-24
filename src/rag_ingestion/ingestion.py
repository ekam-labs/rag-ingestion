import tiktoken
from pathlib import Path
from typing import Any, Sequence
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    UnstructuredExcelLoader
) 

class RAGIngestion:
    """Identify uploaded files and extract their content."""
    LOADERS = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".xlsx": UnstructuredExcelLoader
    }

    def __init__(
              self,
              tokenizer: Any | None = None,
              max_tokens: int | None = None,
              strict: bool = False,
              text_splitter: Any | None = None,
              chunk_size: int = 1000,
              chunk_overlap: int = 200,
              clean: bool = True
    ) -> None:
         
         """
        Initialize the ingestion pipeline.

        Args:
            tokenizer:
                Optional tokenizer. If omitted, the default tiktoken
                encoding is used when token counting is required.

            max_tokens:
                Maximum number of tokens to process. None means unlimited.

            strict:
                If True, raise an exception when a file cannot be processed.
                If False, skip unsupported/failed files.

            text_splitter:
                Optional custom LangChain text splitter.

            chunk_size:
                Default chunk size.

            chunk_overlap:
                Default chunk overlap.

            clean:
                If True, clean documents before chunking.      
         """
         
         self.max_tokens = max_tokens
         self.strict = strict
         self.tokenizer = tokenizer or tiktoken.get_encoding("cl100k_base")

         self.text_splitter = text_splitter or RecursiveCharacterTextSplitter(
             chunk_size=chunk_size,
             chunk_overlap=chunk_overlap
         )
         self.clean_enabled = clean

    def load(
              self, 
              files: str | Path | Sequence[str | Path]
              ) -> dict:
         """
        Load one or multiple files and extract their content.

        Args:
            files:
                A single file path or a list of file paths.

        Returns:
            Dictionary containing:
                documents:
                    Extracted LangChain Document objects.

                total_tokens:
                    Total number of extracted tokens.

                files_processed:
                    Number of successfully processed files.
        """
         if isinstance(files, (str, Path)):
            files = [files]

         documents = []
         total_tokens = 0
         files_processed = 0   

         for file in files:
             file_path = Path(file)
             extension = file_path.suffix.lower()

             if extension not in self.LOADERS:
                 if self.strict:
                     raise ValueError(
                         f"Unsupported file type: {extension}"
                         )
                 continue

             try:
                 loader = self.LOADERS[extension](str(file_path))
                 file_documents = loader.load()
                 file_tokens = sum(len(self.tokenizer.encode(document.page_content))for document in file_documents) 
                 if (
                     self.max_tokens is not None and
                     total_tokens + file_tokens > self.max_tokens
                 ):
                     break

                 documents.extend(file_documents)
                 total_tokens += file_tokens
                 files_processed += 1
             except Exception:
                 if self.strict:
                     raise 
                     
         return {
             "documents": documents,
             "total_tokens": total_tokens,
             "files_processed": files_processed
         }   

    def clean(self, documents: list[Document]) -> list[Document]:
        """Perform basic cleaning while preserving document metadata."""
        cleaned_documents = []

        for document in documents:
            text = document.page_content
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            lines = [line.strip() for line in text.split("\n")]
            text = "\n".join(line for line in lines if line).strip()

            if not text:
                continue

            cleaned_documents.append(
                Document(
                    page_content=text,
                    metadata=document.metadata.copy()
                )
            )

        return cleaned_documents
        
    def chunk(
            self, 
            documents: list[Document],
            text_splitter: Any | None = None,
            ) -> list[Document]:
        """Split documents using a LangChain text splitter."""

        if self.clean_enabled:
            documents = self.clean(documents)

        splitter = text_splitter or self.text_splitter

        return splitter.split_documents(documents)            