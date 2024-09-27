#!/usr/bin/env python3
"""
Create an overview of Python files and/or a directory tree.

Usage examples:

- Process all Python files while ignoring specific directories and files:
  python create_overview.py -p --ignore-dirs tmp logs --ignore-files config.py

- Generate a directory tree, reading ignore patterns from a file:
  python create_overview.py -t --ignore-file .myignore

- Process Python files with description generation using an API key:
  python create_overview.py -p -description -api YOUR_API_KEY

- Include specific directories or files:
  python create_overview.py -p --include-dirs src tests --include-files main.py

For more help, run:
  python create_overview.py -h

"""

import os
import json
import argparse
from datetime import datetime
import pwd
import stat
import requests
import sys
import logging
import fnmatch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def should_process(path, root_dir, include_patterns, ignore_patterns):
    """
    Determine whether a given path should be processed based on include and ignore patterns.

    Args:
        path (str): The file or directory path to check.
        root_dir (str): The root directory of the scan.
        include_patterns (list): List of patterns to include.
        ignore_patterns (list): List of patterns to ignore.

    Returns:
        bool: True if the path should be processed, False otherwise.
    """
    rel_path = os.path.relpath(path, root_dir)
    base_name = os.path.basename(path)

    # Do not ignore the root directory
    if rel_path == '.':
        return True

    # If include_patterns is provided, process only if path matches an include pattern
    if include_patterns:
        included = any(fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(base_name, pattern)
                       for pattern in include_patterns)
        if not included:
            return False

    # Exclude if path matches any ignore patterns
    ignored = any(fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(base_name, pattern)
                  for pattern in ignore_patterns)
    if ignored:
        return False

    return True


def get_file_description(file_content, api_key, partial_prompt=None):
    """
    Sends the file content to OpenAI's ChatGPT API to retrieve a concise description.
    Returns a tuple of (description, usage_info).

    Args:
        file_content (str): The content of the Python file.
        api_key (str): OpenAI API key.
        partial_prompt (str, optional): An optional partial prompt to guide the description generation.

    Returns:
        tuple: (description (str), usage_info (dict))
    """
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Construct the prompt
    main_prompt = (
        "Provide a concise description of the following Python file, focusing on the filename, its path, "
        "its purpose, and key variables with their purposes. Do not include unnecessary explanations of open-source platforms or general concepts."
    )
    if partial_prompt:
        main_prompt = f"{partial_prompt}\n{main_prompt}"

    system_message = {
        "role": "system",
        "content": "You are ChatGPT, a large language model trained by OpenAI."
    }

    user_message = {
        "role": "user",
        "content": f"{main_prompt}\n\n```python\n{file_content}\n```"
    }

    payload = {
        "model": "gpt-4",
        "messages": [system_message, user_message],
        "max_tokens": 150,  # Reduced max_tokens for shorter descriptions
        "temperature": 0.3  # Lower temperature for more focused responses
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        description = data['choices'][0]['message']['content'].strip()

        # Extract token usage
        usage = data.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)

        usage_info = {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }

        return description, usage_info

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while fetching description: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred while fetching description: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred while fetching description: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An error occurred while fetching description: {req_err}")
    except KeyError:
        logging.error("Unexpected response structure from the API.")

    return "Description unavailable due to an API error.", {}


