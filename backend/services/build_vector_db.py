import argparse
import hashlib
import logging
import uuid
from typing import List

from services import pgvector_instance  
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from services.config import settings  

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

logger = logging.getLogger(__name__)


def _load_documents() -> List[Document]:
    loader = PyPDFDirectoryLoader(settings.DOCUMENTS_PATH, glob="*.pdf")
    return loader.load()


def _chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    return splitter.split_documents(documents)


def _encode_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _process_chunks() -> List[Document]:
    documents = _load_documents()
    chunks = _chunk_documents(documents)

    current_source = None
    chunk_index = 0

    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")

        if source != current_source:
            logger.info(f"Processing source: {source}")
            current_source = source
            chunk_index = 0
        else:
            chunk_index += 1

        string_index = f"{source}:{page}:{chunk_index}"
        generated_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, string_index)
        chunk.id = str(generated_uuid)
        chunk.metadata.update({
            "index": string_index,
            "hash": _encode_text(chunk.page_content)
        })
        logger.info(f"Processed chunk {i} with hash: {chunk.metadata['hash']}, id: {chunk.metadata['index']}")

    return chunks


def update_database(db: PGVector):
    # Ensure the target collection exists before querying by IDs
    try:
        # Some PGVector versions require explicit collection creation
        if getattr(db, "create_collection", None):
            db.create_collection()
    except Exception as e:
        logger.warning(f"Skipping create_collection (possibly already exists): {e}")

    chunks = _process_chunks()
    chunk_ids = [chunk.id for chunk in chunks]

    existing_docs = []
    batch_size = 100
    for i in range(0, len(chunk_ids), batch_size):
        batch_ids = chunk_ids[i:i + batch_size]

        batch_docs = db.get_by_ids(batch_ids)
        existing_docs.extend(batch_docs)

    existing_docs_by_id = {
        doc.id: doc.metadata
        for doc in existing_docs
    }
    logger.info(f"Found {len(existing_docs)} existing documents that match our chunks ✅")

    new_chunks = []
    updated_chunks = []

    for chunk in chunks:
        chunk_id = chunk.id
        chunk_hash = chunk.metadata["hash"]

        if chunk_id not in existing_docs_by_id:
            new_chunks.append(chunk)
        elif existing_docs_by_id[chunk_id].get("hash") != chunk_hash:
            updated_chunks.append(chunk)

    batch_size = 100

    if new_chunks:
        total_new = len(new_chunks)
        for i in range(0, total_new, batch_size):
            batch = new_chunks[i:i + batch_size]
            logger.info(f"Adding batch of documents {i+1}-{min(i+batch_size, total_new)} of {total_new} ✅")
            db.add_documents(batch, ids=[doc.id for doc in batch])

    if updated_chunks:
        total_updates = len(updated_chunks)
        for i in range(0, total_updates, batch_size):
            batch = updated_chunks[i:i + batch_size]
            logger.info(f"Updating batch of documents {i+1}-{min(i+batch_size, total_updates)} of {total_updates} ✅")
            db.add_documents(batch, ids=[doc.id for doc in batch])

    if not new_chunks and not updated_chunks:
        logger.info("No documents to add or update")


def clear_database() -> None:
    try:
        db = pgvector_instance.get()
        db.delete_collection()
        logger.info("Database cleared successfully ✅")
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)} ❌")
        raise


