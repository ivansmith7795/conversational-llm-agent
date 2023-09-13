import os
import json

import re
import uuid
import logging
import boto3
from botocore.exceptions import ClientError

from pathlib import Path
from typing import Optional, List, Mapping, Any

from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from llama_index import LLMPredictor
from llama_index import LangchainEmbedding
from llama_index import ServiceContext
from llama_index import PromptHelper
from llama_index import GPTVectorStoreIndex

from llama_index.node_parser import SimpleNodeParser
from llama_index.schema import MetadataMode
from langchain.llms.base import LLM
from langchain.embeddings import LlamaCppEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Get the constants from environment vars
AWS_REGION = os.environ['AWS_REGION']
AWS_ACCOUNT = os.environ['AWS_ACCOUNT']
S3_SOURCE_DOCUMENTS_BUCKET = os.environ['S3_SOURCE_DOCUMENTS_BUCKET']
S3_INDEX_STORE_BUCKET = os.environ['S3_INDEX_STORE_BUCKET']
SAGEMAKER_MODEL_ENDPOINT_NAME = os.environ['SAGEMAKER_MODEL_ENDPOINT_NAME']

# AWS_REGION = "us-east-1"
# AWS_ACCOUNT = "413034898429"
# S3_SOURCE_DOCUMENTS_BUCKET = "conversational-bot-source-documents-413034898429-us-east-1"
# S3_INDEX_STORE_BUCKET = "conversational-bot-index-store-413034898429-us-east-1"
# SAGEMAKER_MODEL_ENDPOINT_NAME = "model"

LOCAL_INDEX_LOC = "/tmp/index_files"

def lambda_handler(event, context):
    
    s3_resource = boto3.resource('s3')
    
    download_dir(resource=s3_resource, dist='', local='/tmp/documents', bucket=S3_SOURCE_DOCUMENTS_BUCKET)
    create_vector_embeddings(s3_resource.meta.client)

    logger.info("Index successfully created")
    return

def download_dir(resource, dist, local='/tmp/documents', bucket=S3_SOURCE_DOCUMENTS_BUCKET):
    """
    Download files from the source S3 bucket
    """
    paginator = resource.meta.client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(resource, subdir.get('Prefix'), local, bucket)
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(local, file.get('Key'))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            if not file.get('Key').endswith('/'):
                resource.meta.client.download_file(bucket, file.get('Key'), dest_pathname)


def create_vector_embeddings(s3_client):

    documents = SimpleDirectoryReader('/tmp/documents').load_data()
    print(len(documents))

    # define prompt helper
    max_input_size = 400  # set maximum input size
    num_output = 50  # set number of output tokens
    max_chunk_overlap = 0  # set maximum chunk overlap
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    llm_predictor = LLMPredictor(llm=CustomLLM())
    embed_model = LangchainEmbedding(HuggingFaceEmbeddings(cache_folder="/tmp/HF_CACHE"))
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper, embed_model=embed_model,
    )

    index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
    index.storage_context.persist(persist_dir=LOCAL_INDEX_LOC)

    for file in os.listdir(LOCAL_INDEX_LOC):
        s3_client.upload_file(LOCAL_INDEX_LOC+"/"+file, S3_INDEX_STORE_BUCKET, file)
 
    logger.info("Index successfully created")
    return


def call_sagemaker(prompt, endpoint_name=SAGEMAKER_MODEL_ENDPOINT_NAME):
    payload = {
        "inputs": prompt,
        "parameters": {
            "do_sample": False,
            # "top_p": 0.9,
            "temperature": 0.1,
            "max_new_tokens": 200,
            "repetition_penalty": 1.03,
            "stop": ["\nUser:", "<|endoftext|>", "</s>"]
        }
    }

    sagemaker_client = boto3.client("sagemaker-runtime")
    payload = json.dumps(payload)
    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=payload
    )
    response_string = response["Body"].read().decode()
    return response_string


def get_response_sagemaker_inference(prompt, endpoint_name=SAGEMAKER_MODEL_ENDPOINT_NAME):
    resp = call_sagemaker(prompt, endpoint_name)
    resp = json.loads(resp)[0]["generated_text"][len(prompt):]
    return resp

def main():
    """
    Test the function when called from the commandline.
    """
    
    lambda_handler({}, {})


class CustomLLM(LLM):
    model_name = SAGEMAKER_MODEL_ENDPOINT_NAME

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = get_response_sagemaker_inference(prompt, SAGEMAKER_MODEL_ENDPOINT_NAME)
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "custom"
    
if __name__ == '__main__':
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_ACCOUNT"] = "413034898429"
    os.environ["S3_SOURCE_DOCUMENTS_BUCKET"] = "conversational-bot-source-documents-413034898429-us-east-1"
    os.environ["SAGEMAKER_MODEL_ENDPOINT_NAME"] = "model"
    main()

