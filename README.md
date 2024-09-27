# Project Overview Generator

A powerful Python script to generate comprehensive overviews of your Python projects, helping you keep track of your codebase and seamlessly integrate with Large Language Models (LLMs) like ChatGPT.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Use Cases](#use-cases)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Introduction

In the era of AI-assisted development, tools like ChatGPT have become invaluable for coding assistance. However, they come with limitations, such as running out of context memory during extended sessions. This script bridges that gap by generating a detailed overview of your project, including file contents and directory structures, allowing you to feed this information back into an LLM to get back up to speed quickly.

Whether you're a developer looking to document your project or someone who frequently collaborates with AI models, this script is designed to make your life easier.

---

## Features

- **Generate Overviews of Python Files**: Scans your project directory and compiles all Python files into a single overview.
- **Directory Tree Generation**: Creates a tree view of your project's directory structure, including file permissions, ownership, and type.
- **Description Generation Using OpenAI's GPT-4**: Optionally generate concise descriptions of your Python files by integrating with the OpenAI API.
- **Customizable Ignoring Mechanism**: Dynamically ignore specific files or directories without hardcoding, using patterns or ignore files.
- **Include Specific Files or Directories**: Focus on particular parts of your project by specifying include patterns.
- **Flexible Command-Line Interface**: Easily control the script's behavior using various command-line options.
- **PEP 8 Compliant and Robust**: Written following best coding practices with comprehensive error handling and logging.

---

## Use Cases

### Overcoming LLM Context Limitations

Large Language Models like ChatGPT have a context window limitation. During extended sessions, they might "run out of memory," leading to decreased performance and forgotten details. This can be frustrating when you're in the middle of a complex project discussion.

**Solution**: By generating an overview of your project's code and directory structure, you can provide the LLM with the necessary context in a new session, effectively bringing it up to speed. This script automates that process, saving you time and ensuring continuity in your interactions with AI assistants.

### Project Documentation and Review

Need a quick summary of your project's structure or a consolidated view of all your Python files? This script can generate comprehensive overviews, making it easier to onboard new team members, conduct code reviews, or prepare for presentations.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/project-overview-generator.git
   cd project-overview-generator
   ```

2. **Install Dependencies**

   Ensure you have Python 3 installed. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

   *Note: The script uses standard libraries except for `requests`, which is required for OpenAI API calls.*

---

## Usage

### Command-Line Arguments

```plaintext
usage: create_overview.py [-h] [-p] [-t] [-description] [-api API_KEY] [-d PARTIAL_PROMPT]
                          [--ignore-dirs [IGNORE_DIRS ...]] [--ignore-files [IGNORE_FILES ...]]
                          [--ignore-patterns [IGNORE_PATTERNS ...]] [--ignore-file IGNORE_FILE]
                          [--include-dirs [INCLUDE_DIRS ...]] [--include-files [INCLUDE_FILES ...]]
                          [--include-patterns [INCLUDE_PATTERNS ...]]
                          [root_dir]

Create an overview of Python files and/or a directory tree.

positional arguments:
  root_dir              Root directory to scan.

optional arguments:
  -h, --help            show this help message and exit
  -p, --python          Process all Python files in the root directory.
  -t, --tree            Generate a tree view of the directory structure.
  -description          Enable description generation for Python files using ChatGPT API.
  -api API_KEY          OpenAI API key for generating descriptions.
  -d PARTIAL_PROMPT     Optional partial prompt to guide the description generation.

Include and ignore patterns:
  --ignore-dirs [IGNORE_DIRS ...]
                        List of directory patterns to ignore.
  --ignore-files [IGNORE_FILES ...]
                        List of file patterns to ignore.
  --ignore-patterns [IGNORE_PATTERNS ...]
                        List of patterns to ignore.
  --ignore-file IGNORE_FILE
                        Path to a file containing patterns to ignore.
  --include-dirs [INCLUDE_DIRS ...]
                        List of directory patterns to include.
  --include-files [INCLUDE_FILES ...]
                        List of file patterns to include.
  --include-patterns [INCLUDE_PATTERNS ...]
                        List of patterns to include.
```

### Examples

#### 1. Process All Python Files While Ignoring Specific Directories and Files

```bash
python create_overview.py -p --ignore-dirs tmp logs --ignore-files config.py
```

#### 2. Generate a Directory Tree, Reading Ignore Patterns from a File

Create an ignore file (e.g., `.myignore`) with patterns to ignore:

```plaintext
# .myignore
tmp
logs
*.pyc
```

Then run:

```bash
python create_overview.py -t --ignore-file .myignore
```

#### 3. Process Python Files with Description Generation Using an API Key

```bash
python create_overview.py -p -description -api YOUR_API_KEY
```

*Alternatively, set your API key as an environment variable:*

```bash
export OPENAI_API_KEY='your_api_key_here'
python create_overview.py -p -description
```

#### 4. Include Specific Directories or Files

```bash
python create_overview.py -p --include-dirs src tests --include-files main.py
```

#### 5. Combine Tree and Python File Processing with Custom Patterns

```bash
python create_overview.py -p -t --ignore-patterns '.*' '__*__' --include-dirs my_project
```

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- **OpenAI**: For providing the powerful GPT-4 model that enhances this script's capabilities.
- **Community Contributors**: Your feedback and suggestions make this tool better.

---

*Crafted with passion and a belief in the power of open-source tools to make developers' lives easier. If you find this script as kick-ass as we do, give it a star on GitHub!*
