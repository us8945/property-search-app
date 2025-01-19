import os
import pandas as pd
import faiss

from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import StorageContext

from utilities.custom_logger import logger

# Mapping columns for preprocessing
key_replacements = {
    "propYear": "property year",
    "propID": "property ID",
    "geoID": "geographical ID",
    "propType": "property type",
    "propSubType": "property subtype",
    "propCategoryCode": "property category code",
    "legalDescription": "legal description",
    "dbaName": "doing business as name",
    "propCreateDate": "property creation date",
    "situsBldgNum": "situs building number",
    "situsStreetPrefix": "situs street prefix",
    "situsStreetName": "situs street name",
    "situsStreetSuffix": "situs street suffix",
    "situsUnit": "situs unit",
    "situsCity": "situs city",
    "situsZip": "situs ZIP",
    "situsConcat": "situs concatenated",
    "situsConcatShort": "situs concatenated short",
    "ownerID": "owner ID",
    "ownerName": "owner name",
    "ownerNameAddtl": "owner name additional",
    "ownerAddrLine1": "owner address line 1",
    "ownerAddrLine2": "owner address line 2",
    "ownerAddrCity": "owner address city",
    "ownerAddrState": "owner address state",
    "ownerAddrZip": "owner address ZIP",
    "ownerAddrCountry": "owner address country",
    "taxAgentID": "tax agent ID",
    "taxAgentName": "tax agent name",
    "imprvYearBuilt": "improvement year built",
    "currValYear": "current value year",
    "currValImprv": "current value improvement",
    "currValLand": "current value land",
    "currValMarket": "current value market",
    "currValAgLoss": "current value agriculture loss",
    "currValAppraised": "current value appraised",
}

key_for_search = {
    "propID": "property ID",
    "legalDescription": "legal description",
    "dbaName": "doing business as name",
    "situsBldgNum": "situs building number",
    "situsStreetPrefix": "situs street prefix",
    "situsStreetName": "situs street name",
    "situsStreetSuffix": "situs street suffix",
    "situsUnit": "situs unit",
    "situsCity": "situs city",
    "situsZip": "situs ZIP",
    "situsConcat": "situs concatenated",
    "ownerID": "owner ID",
    "ownerName": "owner name",
    "ownerNameAddtl": "owner name additional",
}


def load_env_file(file_path):
    # Load environment variables from .env file
    variables_to_define = [
        "OPENAI_API_KEY",
        "embeddings_llm",
        "embeddings_cache_folder",
        "data_path",
        "property_file",
        "persist_dir",
        "vector_dim",
    ]
    variables_to_hide = [
        "OPENAI_API_KEY",
    ]
    try:
        with open(file_path, "r") as file:
            for line in file:
                # Remove whitespace and comments
                line = line.strip()
                if line and not line.startswith("#"):
                    # Split by the first '=' character
                    key, value = line.split("=", 1)
                    # Remove any surrounding quotes from the value
                    value = value.strip().strip('"').strip("'")
                    # Set the environment variable
                    if key in variables_to_define:
                        os.environ[key.strip()] = value
                        if key in variables_to_hide:
                            value = "HIDDEN"
                        logger.info(f"Set environment variable: {key.strip()}={value}")

    except FileNotFoundError:
        logger.error(f"Error: {file_path} not found.")
        raise FileNotFoundError
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        raise e


def get_models():
    # Define variables from environment variables
    embeddings_llm = os.getenv("embeddings_llm")
    logger.info(f"embeddings_llm:{embeddings_llm}")
    embeddings_cache_folder = os.getenv("embeddings_cache_folder")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    # Embedding model
    embedding_model = HuggingFaceEmbedding(
        model_name=embeddings_llm,
        cache_folder=embeddings_cache_folder,
        embed_batch_size=32,
    )

    # Generation model
    generation_llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        api_key=openai_api_key,
    )
    return embedding_model, generation_llm


def preprocess_csv(file_path):
    # Specify data types for problematic columns
    dtype_mapping = {
        32: "str",  # Example: Column 32 as string
        49: "str",  # Example: Column 49 as string
    }

    df = pd.read_csv(file_path, dtype=dtype_mapping)
    # df = pd.read_csv(file_path)
    df.rename(columns=key_replacements, inplace=True)
    filtered_df = df[list(key_for_search.values())]
    return df, filtered_df


