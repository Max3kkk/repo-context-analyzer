import os
import token
import requests
import json

def get_repo_languages(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful

    data = response.json()

    total_lines = sum(data.values())
    data_percentage = {lang: (count / total_lines) * 100 for lang, count in data.items()}

    # round to 2 decimal places
    return {lang: round(percentage, 2) for lang, percentage in data_percentage.items() if percentage >= 30}


def write_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    # owner = os.getenv('OWNER')
    # repo = os.getenv('REPO')
    # token = os.getenv('GITHUB_TOKEN')
    owner = "max3kkk"
    repo = "moonlight-android"
    token = "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"
    filename = "data/project_languages.json"

    data = get_repo_languages(owner, repo, token)
    write_to_file(data, filename)