import os
from llama_index.core import get_response_synthesizer
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from .build_index import load_env_file, get_models


class QueryEngineSingleton:
    _instance = None
    _index = None
    _query_engine = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QueryEngineSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._index is None and self._query_engine is None:
            self._initialize()

    def _initialize(self):
        # Load environment variables
        load_env_file("/usr/local/stage3technical/var/sand/property-rag-search/.env")
        embedding_model, generation_llm = get_models()
        Settings.embed_model = embedding_model
        Settings.llm = generation_llm

        # Load index
        print("Creating storage context from", os.environ["persist_dir"])
        storage_context = StorageContext.from_defaults(
            persist_dir=os.environ["persist_dir"]
        )
        owner_index = load_index_from_storage(storage_context=storage_context)

        # Initialize query engine
        base_retriever = owner_index.as_retriever(similarity_top_k=20)
        auto_merge_retriever = AutoMergingRetriever(
            base_retriever, storage_context, verbose=False
        )

        response_synthesizer = get_response_synthesizer(
            llm=generation_llm,
            response_mode="compact",
        )
        self._query_engine = RetrieverQueryEngine.from_args(
            retriever=auto_merge_retriever,
            llm=generation_llm,
            response_synthesizer=response_synthesizer,
        )

        # Store index and storage context for potential future use
        self._index = owner_index

    def query(self, query_text):
        if self._query_engine is None:
            raise RuntimeError("Query engine is not initialized.")
        return self._query_engine.query(query_text)


def main():
    import logging
    import sys

    # logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # Test singleton query engine
    query_engine_instance = QueryEngineSingleton()
    query_list = [
        ("What properties are owned by 'Smith'"),
        ("What properties are owned by 'Smeeth'"),
        ("What properties are owned by 'Smithes'"),
    ]

    for query_str in query_list:
        response = query_engine_instance.query(query_str)
        print(f"Query: {query_str}")
        print(str(response))
        print("*" * 50)


if __name__ == "__main__":
    main()
