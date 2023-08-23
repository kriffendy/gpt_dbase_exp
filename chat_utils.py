from typing import Any, List, Dict
import openai
import requests
import secret
import logging

dbase_operations = ["insert", "read", "get all", "update", "delete"]

def query_categorization(query_prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "categorize the prompt based on the possible following operations: insert, read, get all, delete, update, outputting only category as response"},
        {"role": "assistant", "content": "prompt: " + query_prompt}
        ],
        max_tokens=1024,
        temperature=0.7,  # High temperature leads to a more creative response.
    )
    query_response = response["choices"][0]["message"]["content"]
    print("response: ", query_response)
    for item in dbase_operations:
        if item in query_response:
            return item
    return ""

def gpt_read(content: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"provide guest detail with following format (name (age:xx)) based on prompt: {content}"},
        ], max_tokens = 1024, temperature = 0.2
    )
    return response["choices"][0]["message"]["content"]

def gpt_read_all(contents: List[str]) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"output updated guest list (without any other detail/explanation) based on the prompt below, with format Current guest list: x. name (age: xx) prompt: {'. '.join(contents)}"},
        ], max_tokens = 1024, temperature = 0.2
    )
    return response["choices"][0]["message"]["content"]