def process_all_python_files(root_dir, include_patterns, ignore_patterns, api_key=None, partial_prompt=None):
    """
    Processes all Python files in the root directory, optionally generating descriptions using the ChatGPT API.
    Outputs both plain text and JSON files containing file details and descriptions.

    Args:
        root_dir (str): The root directory to scan.
        include_patterns (list): List of patterns to include.
        ignore_patterns (list): List of patterns to ignore.
        api_key (str, optional): OpenAI API key.
        partial_prompt (str, optional): An optional partial prompt to guide the description generation.
    """
    overview_data = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_txt = f"all_python_files_{timestamp}.txt"
    output_file_json = f"all_python_files_{timestamp}.json"

    try:
        with open(output_file_txt, 'w', encoding='utf-8') as output_txt:
            for dirpath, dirnames, filenames in os.walk(root_dir):
                # Modify dirnames in place to prevent os.walk from descending into ignored directories
                dirnames[:] = [d for d in dirnames if should_process(os.path.join(dirpath, d), root_dir, include_patterns, ignore_patterns)]

                if not should_process(dirpath, root_dir, include_patterns, ignore_patterns):
                    logging.debug(f"Ignored directory: {dirpath}")
                    continue

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if not should_process(filepath, root_dir, include_patterns, ignore_patterns):
                        logging.debug(f"Ignored file: {filepath}")
                        continue

                    if filename.endswith('.py'):
                        logging.info(f"Processing file: {filepath}")
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                        except (IOError, OSError) as e:
                            logging.error(f"Failed to read file {filepath}: {e}")
                            continue

                        if api_key:
                            description, usage = get_file_description(file_content, api_key, partial_prompt)
                            file_entry = {
                                'filename': filename,
                                'filepath': filepath,
                                'description': description,
                                'content': file_content
                            }
                            output_txt.write(f"'{filename}'\n**Description:** {description}\n``` File path = {filepath}\n\n")
                            output_txt.write(file_content)
                            output_txt.write("\n```\n\n")

                            # Log token usage
                            if usage:
                                logging.info(
                                    f"Tokens used for {filename}: "
                                    f"Prompt={usage['prompt_tokens']}, "
                                    f"Completion={usage['completion_tokens']}, "
                                    f"Total={usage['total_tokens']}"
                                )
                        else:
                            file_entry = {
                                'filename': filename,
                                'filepath': filepath,
                                'content': file_content
                            }
                            output_txt.write(f"'{filename}'\n``` File path = {filepath}\n\n")
                            output_txt.write(file_content)
                            output_txt.write("\n```\n\n")

                        overview_data.append(file_entry)

    except (IOError, OSError) as e:
        logging.critical(f"Failed to write to output file {output_file_txt}: {e}")
        sys.exit(1)

    try:
        with open(output_file_json, 'w', encoding='utf-8') as output_json:
            json.dump(overview_data, output_json, ensure_ascii=False, separators=(',', ':'))
    except (IOError, OSError) as e:
        logging.critical(f"Failed to write to JSON output file {output_file_json}: {e}")
        sys.exit(1)


