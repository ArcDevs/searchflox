# SearchFlox ✨

[![PyPI version](https://badge.fury.io/py/searchflox.svg)](https://badge.fury.io/py/searchflox)
[![Python Versions](https://img.shields.io/pypi/pyversions/searchflox.svg)](https://pypi.org/project/searchflox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/ArcDevs/searchflox/python-package.yml?branch=main)](https://github.com/ArcDevs/searchflox/actions)

**SearchFlox, powered by ArcDevs, is an AI-Powered Research Platform and advanced CLI tool leveraging ArcDevs Intelligence for intelligent research and automated report generation.**

It utilizes AI agents to connect to services and perform comprehensive searches, analyze information, and compile reports based on user queries.
*(For educational purposes, this project explores concepts similar to those that might be used by services like `searc.ai`.)*

## 🚀 Features

*   **🧠 AI-Powered Research:** Employs advanced AI for in-depth information gathering.
*   **📄 Multiple Report Types:** Generate summaries, detailed reports, or multi-agent analyses.
*   **🎨 Customizable Tone:** Adjust the writing tone of reports (Objective, Formal, Analytical, etc.).
*   **🌐 Domain Filtering:** Focus research on specific websites or domains.
*   **💬 Interactive Mode:** Conduct multiple research queries in a single session.
*   **⚙️ Configurable:** Save default preferences for report types and tones.
*   **💾 Multiple Output Formats:** Save reports as text, Markdown, or JSON.
*   **📡 Real-time Logging:** (Optional) View the AI's research process live.

## 🛠️ Installation

You can install SearchFlox using pip:

```bash
pip install searchflox
```

*(This command will work once the package version with these updates is published to PyPI. For local development, see the section below.)*

## 💡 Usage

### Basic Search

Execute a search query directly from your terminal:

```bash
searchflox "your research query here"
```

**Example:**

```bash
searchflox "latest advancements in quantum computing"
```

You can also use the short alias `sf`:
```bash
sf "latest advancements in quantum computing"
```

### Command-Line Options

Fine-tune your research with these options:

*   **Report Type (`-t` or `--type`):**
    *   `summary`: Quick overview (~2 min)
    *   `multi_agents_report`: Collaborative analysis
    *   `research_report`: Comprehensive research (~5 min)
    ```bash
    searchflox -t research_report "CRISPR gene editing ethics"
    ```

*   **Report Tone (`-o` or `--tone`):**
    *   `objective`: Impartial and unbiased
    *   `formal`: Academic and professional
    *   `analytical`: Critical evaluation
    *   `persuasive`: Convincing and argumentative
    *   `informative`: Clear and comprehensive
    ```bash
    sf -o formal "economic impact of renewable energy"
    ```

*   **Specific Domains (`-d` or `--domains`):**
    Provide a space-separated list of domains.
    ```bash
    searchflox -d arxiv.org nature.com "dark matter theories"
    ```

*   **No Real-time Logs (`--no-logs`):**
    Disables the streaming output of agent activities for a cleaner console.
    ```bash
    searchflox --no-logs "history of the internet"
    ```

*   **Output to File (`-O` or `--output` with `--format`):**
    Save your research findings directly to a file. Supported formats: `text`, `markdown`, `json`.
    ```bash
    searchflox "Python web frameworks" -O report.md --format markdown
    sf "Market analysis of AI startups" -O analysis.json --format json
    ```

### Interactive Mode

For an engaging session with multiple queries or to easily change settings on the fly:

```bash
searchflox --interactive
# or
sf --interactive
```

Inside interactive mode:
*   Type `help` for a list of available commands.
*   Current settings (type/tone) are shown in the prompt.
*   Use `set <option> <value>` to change settings for the current session (e.g., `set type summary`).

### Configuration

Customize your default SearchFlox experience:

```bash
searchflox --config
# or
sf --config
```

Set your preferred report type, tone, and other settings. These are typically saved to `~/.searchflox/config.json` (the directory name matches the package).

## 💻 Local Development & Contribution

Want to contribute or run SearchFlox locally?

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ArcDevs/searchflox.git
    cd searchflox
    ```
2.  **Set up your environment:**
    Create and activate a virtual environment.
    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows (Git Bash or cmd):
    # venv\Scripts\activate
    ```

3.  **Install for development:**
    Install in editable mode with development dependencies.
    ```bash
    pip install -e .[dev]
    ```

4.  **Run the CLI:**
    You can now run `searchflox` (or `sf`) from your terminal. Changes to the source code will be reflected immediately.
    ```bash
    searchflox --version
    ```

##🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/ArcDevs/searchflox/issues).
Please read `CONTRIBUTING.md` (you'll need to create this file with guidelines for contributors).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🧑‍💻 Authors

*   **KOBULA**
*   **UTKRASH RISHI**
*   **ArcDevs Corp**

---
*Powered by ArcDevs Intelligence*