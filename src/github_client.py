"""
This file contains three functions to interact with the GitHub API: get_pr_diff(), post_pr_comment(), and get_file_content(owner, repo, path, sha, token).
- get_pr_diff() retrieves the diff of a pull request given the repository, pull request number, and token. Then
returns the diff text.
- post_pr_comment() posts a comment to a pull request given the repository, pull request number, comment body, 
and token. Then returns the response JSON.
- get_file_content() retrieves and decodes a file's contents from GitHub at a given commit SHA.

"""
import requests
import base64

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


def get_file_content(owner, repo, path, sha, token):

    # Checking if the required parameters are provided
    if not owner or not repo or not path:
        raise ValueError("Owner, repo, and path must be provided.")

    # Url for the repo's contents 
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    # Headers for the request, including the authorization token and the Accept header 
    headers = { 
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    params = {"ref": sha}

    # Make the GET request to the GitHub API
    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        return None

    data = response.json()

    # Making sure that the data is type file
    if data.get("type") != "file":
        return None

    # Decoding the data from github using base64
    encoded_content = data.get("content", "")
    decoded_bytes = base64.b64decode(encoded_content)

    # Try to return a text file for the github or if can not then return None
    try:
        return decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None
