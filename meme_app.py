import os
import requests

from flask import Flask, request
from github import Github, GithubIntegration


app = Flask(__name__)

app_id = '219152'

with open(
        os.path.normpath(os.path.expanduser('pr-meme-bot-42-private-key.pem')),
        'r'
) as cert_file:
    app_key = cert_file.read()

git_integration = GithubIntegration(
    app_id,
    app_key,
)


@app.route("/", methods=['POST'])
def bot():

    payload = request.json

    # Check if it is a GitHub PR event
    if not all(k in payload.keys() for k in ['action', 'pull_request']) and \
            payload['action'] == 'opened':
        return "ok"

    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']

    # Get git connection as our bot
    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")

    issue = repo.get_issue(number=payload['pull_request']['number'])

    # Call meme-api to get random meme
    response = requests.get(url='https://meme-api.herokuapp.com/gimme')
    if response.status_code != 200:
        return 'ok'

    meme_url = response.json()['preview'][-1]

    issue.create_comment(f"![Alt Text]({meme_url})")
    return "ok"


if __name__ == "__main__":
    app.run(debug=True, port=5000)