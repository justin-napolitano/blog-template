# blog-template

A Python-based template repository for managing technical blog posts with automated frontmatter generation and environment setup.

## Features

- Automates metadata extraction and frontmatter creation for blog posts.
- Supports environment initialization with dependencies like OpenAI API client and date utilities.
- Uses TOML frontmatter and Markdown for blog content.

## Tech Stack

- Python 3
- OpenAI Python SDK
- dateutil
- tomli-w (TOML writer)
- dotenv for environment variable management

## Getting Started

### Prerequisites

- Python 3 installed
- Access to OpenAI API (for metadata generation)

### Installation

Clone the repository:

```bash
git clone https://github.com/justin-napolitano/blog-template.git
cd blog-template
```

Initialize the environment and install dependencies:

```bash
source .env
python3 -m venv .venv
source .venv/bin/activate
pip install openai tomli-w python-dateutil
```

### Running

- Use `fill_frontmatter.py` to generate or update blog post metadata.
- Blog posts are written in Markdown with TOML frontmatter (e.g., `index.md`).

## Project Structure

- `fill_frontmatter.py`: Python script to generate frontmatter metadata using OpenAI API.
- `index.md`: Sample blog post in Markdown with frontmatter.
- `initialize.sh`: Shell script to set up environment (activate venv and install dependencies).
- `initialize.sh.bak`: Backup of initialization script.

## Future Work / Roadmap

- Complete and enhance frontmatter generation logic in `fill_frontmatter.py`.
- Add support for batch processing multiple blog posts.
- Integrate validation and formatting checks for frontmatter.
- Expand documentation and usage examples.
- Potentially add CI/CD workflows for blog deployment.
