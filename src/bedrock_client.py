"""
This file contains the function to call Bedrock and get an AI code review.
review_code() takes a diff, fills it into the prompt template, sends it to
Bedrock, and returns the AI's review text.
"""
import boto3
import json
import os
from pathlib import Path

def review_code(diff, file_content):
    # Client used to make requests to Bedrock
    client = boto3.client("bedrock-runtime")

    # For getting the prompt path in the project
    PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "review_prompt.txt"

    # Load the prompt template and fill in the diff and file_content
    with open(PROMPT_PATH, 'r', encoding='utf-8') as file:
        contents = file.read()
    prompt = contents.replace('{diff}', diff).replace('{file_content}', file_content)

    # Package the prompt in the format Bedrock's Claude models expect
    ai_input = {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}

    # Send the request to Bedrock
    response = client.invoke_model(
        modelId=os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"),
        body=json.dumps(ai_input),
        contentType="application/json",
        accept="application/json"
    )

    # Unwrap the response: stream -> bytes -> parsed JSON -> the actual review text
    raw_bytes = response["body"].read()
    response_body = json.loads(raw_bytes)
    return response_body["content"][0]["text"]

