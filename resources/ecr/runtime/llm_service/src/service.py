import boto3
from botocore.exceptions import ClientError, ValidationError

from flask import Flask, abort, request
import flask

import logging
import json
import os
from typing import Optional, List, Mapping, Any
from langchain.llms.base import LLM
from llama_index import (
    LangchainEmbedding,
    PromptHelper,
    ResponseSynthesizer,
    LLMPredictor,
    ServiceContext,
    Prompt,
)

from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever
from llama_index.vector_stores.types import VectorStoreQueryMode
from llama_index import StorageContext, load_index_from_storage

s3_client = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SAGEMAKER_MODEL_ENDPOINT_NAME = os.environ['SAGEMAKER_MODEL_ENDPOINT_NAME']
# ERROR_RESPONSE = "I'm sorry, an error occured while processing the request. Please try again later."
# OUT_OF_DOMAIN_RESPONSE = "I'm sorry, but I am only able to give responses regarding the source topic"
# INDEX_WRITE_LOCATION = "/tmp/index"
# DEFAULT_ACCOUNT = os.environ['DEFAULT_ACCOUNT']
# S3_INDEX_STORE_BUCKET = os.environ['S3_INDEX_STORE_BUCKET']
# RETRIEVAL_THRESHOLD = 0.1

SAGEMAKER_MODEL_ENDPOINT_NAME = "jumpstart-dft-meta-textgeneration-llama-2-7b-f"
OUT_OF_DOMAIN_RESPONSE = "I'm sorry, but I am only able to give responses regarding the source topic"
ERROR_RESPONSE = "I'm sorry, an error occured while processing the request. Please try again later."
INDEX_WRITE_LOCATION = "/tmp/index"
DEFAULT_ACCOUNT = "413034898429"
S3_INDEX_STORE_BUCKET = "conversational-bot-index-store-413034898429-us-east-1"
RETRIEVAL_THRESHOLD = 0.1


def call_sagemaker(prompt, endpoint_name=SAGEMAKER_MODEL_ENDPOINT_NAME):
    print("Prompt")
    print(prompt)
    payload = {
        "inputs": [
            [
                {"role": "user", "content": str(prompt)}
            ]
        ],
        "parameters": {
            "do_sample": False,
            # "top_p": 0.9,
            "temperature": 0.1,
            "max_new_tokens": 200,
            "repetition_penalty": 1.03
        }
    }

    sagemaker_client = boto3.client("sagemaker-runtime")
    custom_attributes = "accept_eula=true"
    payload = json.dumps(payload)
    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=payload,
        CustomAttributes=custom_attributes
    )
    response_string = response["Body"].read().decode()
    return response_string


def get_response_sagemaker_inference(prompt, endpoint_name=SAGEMAKER_MODEL_ENDPOINT_NAME):
    resp = call_sagemaker(prompt, endpoint_name)
    print("Response:")
    print(resp)

    resp = json.loads(resp)[0]["generation"]["content"]
    return resp


class CustomLLM(LLM):
    model_name = SAGEMAKER_MODEL_ENDPOINT_NAME

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = get_response_sagemaker_inference(
            prompt, SAGEMAKER_MODEL_ENDPOINT_NAME)
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "custom"


print("Initiating runtime...")
# define prompt helper
max_input_size = 400  # set maximum input size
num_output = 50  # set number of output tokens
max_chunk_overlap = 0  # set maximum chunk overlap
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

application = app = Flask(__name__)
# define our LLM
llm_predictor = LLMPredictor(llm=CustomLLM())
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(cache_folder="/tmp/HF_CACHE"))
service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor, prompt_helper=prompt_helper, embed_model=embed_model,
)

# Download index here
print("Downloading index...")
if not os.path.exists(INDEX_WRITE_LOCATION):
    os.mkdir(INDEX_WRITE_LOCATION)
try:
    s3_client.download_file(
        S3_INDEX_STORE_BUCKET, "docstore.json", INDEX_WRITE_LOCATION + "/docstore.json")
    s3_client.download_file(
        S3_INDEX_STORE_BUCKET, "index_store.json", INDEX_WRITE_LOCATION + "/index_store.json")
    s3_client.download_file(S3_INDEX_STORE_BUCKET, "vector_store.json",
                            INDEX_WRITE_LOCATION + "/vector_store.json")

    # load index
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_WRITE_LOCATION)
    index = load_index_from_storage(
        storage_context, service_context=service_context)
    logger.info("Index successfully loaded")
except ClientError as e:
    logger.error(e)
    print("ERROR LOADING/READING INDEX")

retriever = VectorIndexRetriever(
    service_context=service_context,
    index=index,
    similarity_top_k=5,
    vector_store_query_mode=VectorStoreQueryMode.DEFAULT,
    alpha=0.5,
)

# configure response synthesizer
synth = ResponseSynthesizer.from_args(
    response_mode="simple_summarize",
    service_context=service_context
)


@app.route('/', methods=['GET'])
def heartbeat():
    return "<html><body>Alive and well!</body></html>"


@app.route('/predict', methods=['GET'])
def query_llm():

    query = request.args.get('query')
    if not query:
        logging.error("An invalid request was submitted to the API.")
        abort(400)

    logging.info("Processing new request: " + query)

    input_text = query

    print("Query:")
    print(query)

    query_engine = RetrieverQueryEngine(
        retriever=retriever, response_synthesizer=synth)
    query_input = query

    try:
        answer = query_engine.query(query_input)
        print("Score:")
        print(str(answer.source_nodes[0].score))

        if answer.source_nodes[0].score < RETRIEVAL_THRESHOLD:
            answer = OUT_OF_DOMAIN_RESPONSE
    except ValidationError as e:
        print(str(e))
        answer = ERROR_RESPONSE

    print("Text Answer:")
    print(answer)

    json_answer = {'response': str(answer)}

    jsonified_resp = json.loads(json.dumps(json_answer, default=str))
    return jsonified_resp


def initialize_cache():
    if not os.path.exists("/tmp/TRANSFORMERS_CACHE"):
        os.mkdir("/tmp/TRANSFORMERS_CACHE")

    if not os.path.exists("/tmp/HF_CACHE"):
        os.mkdir("/tmp/HF_CACHE")


def main():
    # app.run(debug=False, use_reloader=False)
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=8080)


if __name__ == '__main__':
    main()
