from app.rerank.reranker import Reranker
    
def compute_similarity_scores(reranker: Reranker, orig_query: str, doc_contents: list[str], normalize: bool = True, verbose: bool=False):
    string_pairs = [[orig_query, doc_content] for doc_content in doc_contents]
    scores = reranker.model.compute_score(string_pairs, normalize=normalize)
    results = [{'doc_content': doc_content, 'score': score} for doc_content, score in zip(doc_contents, scores)]
    
    if verbose ==True:
        print('=== Similarity scores ===')
        print(f'Original query:{orig_query}')
        print('***      Scores       ***')
        for i, result in enumerate(results):
            print(f"[{i}] content: {result['doc_content']}; score: {result['score']}")
    
    return results

def filter_low_score_docs(results: list[dict], threshold: float):
    filtered_results = [result for result in results if result['score'] >= threshold]
    return filtered_results