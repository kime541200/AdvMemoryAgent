from typing import Union
import torch

from app.rerank.reranker import Reranker

    
def compute_similarity_scores(reranker: Reranker, orig_query: str, doc_contents: list[str], normalize: bool = True, verbose: bool=False):
    """計算語句對的相似分數

    Args:
        reranker (Union[Reranker, Reranker_LLMBase]): Reranker實體
        orig_query (str): 原始語句(使用者輸入的query或是經由 "multi query"產生的)
        doc_contents (list[str]): 要與原始語句比較相似性的文字
        normalize (bool, optional): 是否將分數正規化成0-1. Defaults to True.

    Returns:
        list[dict]: 返回包含用於比較的文字與其得分的列表 [{"doc_content": "the content", "score": float}]
    """
    # 構建包含所有字串對的列表
    string_pairs = [[orig_query, doc_content] for doc_content in doc_contents]
    # 計算相似性分數
    scores = reranker.model.compute_score(string_pairs, normalize=normalize)
    # 將文本資料和相應的分數配對
    results = [{'doc_content': doc_content, 'score': score} for doc_content, score in zip(doc_contents, scores)]
    
    if verbose ==True:
        print('=== Similarity scores ===')
        print(f'Original query:{orig_query}')
        print('***      Scores       ***')
        for i, result in enumerate(results):
            print(f"[{i}] content: {result['doc_content']}; score: {result['score']}")
    
    return results

def filter_low_score_docs(results: list[dict], threshold: float):
    """篩選出分數高於閾值的文本資料

    Args:
        results (list[dict]): `def compute_similarity_scores()`所得到的結果
        threshold (float): 閥值

    Returns:
        list[dict]: 將從`def compute_similarity_scores()`所得到的結果去掉分數低於特定閥值後的結果
    """
    filtered_results = [result for result in results if result['score'] >= threshold]
    return filtered_results