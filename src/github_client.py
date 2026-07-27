"""
This file contains two functions to interact with the GitHub API: get_pr_diff() and post_pr_comment().
- get_pr_diff() retrieves the diff of a pull request given the repository, pull request number, and token. Then
returns the diff text.
- post_pr_comment() posts a comment to a pull request given the repository, pull request number, comment body, 
and token. Then returns the response JSON.

"""
import requests

def get_pr_diff(repo, pr_number, token):

    # Checking if the required parameters are provided
    if not repo or not pr_number or not token:
        raise ValueError("Repository, PR number, and token must be provided.")

    # Url to get the pull request diff from GitHub API
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    # Headers for the request, including the authorization token and the Accept header 
    headers = { 
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    # Make the GET request to the GitHub API
    response = requests.get(url, headers=headers, timeout=10)

    # Raise an exception if the request was unsuccessful
    response.raise_for_status()

    # Return the diff text from the response
    return response.text


def post_pr_comment(repo, pr_number, comment_body, token):
    # Checking if the required parameters are provided
    if not repo or not pr_number or not token or not comment_body:
        raise ValueError("Repository, PR number, token, and comment body must be provided.")

    # Url to get the pull request diff from GitHub API
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    # Headers for the request, including the authorization token and the Accept header 
    headers = { 
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # Make the POST request to the GitHub API
    response = requests.post(url, headers=headers, timeout=10, json={"body": comment_body})

    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Return the diff json from the response
    return response.json()
