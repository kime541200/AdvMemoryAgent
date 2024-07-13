import json
from tqdm import tqdm
from colorama import Fore
from pydantic import BaseModel, field_validator, ValidationError

def _load_instruction_from_file(file_path: str = './app/chatting/prompts/Generate_multi_query.txt'):
    with open(file_path, "r", encoding='utf-8') as f:
        load_text=f.read()
        return load_text

def generate_multi_query(llm_client, orig_query: str, query_amount: int, max_retry: int=5, verbose: bool = False) -> list[str]:
    """生成多個查詢

    Args:
        llm_client (LLMClient): `LLMClient`實例
        orig_query (str): 原始查詢字串
        query_amount (int): 需要生成的查詢數量
        max_retry (int, optional): 最大重試次數. Defaults to 5.

    Returns:
        list[str]: 包含多個 「生成的query」 的列表
    """
    # 定義一個pydantic類別用來確保LLM生成的結果符合預期的格式
    class multi_query_response(BaseModel):
        queries: dict

        @field_validator('queries')
        def check_queries(cls, v):
            if len(v) != query_amount:
                raise ValueError(f"JSON does not contain exactly {query_amount} items.")
            for key, value in v.items():
                if not key.startswith("query") or not key[5:].isdigit(): # Check the key is start with 'query' and end with a digit(number)
                    raise ValueError(f"Key {key} does not match required pattern 'query' + number.")
                if not isinstance(value, str):
                    raise ValueError(f"Value for {key} is not a string.")
            return v

    # 載入用來生成multi query的系統提示詞
    system_prompt_gen_multi_query=_load_instruction_from_file()

    # 格式化提示詞模板
    system_prompt=system_prompt_gen_multi_query.format(amount=query_amount)

    convo=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': '幫我寫一封email給保險公司，跟他說我想要調整汽車的保險合約內容。'},
        {'role': 'assistant', 'content': '{"query1": "撰寫一封至保險公司的電子信件，關於調整我的汽車保單條款","query2": "構建並發送給車險公司的一封電子郵件，要求更改合約詳細內容","query3": "草擬並寄出給汽車保險公司的正式電子郵件，請求修改合約內文"}'},
        {'role': 'user', 'content': orig_query},
    ]

    # Initialize the progress bar
    pbar = tqdm(total=max_retry, desc="Generating multiple queries", unit="attempt")

    # Make sure to get multiple queries with specific format
    retry_count=0
    while retry_count < max_retry:
        response=llm_client.ollama_invoke(convo=convo, format='json')

        validate_json_response=""
        try:
            json_response=json.loads(response['message']['content'])
            validate_json_response = multi_query_response(queries=json_response)
            break
        except ValidationError as e:
            if verbose == True:
                print(Fore.MAGENTA + "***** Response of question generation incorrect *****\n")
                print(Fore.MAGENTA + e.json())
            retry_count=retry_count+1
            pbar.update(1) # Update progress bar
            continue
        except Exception as ex:
            if verbose == True:
                print(Fore.MAGENTA + "***** An unexpected error occurred when generate questions *****\n")
                print(Fore.MAGENTA + ex)
            retry_count=retry_count+1
            pbar.update(1) # Update progress bar
            continue
    
    if validate_json_response != "":
        pbar.n = max_retry # Ensure the progress bar is complete
        queries=[]
        for _, value in validate_json_response.queries.items():
            queries.append(value)

        return queries
    else:
        return [] # 超過重試次數上限後返回空的列表