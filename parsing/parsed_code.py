import os
from langchain.schema import Document

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT_DIR, 'mock_data/code_repos')

def load_chunks():
    documents = []

    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(('.cpp', '.h', '.c', '.py')):
                try:
                    full_path = os.path.join(root, file)
                    with open(full_path, 'r', errors='ignore') as f:
                        code = f.read()

                    lines = code.split('\n')
                    chunks = [lines[i:i+200] for i in range(0, len(lines), 200)]

                    for idx, chunk in enumerate(chunks):
                        chunk_text = '\n'.join(chunk)

                        documents.append(
                            Document(
                                page_content=chunk_text,
                                metadata={
                                    "source": "code",
                                    "file": file,
                                    "chunk_id": idx,
                                    "path": os.path.relpath(full_path, ROOT_DIR)
                                }
                            )
                        )
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")

    return documents
