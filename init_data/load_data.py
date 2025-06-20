import psycopg2
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from parsing.parsed_code import load_chunks

DB_NAME = "repo"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

def init_db():
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, host=DB_HOST, port=DB_PORT)
    conn.autocommit = True
    cur = conn.cursor()

    # Create new DB if not
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created.")

    cur.close()
    conn.close()

    # Connect to new DB and enable pgvector
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    cur.close()
    conn.close()
    print("pgvector extension ensured.")

def embed_and_store():
    docs = load_chunks()
    print(f"Loaded {len(docs)} code chunks.")

    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    PGVector.from_documents(
        documents=docs,
        embedding=embedder,
        collection_name="documents",
        connection_string=f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    print("Data embedded and stored in PostgreSQL.")

if __name__ == "__main__":
    init_db()
    embed_and_store()