def convert_to_documents(df):
    return [row.to_dict() for _, row in df.iterrows()]


def get_documents_facts(document: dict):
    facts = ""
    for key, value in document.items():
        facts += f"{key}: {value}\n"
    return facts


def create_node_representation(input_dict):
    # Extract relevant fields
    legal_description = input_dict.get("legal description", "N/A")
    owner_id = input_dict.get("owner ID", "N/A")
    owner_name = input_dict.get("owner name", "N/A")
    owner_name_additional = input_dict.get("owner name additional", "N/A")
    property_id = input_dict.get("property ID", "N/A")
    situs_concatenated = input_dict.get("situs concatenated", "N/A")
    situs_city = input_dict.get("situs city", "N/A")
    situs_zip = input_dict.get("situs ZIP", "N/A")
    dba = input_dict.get("doing business as name", "N/A")

    # Combine owner names if additional owner exists
    if owner_name_additional in ["N/A", "nan"] or pd.isna(owner_name_additional):
        owner_names = owner_name
    else:
        owner_names = f"{owner_name} and {owner_name_additional}"

    # Construct the natural language description
    value = (
        f"This property, located at {situs_concatenated}, is legally described as "
        f"'{legal_description}'. The property ID is {property_id}. "
        f"It is owned by {owner_names}, with an owner ID of {owner_id}. "
    )
    if not (dba == "N/A" or pd.isna(dba)):
        value += f"The property is also known as {dba}."

    # Construct the output dictionary
    output_node = {
        "key": f"Property Information - {situs_concatenated}",
        "value": value,
        "metadata": {
            "property_id": property_id,
            "situs_city": situs_city,
            "situs_zip": situs_zip,
            "owner_name": owner_names,
            "legal_description": legal_description,
        },
    }
    return output_node


def get_nodes(input_file_path):
    df, filtered_df = preprocess_csv(input_file_path)
    documents = convert_to_documents(filtered_df)
    # Limit to 10 for testing
    # documents = documents[:10]
    full_nodes = []
    owner_nodes = []
    all_nodes = []
    node_id = 0
    for document in documents:
        doc_node = create_node_representation(document)
        node_text = f"{doc_node['key']}. {doc_node['value']}"
        node_full = TextNode(
            text=node_text, id_=str(node_id), metadata=doc_node["metadata"]
        )
        node_owner = TextNode(
            text=doc_node["metadata"]["owner_name"],
            id_=str(node_id) + "_owner",
            metadata={
                "owner_name": doc_node["metadata"]["owner_name"],
                "legal_description": doc_node["metadata"]["legal_description"],
            },
        )
        node_full.relationships[NodeRelationship.CHILD] = [
            RelatedNodeInfo(node_id=node_owner.node_id)
        ]
        node_owner.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(
            node_id=node_full.node_id
        )
        node_id += 1
        full_nodes.append(node_full)
        owner_nodes.append(node_owner)
        all_nodes.append(node_full)
        all_nodes.append(node_owner)

    return full_nodes, owner_nodes, all_nodes


def build_docstore_index(owner_nodes, all_nodes):
    # define storage context

    docstore = SimpleDocumentStore()

    # insert nodes into docstore
    docstore.add_documents(all_nodes)

    # Define Index and Vector Store
    vector_dim = int(os.getenv("vector_dim"))
    logger.info(f"Loaded vector dimension from env: {vector_dim}")
    faiss_index = faiss.IndexFlatL2(vector_dim)
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    # define storage context (will include vector store by default too)
    storage_context = StorageContext.from_defaults(
        docstore=docstore, vector_store=vector_store
    )

    # owner_nodes are defined as leaf nodes
    owner_index = VectorStoreIndex(
        nodes=owner_nodes,
        index_name="owner_index",
        show_progress=True,
        insert_batch_size=10000,
        storage_context=storage_context,
    )
    logger.info("Owner index created")

    # Persist the storage context
    owner_index.storage_context.persist(persist_dir=os.getenv("persist_dir"))
    logger.info("Owner index persisted")
