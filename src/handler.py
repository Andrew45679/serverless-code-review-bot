"""
Main Lambda entry point for the AI Code Review Bot

Handles incoming GitHub webhook events. Verifies each request is really
from GitHub, filters for pull request open/update events, fetches the
PR's diff, sends it to Bedrock for an AI review, and posts the result
back as a comment on the pull request.
"""
import json
import os
from webhook_verify import verify_signature
from bedrock_client import review_code
from github_client import get_pr_diff, post_pr_comment

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

    # Getting the repo and PR number
    repo = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    # Getting the code changes for this PR
    diff = get_pr_diff(repo, pr_number, token)

    # Send the diff to Bedrock and get the AI's written review
    response = review_code(diff)

    # Post the review back to the PR as a comment
    post_pr_comment(repo, pr_number, response, token)

    return {"statusCode": 200, "body": "The PR was successfuly reviewed and a comment has been posted"}