def generate_tree_view(root_dir, include_patterns, ignore_patterns):
    """
    Generates a tree view of the directory structure, including file permissions, ownership, and type.
    Outputs both plain text and JSON files containing the tree structure.

    Args:
        root_dir (str): The root directory to scan.
        include_patterns (list): List of patterns to include.
        ignore_patterns (list): List of patterns to ignore.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_tree = f"directory_tree_{timestamp}.txt"
    output_file_json = f"directory_tree_{timestamp}.json"
    tree_data = []

    try:
        with open(output_file_tree, 'w', encoding='utf-8') as output_txt:
            for dirpath, dirnames, filenames in os.walk(root_dir):
                # Modify dirnames in place to prevent os.walk from descending into ignored directories
                dirnames[:] = [d for d in dirnames if should_process(os.path.join(dirpath, d), root_dir, include_patterns, ignore_patterns)]

                if not should_process(dirpath, root_dir, include_patterns, ignore_patterns):
                    logging.debug(f"Ignored directory: {dirpath}")
                    continue

                output_txt.write(f"\nDirectory: {dirpath}\n")
                output_txt.write("=" * (len(dirpath) + 11) + "\n")

                directory_info = {"directory": dirpath, "contents": []}

                for name in dirnames + filenames:
                    full_path = os.path.join(dirpath, name)
                    if not should_process(full_path, root_dir, include_patterns, ignore_patterns):
                        logging.debug(f"Ignored: {full_path}")
                        continue

                    try:
                        stats = os.stat(full_path)
                        permissions = stat.filemode(stats.st_mode)
                        owner = pwd.getpwuid(stats.st_uid).pw_name
                        entry_info = {
                            "name": name,
                            "permissions": permissions,
                            "owner": owner,
                            "type": "directory" if os.path.isdir(full_path) else "file"
                        }
                        output_txt.write(f"{permissions} {owner} {name}\n")
                        directory_info["contents"].append(entry_info)
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error(f"Failed to access {full_path}: {e}")
                        continue

                tree_data.append(directory_info)
    except (IOError, OSError) as e:
        logging.critical(f"Failed to write to tree output file {output_file_tree}: {e}")
        sys.exit(1)

    # Write out the JSON file in a compact single-line format
    try:
        with open(output_file_json, 'w', encoding='utf-8') as output_json:
            json.dump(tree_data, output_json, ensure_ascii=False, separators=(',', ':'))
    except (IOError, OSError) as e:
        logging.critical(f"Failed to write to JSON output file {output_file_json}: {e}")
        sys.exit(1)


def main():
    """
    Main function to parse command-line arguments and execute the appropriate functions.
    """
    parser = argparse.ArgumentParser(
        description="Create an overview of Python files and/or a directory tree.",
        formatter_class=argparse.RawTextHelpFormatter)

    current_working_directory = os.getcwd()  # Get current working directory
    parser.add_argument('root_dir', nargs='?', default=current_working_directory, help="Root directory to scan.")
    parser.add_argument('-p', '--python', action='store_true', help="Process all Python files in the root directory.")
    parser.add_argument('-t', '--tree', action='store_true', help="Generate a tree view of the directory structure.")
    parser.add_argument('-description', action='store_true', help="Enable description generation for Python files using ChatGPT API.")
    parser.add_argument('-api', metavar='API_KEY', type=str, help="OpenAI API key for generating descriptions.")
    parser.add_argument('-d', metavar='PARTIAL_PROMPT', type=str, help="Optional partial prompt to guide the description generation.")

    # Include and ignore patterns
    parser.add_argument('--ignore-dirs', nargs='*', help='List of directory patterns to ignore.')
    parser.add_argument('--ignore-files', nargs='*', help='List of file patterns to ignore.')
    parser.add_argument('--ignore-patterns', nargs='*', help='List of patterns to ignore.')
    parser.add_argument('--ignore-file', help='Path to a file containing patterns to ignore.')
    parser.add_argument('--include-dirs', nargs='*', help='List of directory patterns to include.')
    parser.add_argument('--include-files', nargs='*', help='List of file patterns to include.')
    parser.add_argument('--include-patterns', nargs='*', help='List of patterns to include.')

    args = parser.parse_args()

    # Retrieve API key from environment variable if available
    env_api_key = os.getenv('OPENAI_API_KEY') or os.getenv('API_KEY') or os.getenv('api_key')

    # Determine the API key to use
    if args.description:
        if args.api:
            api_key = args.api
            logging.info("Using OpenAI API key provided via '-api' argument.")
        elif env_api_key:
            api_key = env_api_key
            logging.info("Using OpenAI API key from environment variables.")
        else:
            logging.critical(
                "An API key is required when using '-description'. Provide it via the '-api' argument or set it in one of the environment variables: 'OPENAI_API_KEY', 'API_KEY', 'api_key'."
            )
            sys.exit(1)
    else:
        api_key = None

    if args.description:
        logging.info("Description generation enabled.")

    logging.info(f"Root directory to scan: {args.root_dir}")

    # Default ignore patterns
    default_ignore_patterns = ['.*', '__*__', 'venv', 'env', '__pycache__']

    # Collect ignore patterns
    ignore_patterns = default_ignore_patterns.copy()

    if args.ignore_patterns:
        ignore_patterns.extend(args.ignore_patterns)

    if args.ignore_dirs:
        ignore_patterns.extend(args.ignore_dirs)

    if args.ignore_files:
        ignore_patterns.extend(args.ignore_files)

    if args.ignore_file:
        try:
            with open(args.ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.append(line)
        except Exception as e:
            logging.error(f"Failed to read ignore file {args.ignore_file}: {e}")
            sys.exit(1)

    # Collect include patterns
    include_patterns = []

    if args.include_patterns:
        include_patterns.extend(args.include_patterns)

    if args.include_dirs:
        include_patterns.extend(args.include_dirs)

    if args.include_files:
        include_patterns.extend(args.include_files)

    logging.debug(f"Include patterns: {include_patterns}")
    logging.debug(f"Ignore patterns: {ignore_patterns}")

    if args.python:
        process_all_python_files(
            root_dir=args.root_dir,
            include_patterns=include_patterns,
            ignore_patterns=ignore_patterns,
            api_key=api_key,
            partial_prompt=args.d
        )

    if args.tree:
        generate_tree_view(args.root_dir, include_patterns, ignore_patterns)


if __name__ == "__main__":
    main()