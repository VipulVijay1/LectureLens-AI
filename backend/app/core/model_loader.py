from sentence_transformers import SentenceTransformer, CrossEncoder


class ModelLoader:
    def __init__(self):
        self.embedding_model = None
        self.reranker = None

    def load_models(self):
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Loading cross-encoder model...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        print("Models loaded successfully.")


# Singleton instance
model_loader = ModelLoader()
