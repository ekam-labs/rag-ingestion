# RAG Ingestion

A lightweight document ingestion component for Retrieval-Augmented Generation (RAG) pipelines.

RAG Ingestion handles the initial document-processing stage of a RAG workflow: loading supported files, extracting their content, tracking token usage, cleaning extracted text, and splitting documents into chunks.

The package is designed to work with LangChain `Document` objects and can be used as a standalone component or as part of a larger RAG pipeline.

## Features

* Load multiple documents from file paths
* Support for PDF, DOCX, and XLSX files
* Extract content into LangChain `Document` objects
* Token counting with `tiktoken`
* Optional maximum token budget
* Optional strict error handling
* Basic text cleaning while preserving document metadata
* Configurable LangChain text splitter
* Configurable chunk size and chunk overlap
* Compatible with custom tokenizers and text splitters

## Supported File Types

| File type | Loader                    |
| --------- | ------------------------- |
| `.pdf`    | `PyPDFLoader`             |
| `.docx`   | `Docx2txtLoader`          |
| `.xlsx`   | `UnstructuredExcelLoader` |

## Installation

```bash
pip install rag-ingestion
```

## Basic Usage

```python
from rag_ingestion import RAGIngection

ingestion = RAGIngection()

result = ingestion.load([
    "document.pdf",
    "document.docx",
    "spreadsheet.xlsx",
])

documents = result["documents"]

chunks = ingestion.chunk(documents)
```

The `load()` method returns:

```python
{
    "documents": [...],
    "total_tokens": ...,
    "files_processed": ...
}
```

## Configuration

The ingestion component can be configured with optional parameters:

```python
ingestion = RAGIngection(
    tokenizer=custom_tokenizer,
    max_tokens=4000,
    strict=True,
    chunk_size=1000,
    chunk_overlap=200,
    clean=True,
)
```

### Tokenizer

A custom tokenizer can be supplied when required.

If no tokenizer is provided, the package uses the default `cl100k_base` encoding from `tiktoken`.

### Token Budget

`max_tokens` can be used to limit the total number of extracted tokens processed by the loader.

```python
ingestion = RAGIngection(max_tokens=4000)
```

If no limit is provided, token processing is unlimited.

### Strict Mode

By default, unsupported or failed files are skipped.

To raise an exception instead:

```python
ingestion = RAGIngection(strict=True)
```

### Chunking

Documents can be split using the default recursive character text splitter:

```python
chunks = ingestion.chunk(documents)
```

Chunking can be configured with:

```python
ingestion = RAGIngection(
    chunk_size=1000,
    chunk_overlap=200,
)
```

A custom LangChain text splitter can also be supplied.

## Pipeline

The basic processing flow is:

```text
Files
  ↓
Load & Extract
  ↓
Token Counting
  ↓
Text Cleaning
  ↓
Chunking
  ↓
LangChain Documents
```

The resulting chunks can then be passed to a retrieval system, vector store, hybrid retriever, or another downstream RAG component.

## Dependencies

This package uses components from the LangChain ecosystem together with document loaders and tokenization utilities.

The package dependencies are defined in `pyproject.toml`.

## Status

This is the initial version of the RAG ingestion component, developed as a modular building block for a larger RAG system.

The package is intentionally focused on document ingestion and preprocessing rather than retrieval or generation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
