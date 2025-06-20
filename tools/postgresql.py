from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import urllib.parse
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI


load_dotenv()

class PostgresqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters.get("query")
        if not query:
            raise Exception("Missing query input")

        creds = self.runtime.credentials
        encoded_password = urllib.parse.quote(creds["pg_password"])
        print("CREDS RECEIVED:", creds)
        retriever = PGVector(
            collection_name="documents",
            connection_string=f"postgresql+psycopg2://{creds['pg_user']}:{encoded_password}@{creds['pg_host']}:{creds['pg_port']}/{creds['pg_database']}",
            embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        ).as_retriever(search_kwargs={"k": 2})
        print(f"Query: {query}")

        #llm=OpenAI(model="gpt-4",temperature=0,max_tokens=512)
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, model_name="gpt-4"),
            retriever=retriever
        )

        result = qa_chain.invoke({"query": query})
        print(f"Query: {query}")
        print(f"LLM Response: {result}")

        if "not specified in the provided context" in result.get("result", "").lower():
            yield self.create_text_message("No result returned.")
        else:
            yield self.create_text_message(result.get("result", "No result returned."))



