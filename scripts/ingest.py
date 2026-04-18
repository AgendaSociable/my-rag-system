import argparse
from pathlib import Path
from src.ingestion.document_loader import DocumentLoader
from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import build_vector_store
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Ingest documents and build vector store.")
    parser.add_argument("--source", type=Path, required=True, help="Directory containing documents to ingest.")
    args = parser.parse_args()
    
    loader = DocumentLoader()
    chunks = loader.load_dir(args.source)
    logger.info(f"Loaded {len(chunks)} document chunks from {args.source}")
    
    embeddings = get_embeddings()
    
    build_vector_store(embeddings, chunks)
    logger.info("Ingestion and vector store building complete.")
    
if __name__ == "__main__":
    main()