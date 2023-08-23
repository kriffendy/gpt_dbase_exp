from typing import Any, Dict
import requests
import os
import uuid
import json
import pinecone
import secret
from typing import List

SEARCH_TOP_K = 3

pinecone.init(api_key=secret.PINECONE_API_KEY, environment=secret.PINECONE_ENVIRONMENT) 
index = pinecone.Index(secret.PINECONE_INDEX) 
fileHandle = open('ids.txt', 'r')
existingIds = fileHandle.read().split('\n')

def upsert(content: str, values: List[float]) -> bool:
    id = str(uuid.uuid4())
    while id in existingIds:
        id = str(uuid.uuid4())
    response = index.upsert(
        vectors=[{
            'id': id,
            'values': values,
            'metadata': {'content': content}
        }]
    )
    if response.get("upserted_count"):
        existingIds.append(id)
        with open('ids.txt', 'w') as f:
            for id in existingIds:
                f.write(id + '\n')
        return True
    else:
        return False

def delete(ids: List[str]) -> bool:
    response = index.delete(ids = ids)
    if response == {}:
        for id in ids:
            existingIds.remove(id)
        with open('ids.txt', 'w') as f:
            for id in existingIds:
                f.write(id + '\n')
        return True
    else:
        return False


def update(id: str, values: List[float], content: str) -> bool:
    response = index.update(
        id = id,
        values = values,
        set_metadata={'content': content},
    )
    if response == {}:
        return True
    else:
        return False
    
def read_all() -> List[str]:
    filteredID = list(filter(lambda element: element != "", existingIds))
    response = index.fetch(filteredID)
    if response.get("vectors"):    #status code 200
        return [response.get("vectors").get(id).get("metadata").get("content") for id in filteredID]
    
def get_id(values: List[float]) -> str:
    response = index.query(top_k = 1, vector = values)
    if response.get("matches"):
        return response.get("matches")[0].get("id")
    else:
        print("Cannot get id!")
        return ""
    
def query(id: str) -> str:
    response = index.fetch(ids = [id])
    if response.get("vectors"):
        return response.get("vectors").get(id).get("metadata").get("content")


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input question.
    """
    url = "http://0.0.0.0:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {secret.DATABASE_INTERFACE_BEARER_TOKEN}",
    }
    data = {"queries": [{"query": query_prompt, "top_k": SEARCH_TOP_K}]}

    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")
    
