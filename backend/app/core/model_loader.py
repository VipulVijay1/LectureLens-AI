from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch


class ModelLoader:
    def __init__(self):
        self.embedding_model = None
        self.reranker = None
        self.generator_tokenizer = None
        self.generator_model = None

    def load_models(self):
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Loading cross-encoder model...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        print("Loading generative model...")
        self.generator_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.generator_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

        print("Models loaded successfully.")


model_loader = ModelLoader()