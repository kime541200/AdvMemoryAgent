import chromadb
from sentence_transformers import SentenceTransformer

class VecDBClient():
    def __init__(self,
                 name: str,
                 embed_model: str,
                 device: str) -> None:
        self.name = name
        self.vecdb_client = chromadb.Client()

        self.device = device
        self.embed_model = self._initial_embed_model(embed_model)

    def _initial_embed_model(self, model_path: str):
        return SentenceTransformer(model_path, device=self.device)

    def create_vector_db(self, conversations):
        try:
            self.vecdb_client.delete_collection(name=self.name)
        except ValueError:
            pass 

        vector_db = self.vecdb_client.create_collection(name=self.name)

        for c in conversations:
            indexing_convo = f"prompt: {c['prompt']} response: {c['response']}"
            embedding = self.embed_model.encode(indexing_convo, normalize_embeddings=True)

            vector_db.add(
                ids=[str(c['id'])],
                embeddings=embedding.tolist(),
                documents=[indexing_convo]
            )

    def retrieve_embeddings(self, query, n_results: int = 1, top_k_result: int = 1):
        if n_results < 1:
            return ""

        if top_k_result < 1:
            top_k_result = 1

        prompt_embedding = self.embed_model.encode(query, normalize_embeddings=True)
        vector_db=self.vecdb_client.get_collection(name=self.name)
        results = vector_db.query(query_embeddings=prompt_embedding.tolist(), n_results=n_results)

        retrieve_docs = []
        ids_list = results['ids'][0]
        docs_list = results['documents'][0]
        for i in range(len(ids_list)):
            item = {'id': ids_list[i], 'document': docs_list[i]}
            retrieve_docs.append(item)

        return retrieve_docs