import os
import logging

from FlagEmbedding import FlagReranker

class Reranker():
    def __init__(
        self,
        device: str,
        reranker_model_path: str,
        threshold: float = 0.05,
        use_fp16: bool = True,
        normalize: bool = True,
    ):
        self.device = device
        self.reranker_model_path = reranker_model_path
        self.threshold=threshold
        self.use_fp16 = use_fp16
        self.normalize= normalize

        self.model = self._load_rerank_model()

    def _load_rerank_model(self):
        return FlagReranker(self.reranker_model_path, 
                            use_fp16=self.use_fp16,
                            device=self.device)