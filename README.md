
# AiGitCommit

AiGitCommit is a Python script that automates the process of generating Git commit messages using AI. It analyzes the changes in your working directory and staging area, and sends the differences to an AI model to generate a concise and meaningful commit message.

## Features

- Supports multiple languages for commit messages.
- Sends the code changes to an AI model to generate a commit message.
- Adds the generated commit message to the staging area and commits the changes.

## Prerequisites

- Python 3.x
- Git
- An API key for the SiliconFlow API

## Installation

1. Install the required Python packages:

```bash
pip install requests
```

2. Set your API key by renaming config_example.py to config.py and updating the API key:

Edit `config.py` and update the API key:

```python
API_KEY = "your_api_key_here"
```

3. Set the `HTTPS_PROXY` environment variable if needed:

```bash
export HTTPS_PROXY="your_proxy_url_here"
```

## Usage

Run the script with the desired language for the commit message:

```bash
python AiGitCommit.py --lang=en
```

The script will analyze the changes in your working directory and staging area, and generate a commit message in the specified language.

## Configuration

- `API_ENDPOINT`: The endpoint for the SiliconFlow API.
- `CURL_PROXY`: The proxy URL for HTTPS requests.
- `COMMIT_MESSAGE_SUFFIX`: A suffix to add to the generated commit message.
- `LANGUAGES`: The default language for the commit message.
- `CONFIRMATION_FILE`: The file to store user confirmation.

## Disclaimer

This tool sends your code to an AI model, which may cause information leakage. Use it responsibly and ensure you have the necessary permissions to share your code.


## References

- [zhufengme/GPTCommit: A Script to Automatically Generate Git Commit Messages Using GPT](https://github.com/zhufengme/GPTCommit)
- [SiliconFlow, Accelerate AGI to Benefit Humanity](https://siliconflow.cn/zh-cn/)