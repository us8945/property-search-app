"""
This module provides a singleton class `QueryEngineSingleton` that initializes and manages a query engine for the application.
The query engine is responsible for loading environment variables, models, and indexes, and performing queries using a retriever
and response synthesizer.

Classes:
    QueryEngineSingleton: A singleton class that initializes and manages the query engine.

Functions:
    __new__(cls, *args, **kwargs): Ensures only one instance of the class is created.
    __init__(self): Initializes the query engine if it is not already initialized.
    _initialize(self): Loads environment variables, models, and indexes, and sets up the query engine.
    query(self, query_text: str) -> Any: Executes a query using the initialized query engine.
"""

import os
from dotenv import find_dotenv
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import get_response_synthesizer
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from .build_index import load_env_file, get_models

from utilities.custom_logger import logger


class QueryEngineSingleton:
    _instance = None
    _index = None
    _query_engine = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QueryEngineSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._index is None and self._query_engine is None:
            logger.info("Initializing QueryEngineSingleton")
            self._initialize()

    def _initialize(self):
        # Load environment variables
        load_env_file(find_dotenv())
        embedding_model, generation_llm = get_models()
        Settings.embed_model = embedding_model
        Settings.llm = generation_llm
        persist_dir = os.getenv("persist_dir")
        if not persist_dir:
            raise EnvironmentError("Environment variable 'persist_dir' is not set.")

        # Load index
        logger.info(f"Creating storage context from : {persist_dir}")

        # Define Index and Vector Store
        vector_store = FaissVectorStore.from_persist_dir(persist_dir)

        # Define storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=persist_dir
        )
        # Load Index from Storage
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

    def query(self, query_text: str) -> str:
        if self._query_engine is None:
            raise RuntimeError("Query engine is not initialized.")
        return self._query_engine.query(query_text)
