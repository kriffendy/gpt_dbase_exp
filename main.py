import logging
import openai
import uuid
from chat_utils import query_categorization, gpt_read, gpt_read_all
from secret import OPENAI_API_KEY
from database_utils import upsert, delete, update, read_all, query, get_id
from sentence_transformers import SentenceTransformer


operation_type = ["insert", "update", "delete", "read", "get all"]
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


if __name__ == "__main__":
    while True:
        openai.api_key = OPENAI_API_KEY
        user_query = input("Enter prompt: ")
        category = query_categorization(user_query)
        vectorized_query = model.encode(user_query).tolist()
        if category == 'insert':
            res = upsert(user_query, vectorized_query)
            if res:
                print('Data has been inserted successfully!')
            else:
                print('Data cannot be inserted! Please try again!')
        elif category == 'update':
            id = get_id(vectorized_query)
            res = update(id, vectorized_query, user_query)
            if res:
                print('Data has been updated successfully!')
            else:
                print('Data cannot be updated! Please try again!')
        elif category == 'delete':
            id = get_id(vectorized_query)
            res = delete([id])
            if res:
                print('Data has been deleted successfully!')
            else:
                print('Data cannot be deleted! Please try again!')
        elif category == 'read':
            id = get_id(vectorized_query)
            res = query(id)
            print(gpt_read(res))
        elif category == 'get all':
            res = read_all()
            print(gpt_read_all(res))
        else:
            print('Query cannot be understood!')