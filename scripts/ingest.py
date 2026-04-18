import argparse
from src.config import DATA_DIR, VECTOR_STORE_DIR
from src.ingestion import DocumentLoader
from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import build_vector_store

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DATA_DIR))
    args = parser.parse_args()

    print(">>> SCRIPT STARTED")

    loader = DocumentLoader()
    chunks = loader.load_dir(args.source)
    print(f"{len(chunks)} chunks loaded")

    print("Generating embeddings and constructing the vector store...")
    embeddings = get_embeddings()
    build_vector_store(embeddings, chunks)
    print(f"Vector store sauvegardé dans {VECTOR_STORE_DIR}")

if __name__ == "__main__":
    main()
