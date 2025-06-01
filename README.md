# SearchFlow

[![PyPI version](https://badge.fury.io/py/searchflow.svg)](https://badge.fury.io/py/searchflow)
[![Python Versions](https://img.shields.io/pypi/pyversions/searchflow.svg)](https://pypi.org/project/searchflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SearchFlow, powered by ArcDevs, is an AI-Powered Research Platform and advanced CLI tool leveraging ArcDevs Intelligence for intelligent research and automated report generation.**

It utilizes AI agents to connect to services and perform comprehensive searches, analyze information, and compile reports based on user queries.
*(For educational purposes, this project explores concepts similar to those that might be used by services like `searc.ai`.)*

## Features

*   **AI-Powered Research:** Employs advanced AI for in-depth information gathering.
*   **Multiple Report Types:** Generate summaries, detailed reports, or multi-agent analyses.
*   **Customizable Tone:** Adjust the writing tone of reports (Objective, Formal, Analytical, etc.).
*   **Domain Filtering:** Focus research on specific websites or domains.
*   **Interactive Mode:** Conduct multiple research queries in a single session.
*   **Configurable:** Save default preferences for report types and tones.
*   **Multiple Output Formats:** Save reports as text, Markdown, or JSON.
*   **Real-time Logging:** (Optional) View the AI's research process live.

## Installation

You can install SearchFlow using pip:

```bash
pip install searchflow
```

*(This command will work once the package is published to PyPI. For local development, see the section below.)*

## Usage

### Basic Search

```bash
searchflow "your research query here"
```

**Example:**

```bash
searchflow "latest advancements in quantum computing"
```

### Options

*   **Report Type (`-t` or `--type`):**
    *   `summary`: Quick overview (~2 min)
    *   `multi_agents_report`: Collaborative analysis
    *   `research_report`: Comprehensive research (~5 min)
    ```bash
    searchflow -t research_report "CRISPR gene editing ethics"
    ```

*   **Report Tone (`-o` or `--tone`):**
    *   `objective`: Impartial and unbiased
    *   `formal`: Academic and professional
    *   `analytical`: Critical evaluation
    *   `persuasive`: Convincing and argumentative
    *   `informative`: Clear and comprehensive
    ```bash
    searchflow -o formal "economic impact of renewable energy"
    ```

*   **Specific Domains (`-d` or `--domains`):**
    Provide a space-separated list of domains.
    ```bash
    searchflow -d arxiv.org nature.com "dark matter theories"
    ```

*   **No Real-time Logs (`--no-logs`):**
    Disables the streaming output of agent activities.
    ```bash
    searchflow --no-logs "history of the internet"
    ```

*   **Output to File (`-O` or `--output` with `--format`):**
    Supported formats: `text`, `markdown`, `json`.
    ```bash
    searchflow "Python web frameworks" -O report.md --format markdown
    searchflow "Market analysis of AI startups" -O analysis.json --format json
    ```

### Interactive Mode

For conducting multiple queries or easily changing settings per query:

```bash
searchflow --interactive
```

Inside interactive mode, type `help` for available commands.
Current settings (type/tone) are shown in the prompt. Use `set <option> <value>` to change them for the session.

### Configuration

Set your default preferences for report type, tone, and other settings:

```bash
searchflow --config
```

Settings are typically saved to `~/.searchflow/config.json`.

## Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arcdevs/searchflow.git
    cd searchflow
    ```
    *(Replace with your actual repository URL if different)*

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows (Git Bash or cmd):
    # venv\Scripts\activate
    ```

3.  **Install in editable mode with development dependencies:**
    The `[dev]` extra typically includes tools for testing, linting, etc.
    ```bash
    pip install -e .[dev]
    ```

4.  **Run the CLI:**
    Now you can run `searchflow` from your terminal, and any changes you make to the source code will be reflected immediately.
    ```bash
    searchflow --version
    ```

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` (you'll need to create this file with guidelines for contributors) and check the issue tracker for open tasks or to report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

*   KOBULA
*   UTKRASH RISHI
*   ArcDevs Corp

---
*Powered by ArcDevs Intelligence*