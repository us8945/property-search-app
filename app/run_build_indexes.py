"""
Run this script to build indexes for the app.
"""

import os
from dotenv import find_dotenv
from llama_index.core import Settings

from utilities.custom_logger import logger
from indexes.build_index import (
    get_nodes,
    build_docstore_index,
    load_env_file,
    get_models,
)


def main():
    logger.info("Start Job to build indexes")
    load_env_file(find_dotenv())
    logger.info("Starting index build...")
    embedding_model, generation_llm = get_models()
    Settings.embed_model = embedding_model
    Settings.llm = generation_llm
    data_path = os.getenv("data_path")
    property_file = os.getenv("property_file")
    property_file_path = os.path.join(data_path, property_file)
    full_nodes, owner_nodes, all_nodes = get_nodes(property_file_path)
    build_docstore_index(owner_nodes=owner_nodes, all_nodes=all_nodes)
    logger.info("Index built")


if __name__ == "__main__":
    main()
