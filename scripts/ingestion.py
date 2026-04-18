from src.config import DATA_DIR
from src.ingestion import DocumentLoader


def main():
    loader = DocumentLoader()
    chunks = loader.load_dir(DATA_DIR)

    print(f"\n✅ {len(chunks)} chunks prêts à être indexés\n")
    print("📋 Aperçu du premier chunk :")
    print(f"  Source  : {chunks[0].metadata.get('source')}")
    print(f"  Page    : {chunks[0].metadata.get('page')}")
    print(f"  Chunk ID: {chunks[0].metadata.get('chunk_id')}")
    print(f"  Content : {chunks[0].page_content[:150]}...")


if __name__ == "__main__":
    main()