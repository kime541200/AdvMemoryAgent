import yaml
import asyncio
from tqdm import tqdm
from colorama import Fore
from config.config import Settings
from app.sql_processing.utils import fetch_conversations, store_conversations, remove_last_conversation
from app.vecdb.VecDBClient import VecDBClient
from app.chatting.LLMClient import LLMClient
from app.chatting.utils.multi_query import generate_multi_query
from app.rerank.reranker import Reranker
from app.rerank.utils.utils import compute_similarity_scores, filter_low_score_docs

def load_configs(config_file_path: str):
    with open(config_file_path, 'r', encoding='utf-8') as file:
        yaml_config = yaml.safe_load(file)
    settings = Settings(**yaml_config)
    if settings.system.chat_verbose == True:
        print(f"Running on device: {settings.system.device}")
        print(settings)    
    return settings

def recall(llm_client: LLMClient, vecdb: VecDBClient, reranker: Reranker, query: str, verbose: bool) -> str:
    queries=generate_multi_query(llm_client=llm_client, orig_query=query, query_amount=3, max_retry=5)
    queries.append(query)

    if verbose == True:
        print(Fore.YELLOW + '\n === Multi queries ===')
        [print(Fore.YELLOW + query) for query in queries]
        print(Fore.YELLOW + '======================\n') 

    docs, already_got_ids = [], []
    for query in tqdm(queries, desc='Processing queries to vector databast'):
        retrieve_docs = vecdb.retrieve_embeddings(query=query, n_results=5, top_k_result=3)
        for doc in retrieve_docs:
            if doc['id'] not in already_got_ids:
                already_got_ids.append(doc['id'])
                docs.append(doc['document'])
    
    rerank_result = compute_similarity_scores(reranker=reranker, orig_query=query, doc_contents=docs)
    filtered_results = filter_low_score_docs(results=rerank_result, threshold=reranker.threshold)
    
    context = ""
    for result in filtered_results:
        context = context + '- ' + result['doc_content'] + '\n'

    prompt = f'MEMORIES:\n```\n{context}```\nUSER PROMPT: {query}'
    if verbose == True:
        print(Fore.YELLOW + '\n=== Current prompt ===')
        print(Fore.YELLOW + prompt)
        print(Fore.YELLOW + '======================\n')
    
    return prompt


async def run():
    settings=load_configs(config_file_path='./config/config.yaml')
    print('\n')

    # PostgreSQL database parameters
    DB_PARAMS = {
        'dbname': settings.sql_db.dbname,
        'user': settings.sql_db.user,
        'password': settings.sql_db.password,
        'host': settings.sql_db.host,
        'port': settings.sql_db.port
    }
    conversations = fetch_conversations(DB_PARAMS)
    vecdb = VecDBClient(name=settings.vector_db.name, embed_model=settings.indexing.embed_model, device=settings.system.device)
    vecdb.create_vector_db(conversations=conversations)
    llm_client = LLMClient(host=settings.llm_client.host, model=settings.llm_client.model, keep_alive=settings.llm_client.keep_alive)    
    reranker = Reranker(device=settings.system.device, reranker_model_path=settings.reranker.reranker_model_path, threshold=settings.reranker.rerank_threshold)

    convo = [{'role': 'system', 'content': llm_client.system_prompt}]

    while True:
        query = input(Fore.WHITE + 'USER: \n')
        if query.lower() in ['bye', '/bye']:
            break

        if query[:7].lower() == '/recall':
            query = query[7:]
            prompt = recall(llm_client=llm_client, vecdb=vecdb, reranker=reranker, query=query, verbose=settings.system.chat_verbose)            
        elif query[:7].lower() == '/forget':
            remove_last_conversation(DB_PARAMS=DB_PARAMS)
            convo = convo[:-2]
            print(Fore.LIGHTRED_EX + 'Latest conversation is removed.\n')
            continue
        elif query[:9].lower() == '/memorize':
            query = query[9:]
            store_conversations(DB_PARAMS=DB_PARAMS, prompt=query, response='Memory stored.')
            print(Fore.LIGHTBLUE_EX + 'Memory stored.\n')
            continue
        else:
            prompt = query

        convo.append({'role': 'user', 'content': prompt})
        stream = llm_client.a_ollama_stream(convo)

        print(Fore.LIGHTGREEN_EX + 'ASSISTANT: \n')

        response = ""
        async for part in stream:
            response = response + part['message']['content']
            print(part['message']['content'], end='', flush=True)

        print('\n')

        convo.append({'role': 'assistant', 'content': response})

        if settings.system.store_chat_to_db == True:
            store_conversations(DB_PARAMS=DB_PARAMS, prompt=prompt, response=response)

if __name__ == "__main__":
    asyncio.run(run())