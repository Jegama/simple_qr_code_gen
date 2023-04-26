from llama_index import GPTSimpleVectorIndex, download_loader, LangchainEmbedding, LLMPredictor, ServiceContext
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.node_parser import SimpleNodeParser
from llama_index.utils import truncate_text
from langchain import HuggingFacePipeline
import pandas as pd
from dotenv import load_dotenv
import json
load_dotenv()


ReadabilityWebPageReader = download_loader("ReadabilityWebPageReader")
loader = ReadabilityWebPageReader(wait_until="networkidle")

print('\nLoading model...')
repo_id = "stabilityai/stablelm-tuned-alpha-7b"
# repo_id = "databricks/dolly-v2-3b"

stablelm = HuggingFacePipeline.from_model_id(model_id=repo_id, task="text-generation")
embed_model = LangchainEmbedding(HuggingFaceEmbeddings())

llm_predictor = LLMPredictor(llm=stablelm)

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, embed_model=embed_model)

parser = SimpleNodeParser()
index = GPTSimpleVectorIndex([], service_context=service_context)

urls = pd.read_csv('cs_articles.csv')['urls'].tolist()
docid_to_url = {}

print('\nPopulating index...')
for page in urls:
    documents = loader.load_data(url=page)
    nodes = parser.get_nodes_from_documents(documents)
    docid_to_url[nodes[0].doc_id] = page
    index.insert_nodes(nodes)

index.save('cs_index.json')
with open('cs_docid_to_url.json', 'w') as f:
    json.dump(docid_to_url, f)

print('\nTokens used to build index\nTokens used on prediction: ', llm_predictor.last_token_usage)
print('\nTokens used on embedding: ', embed_model.last_token_usage)