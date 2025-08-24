import requests
import time
import base64
import json
import yaml
import re

# Patterns to detect translation files and folders
TRANSLATION_FILE_EXTENSIONS = {'.po', '.pot', '.mo', '.xliff', '.arb'}
TRANSLATION_DIR_KEYWORDS = {'locales', 'i18n', 'lang', 'translations'}

# Example pattern to match Android style 'values-xx' folders with language codes
VALUES_LANG_FOLDER_REGEX = re.compile(r'^values-([a-z]{2}(-r[a-zA-Z]{2})?)$')  # values-fr, values-es, values-en-rUS

TRANSLATION_FILENAME_PATTERNS = [
    re.compile(r'.*messages.*', re.IGNORECASE),
    re.compile(r'.*translation.*', re.IGNORECASE),
    re.compile(r'.*locale.*', re.IGNORECASE),
    re.compile(r'.*strings.*', re.IGNORECASE),
]

def github_api_get(url, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            sleep_time = reset_time - int(time.time()) + 5
            if sleep_time > 0:
                print(f"Rate limit reached, sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
                continue
        response.raise_for_status()
        return response

def get_user_repos(username, token=None):
    repos = []
    per_page = 100
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page={per_page}&page={page}"
        response = github_api_get(url, token)
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_repo_all_files(owner, repo, branch='main', token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = github_api_get(url, token)
    data = response.json()
    return [item['path'] for item in data.get('tree', []) if item['type'] == 'blob']

def get_file_content(owner, repo, filepath, branch='main', token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}?ref={branch}"
    response = github_api_get(url, token)
    data = response.json()
    if data.get('encoding') == 'base64' and 'content' in data:
        content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
        return content
    return None

def is_translation_file(filename):
    filepath = filename.lower()
    path_parts = filepath.split('/')
    # Check translation directory keywords
    if any(part in TRANSLATION_DIR_KEYWORDS for part in path_parts):
        return True
    # Check values-xx folders for Android translations
    if any(VALUES_LANG_FOLDER_REGEX.match(part) for part in path_parts):
        return True
    # Check file extensions
    if any(filepath.endswith(ext) for ext in TRANSLATION_FILE_EXTENSIONS):
        return True
    # Check filename patterns
    filename_only = path_parts[-1]
    if any(pattern.match(filename_only) for pattern in TRANSLATION_FILENAME_PATTERNS):
        return True
    return False

def looks_like_translation_content(content, filename):
    ext = '.' + filename.split('.')[-1].lower()
    if ext in ['.po', '.pot']:
        return 'msgid' in content and 'msgstr' in content
    if ext in ['.json', '.yaml', '.yml', '.arb']:
        try:
            if ext in ['.json', '.arb']:
                data = json.loads(content)
            else:
                data = yaml.safe_load(content)
            if isinstance(data, dict):
                keys = data.keys()
                # Check if keys look like language codes or if values are strings
                if any(len(k) in (2, 5) for k in keys):
                    return True
                if any(isinstance(v, str) and len(v) > 0 for v in data.values()):
                    return True
        except Exception:
            return False
    return False

def scan_repo_for_translation_files(owner, repo, branch='main', token=None):
    files = get_repo_all_files(owner, repo, branch, token)
    translation_files = []
    for f in files:
        if is_translation_file(f):
            content = get_file_content(owner, repo, f, branch, token)
            if content and looks_like_translation_content(content, f):
                translation_files.append(f)
    return translation_files

def scan_all_user_repos_for_translations(username, token=None):
    repos = get_user_repos(username, token)
    translation_repos = {}
    for repo in repos:
        repo_name = repo['name']
        branch = repo.get('default_branch', 'main')
        print(f"Scanning repository: {repo_name} ...")
        matches = scan_repo_for_translation_files(username, repo_name, branch, token)
        if matches:
            translation_repos[repo_name] = matches
    return translation_repos

if __name__ == "__main__":
    github_username = "mao1910"  # Change to your user or target user
    github_token = None  # Add your GitHub personal access token here for higher rate limits
    results = scan_all_user_repos_for_translations(github_username, github_token)
    if results:
        print("\nTranslation files found in these repositories:\n")
        for repo, files in results.items():
            print(f"Repository: {repo}")
            for filepath in files:
                print(f"  - {filepath}")
    else:
        print("No translation files detected.")
