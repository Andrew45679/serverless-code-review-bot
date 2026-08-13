"""
Main Lambda entry point for the AI Code Review Bot

Handles incoming GitHub webhook events. Verifies each request is really
from GitHub, filters for pull request open/update events, fetches the
PR's diff along with the full content of each changed file for extra
context, sends everything to Bedrock for an AI review, and posts the
result back as a comment on the pull request.
"""
import json
import os
import requests
from webhook_verify import verify_signature
from bedrock_client import review_code
from github_client import get_pr_diff, post_pr_comment, get_file_content

# Allowed files for the bot
ALLOWED_FILES = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rb", ".php",
    ".yaml", ".yml", ".json",
    ".html", ".css",
    ".md", ".txt",
}

MAX_FILE_SIZE_CHARS = 8000
MAX_TOTAL_CONTEXT_CHARS = 30000
MAX_FILES = 10

def lambda_handler(event, context):
    # Get the signature, body, secret, and token
    signature = event['headers'].get('X-Hub-Signature-256')
    body = event['body']
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    token = os.environ.get("GITHUB_TOKEN")

    # Verifies webhook signatures are real
    if not verify_signature(body, signature, secret):
        return {"statusCode": 401, "body": "invalid signature"}

    # Parse the webhook payload
    payload = json.loads(body)

    # If the PR is closed then do not review it
    action = payload.get("action")
    if action not in ("opened", "synchronize", "reopened"):
        return {"statusCode": 200, "body": f"ignored action: {action}"}

    # Getting the repo, PR number, owner, and sha
    repo = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    owner = payload['repository']['owner']['login']
    sha = payload["pull_request"]["head"]["sha"]

    # Getting the code changes for this PR
    diff = get_pr_diff(repo, pr_number, token)

    # Get the list of changed file paths directly from GitHub's PR files endpoint
    files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    files_response = requests.get(files_url, headers=headers, timeout=10)
    changed_file_paths = [f["filename"] for f in files_response.json()] if files_response.status_code == 200 else []

    contexts = []
    total_chars = 0
    for file_path in changed_file_paths:
        # Check if the max files are reached for context
        if len(contexts) >= MAX_FILES:
            break

        # Only include files with a recognized code/text extension
        is_allowed_type = False
        for extension in ALLOWED_FILES:
            if file_path.endswith(extension):
                is_allowed_type = True
                break

        if not is_allowed_type:
            continue

        # Fetch this file's full content as it exists in the PR
        content = get_file_content(owner, repo, file_path, sha, token)

        # Skip if the fetch failed
        if content is None:
            continue

        # Skip individual files that are too large to be useful context
        if len(content) > MAX_FILE_SIZE_CHARS:
            continue

        # Stop adding files once they exceed the total contexts
        if total_chars + len(content) > MAX_TOTAL_CONTEXT_CHARS:
            break

        # Add file to context and update the total_chars
        contexts.append(f"--- {file_path} ---\n{content}")
        total_chars += len(content)

    # Combine all collected file contents into one string for the prompt
    file_contexts = "\n\n".join(contexts)

    # Send the diff to Bedrock and get the AI's written review
    response = review_code(diff, file_contexts)

    # Post the review back to the PR as a comment
    post_pr_comment(repo, pr_number, response, token)

    return {"statusCode": 200, "body": "The PR was successfuly reviewed and a comment has been posted"}


