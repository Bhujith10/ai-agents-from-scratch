import httpx
import base64
import os
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlparse

load_dotenv(find_dotenv())

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")  # optional but avoids rate limits
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def parse_github_url(url: str) -> tuple[str, str]:
    """Parse a GitHub repository URL and return the (owner, repo) tuple.
    
    Args:
        url: Full GitHub URL e.g. 'https://github.com/microsoft/vscode'
    
    Returns:
        Tuple of (owner, repo) strings.
    """
    path = urlparse(url).path          # /microsoft/vscode
    parts = path.strip("/").split("/") # ['microsoft', 'vscode']
    owner, repo = parts[0], parts[1]
    return owner, repo

def get_file_content(repo_url: str, file_path: str, branch: str = "main") -> str:
    """Fetch and decode the content of a file from a GitHub repository.

    Args:
        repo_url: Full GitHub URL (e.g. 'https://github.com/microsoft/vscode').
        file_path: Path to the file inside the repo (e.g. 'src/main.py').
        branch: Branch to read from. Defaults to 'main'.

    Returns:
        Decoded file content as a string, truncated to 10 000 characters if needed.
        Returns an error string on failure.
    """
    owner, repo = parse_github_url(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    response = httpx.get(url, headers=HEADERS)
    if response.status_code != 200:
        return f"Error: could not fetch '{file_path}' (HTTP {response.status_code})"
    data = response.json()
    if "content" not in data:
        return f"Error: no content returned for '{file_path}'"
    content = base64.b64decode(data["content"]).decode("utf-8")
    if len(content) > 10000:
        content = content[:10000] + "\n\n... [truncated]"
    return content

def get_file_tree(repo_url: str, branch: str = "main") -> str:
    """Fetch the recursive file tree of a GitHub repository.

    Automatically falls back to 'master' and 'main' if the requested branch
    returns a 404.

    Args:
        repo_url: Full GitHub URL (e.g. 'https://github.com/microsoft/vscode').
        branch: Preferred branch name. Defaults to 'main'.

    Returns:
        Newline-separated list of file paths (capped at 100 entries).
        Returns an error string if all branch attempts fail.
    """
    owner, repo = parse_github_url(repo_url)
    for b in [branch, "master", "main"]:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{b}?recursive=1"
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if "tree" not in data:
                return "Error: could not parse file tree"
            items = data["tree"]
            paths = [item["path"] for item in items[:100]]
            suffix = f"\n... and {len(items) - 100} more files" if len(items) > 100 else ""
            return "\n".join(paths) + suffix
    return f"Error: could not fetch file tree (tried branches: {branch}, master, main)"

def search(repo_url: str, query: str) -> str:
    """Search for files or code matching a query inside a GitHub repository.

    Uses the GitHub code search API. Results are limited to the top 10 matches.

    Args:
        repo_url: Full GitHub URL (e.g. 'https://github.com/microsoft/vscode').
        query: Search keyword or phrase (e.g. 'azure-openai', 'def train').

    Returns:
        Formatted string listing matching file paths and their GitHub URLs.
        Returns an error string on failure or 'No results found.' if empty.
    """
    owner, repo = parse_github_url(repo_url)
    url = f"https://api.github.com/search/code?q={query}+in:file,path+repo:{owner}/{repo}"
    response = httpx.get(url, headers=HEADERS)
    if response.status_code != 200:
        return f"Error: search failed (HTTP {response.status_code})"
    data = response.json()
    if "items" not in data:
        return f"Error: unexpected search response — {data.get('message', 'unknown error')}"
    items = data["items"][:10]
    if not items:
        return "No results found."
    return "".join([f"File : {item['path']}\nURL  : {item['html_url']}\n" for item in items])

if __name__ == "__main__":
    url = "https://github.com/mem0ai/mem0"
    print(f"Repo: {url}")
    # print(get_file_tree(url))
    # print(get_file_content(url, "mem0/client/main.py"))
    print(search(url, "azure-openai"))