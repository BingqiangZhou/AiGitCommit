import os
import subprocess
import requests
import json

from config import API_KEY, MODEL_NAME, MODEL_CONTEXT_LENGTH

# Set your API key and endpoint
API_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"
CURL_PROXY = os.getenv("HTTPS_PROXY", "")
COMMIT_MESSAGE_SUFFIX = "--generate by AiGitCommit"

# Default language for commit message
LANGUAGES = "en"
# File to store user confirmation
CONFIRMATION_FILE = os.path.expanduser("~/.gptcommit_confirmed")

# ANSI color codes
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

# Parse command-line arguments
import sys
for arg in sys.argv[1:]:
    if arg.startswith("--lang="):
        LANGUAGES = arg.split("=", 1)[1]
    else:
        print(f"Unknown parameter passed: {arg}")
        sys.exit(1)

# Check for user confirmation
if not os.path.isfile(CONFIRMATION_FILE):
    print(f"{RED}Warning: This tool sends your code to an LLM, which may cause information leakage. Type YES to agree and not be prompted again.{NC}")
    user_confirmation = input()
    if user_confirmation != "YES":
        print("You did not confirm. Exiting.")
        sys.exit(1)
    else:
        with open(CONFIRMATION_FILE, 'w') as f:
            f.write("Confirmed.")

# Check the status of the working directory
print("Checking the status of the working directory...")
print(f"Current working directory: {os.getcwd()}")
git_status = subprocess.run(["git", "status"], capture_output=True, text=True).stdout

# Check for untracked files
print("Checking for untracked files...")
untracked_changes = ""
if "Untracked files:" in git_status:
    untracked_changes = subprocess.run(["git", "status", "--untracked-files"], capture_output=True, text=True, encoding="utf-8").stdout

# Get the difference between the working directory and the staging area
print("Getting the difference between the working directory and the staging area...")
working_diff = subprocess.run(["git", "diff"], capture_output=True, text=True, encoding="utf-8").stdout
staged_diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8").stdout

# Combine the differences
diff = working_diff + staged_diff + untracked_changes

# If there are no differences, exit
if not diff.strip():
    print("No differences found.")
    sys.exit(0)

# Call SiliconFlow API to generate a commit message
def generate_commit_message(languages, diff):
    url = API_ENDPOINT
    message = {
                "role": "user",
                "content": f"Analyze the following code changes, and generate a concise Git commit message, providing it in the following languages: {languages}. Text only:\n\n{diff}\n\n"
                # "content": f"Based on the following Git diff, analyze the file changes and code modifications, and generate a concise Git commit message. Please provide the message in the following languages: {languages}. Git diff Text:\n\n{diff}\n\n"
            }
    # check if the diff is too long, if so, only send the first part of the diff
    model_context_len = MODEL_CONTEXT_LENGTH - 64 # 64 is the lenght for "role": "user", "content": "..."
    if len(message["content"]) > model_context_len:
        # tip: the diff is too long, only send the first part of the diff, and the rest of the diff will be ignored.
        # change the console output text's color to red
        print(f"{RED}Warning: The diff is too long, only sending the first part of the diff, and the rest of the diff will be ignored.{NC}")
        message["content"] = message["content"][:model_context_len]

    payload = {
        "model": MODEL_NAME, 
        "messages": [message],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, proxies={"https": CURL_PROXY} if CURL_PROXY else None)
        response.raise_for_status()
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error: SiliconFlow API call failed due to network error: {e}")
        sys.exit(1)
    except (KeyError, IndexError):
        print("Error: SiliconFlow API returned an error.")
        sys.exit(1)

# Get the generated commit message
commit_message = generate_commit_message(LANGUAGES, diff)

# If no commit message is generated, exit
if not commit_message:
    print("Unable to generate commit message.")
    sys.exit(1)

# Add changes to the staging area
subprocess.run(["git", "add", "."])

# Commit the changes
subprocess.run(["git", "commit", "-m", commit_message + COMMIT_MESSAGE_SUFFIX])

print("Commit complete with message:")
print(commit_message)
