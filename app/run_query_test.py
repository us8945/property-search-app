"""
Run the query engine with a sample query.
"""

from indexes.index_query import QueryEngineSingleton
from utilities.custom_logger import logger


def main():
    # Test singleton query engine
    query_engine_instance = QueryEngineSingleton()
    query_list = [
        ("What properties are owned by 'Smith'"),
        ("What properties are owned by 'Smeeth'"),
        ("What properties are owned by 'Smithes'"),
    ]
    logger.info("Starting Tests...")
    for query_str in query_list:
        logger.info("*" * 50)
        response = query_engine_instance.query(query_str)
        logger.info(f"Query: {query_str}")
        logger.info("Response:.......")
        logger.info(str(response))
        logger.info("*" * 50)


if __name__ == "__main__":
    main()
