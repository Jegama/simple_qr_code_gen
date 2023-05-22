from llama_index import (
    LLMPredictor,
    ServiceContext,
    ResponseSynthesizer
)
import re
from llama_index.indices.loading import load_index_from_storage
from llama_index import StorageContext
from llama_index.indices.document_summary import DocumentSummaryIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.optimization.optimizer import SentenceEmbeddingOptimizer

from langchain.chat_models import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt, chunk_size_limit=1024)
response_synthesizer = ResponseSynthesizer.from_args()

# personal_index = GPTVectorStoreIndex.load_from_disk('index.json', service_context=service_context)

docid_to_url = pd.read_json('cs_docid_to_url.json', typ='series').to_dict()

# rebuild storage context
print("Loading index from storage...")
cs_storage_context = StorageContext.from_defaults(persist_dir="cs_index")
cs_index = load_index_from_storage(cs_storage_context)
# cs_retriever = DocumentSummaryIndexRetriever(
#     cs_index,
#     service_context=service_context
# )
# cs_query_engine = RetrieverQueryEngine(
#     retriever=cs_retriever,
#     response_synthesizer=response_synthesizer,
# )
cs_query_engine = cs_index.as_query_engine(response_mode="tree_summarize", use_async=True, optimizer=SentenceEmbeddingOptimizer(threshold_cutoff=0.8))

error_storage_context = StorageContext.from_defaults(persist_dir="error_codes_index")
error_codes_index = load_index_from_storage(error_storage_context)
# error_codes_retriever = DocumentSummaryIndexRetriever(
#     error_codes_index,
#     service_context=service_context
# )
# error_codes_query_engine = RetrieverQueryEngine(
#     retriever=error_codes_retriever,
#     response_synthesizer=response_synthesizer,
# )
error_codes_query_engine = error_codes_index.as_query_engine(response_mode="tree_summarize", use_async=True,optimizer=SentenceEmbeddingOptimizer(threshold_cutoff=0.8))

class SourceFormatter:
    def formater(self, response, source_nodes):
        """Get formatted sources text."""
        texts = []
        texts.append(response)
        for source_node in source_nodes[:3]:
            try:
                title = source_node.node.text.split('\n')[0]
            except:
                title = "Not available"
            doc_id = source_node.node.doc_id or "None"
            source_text = f"\nSource:\nConfidence: {source_node.score:.3f}\nTitle: \nURL: <a href=\"{title}\">{docid_to_url[doc_id]}</a>"
            texts.append(source_text)
        return "\n".join(texts)
    
    def query_cs(self, question):
        response = cs_query_engine.query(question)

        return self.formater(response.response, response.source_nodes)
    
    def query_error_codes(self, question):
        response = error_codes_query_engine.query(question)
        return self.formater(response.response, response.source_nodes)
    
    def connect_to_human(self, question):
        return "Please connect with a human agent by going to https://support.roku.com/contactus.\nThank you for using Roku Support. Have a nice day!\n\nAnother alternative is connect with my human by email at jmancilla@roku.com or scheduling a call <a href=\"https://calendly.com/jgmancilla/phonecall\">here</a>."
    
    def audio_guide(self, question):
        return "When the screen reader shortcut is enabled, you can quickly press Star * button on Roku remote four times to turn the screen reader on or off from any screen.\n\nSource <a href=\"https://support.roku.com/article/231584647\">How to enable the text-to-speech screen reader on your Roku® streaming device</a>."


print("Querying...")
formatter = SourceFormatter()
response = formatter.query_cs('How do I pair my remote?')

print(response)