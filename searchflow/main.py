#!/usr/bin/env python3
"""
SearchFlow - Advanced AI Research Platform
A powerful CLI tool for AI-powered research and report generation.

Author: KOBULA & UTKRASH RISHI from ArcDevs Corp
Purpose: Professional AI Research Tool
Copyright: ArcDevs Corp (c) 2025 - All Rights Reserved
"""

import asyncio
import websockets
import json
import time
import sys
import traceback
import signal
import threading
import argparse
import os
from urllib.parse import quote
from typing import Dict, List, Optional, Any

__version__ = "1.0.0"
__author__ = "KOBULA & UTKRASH RISHI from ArcDevs Corp"
__email__ = "arcdev.90@gmail.com"
__license__ = "MIT"

class Colors:
    """ANSI color codes for terminal output"""
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal environments"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')

if not sys.stdout.isatty():
    Colors.disable()

C = Colors

APP_NAME = "SearchFlow"
APP_TITLE = f"{C.BOLD}{C.CYAN}{APP_NAME} - AI Research Platform{C.RESET} {C.YELLOW}v{__version__}{C.RESET}"
CREDITS = f"{C.BOLD}{C.GREEN}Developed by KOBULA & UTKRASH RISHI{C.RESET} {C.YELLOW}| ArcDevs Corp{C.RESET}\n{C.CYAN}💬 Join our Telegram: {C.UNDERLINE}https://t.me/ArcAgents{C.RESET}"
SEPARATOR = f"{C.BLUE}{'=' * 70}{C.RESET}"

PROMPT_COLOR = C.BOLD + C.GREEN
QUERY_COLOR = C.BOLD + C.YELLOW
INFO_COLOR = C.CYAN
LOG_COLOR = C.WHITE
SOURCE_COLOR = C.GREEN
REPORT_CHUNK_COLOR = C.MAGENTA
ERROR_COLOR = C.BOLD + C.RED
SUCCESS_COLOR = C.BOLD + C.GREEN
PATH_COLOR = C.BLUE
URL_COLOR = C.UNDERLINE + C.BLUE

REPORT_TYPES = {
    "1": {"display": "Summary - Quick overview (~2 min)", "api_value": "summary"},
    "2": {"display": "Multi-Agent - Collaborative analysis", "api_value": "multi_agents_report"},
    "3": {"display": "Detailed - Comprehensive research (~5 min)", "api_value": "research_report"},
}

TONES = {
    "1": "Objective - Impartial and unbiased presentation",
    "2": "Formal - Academic and professional standards",
    "3": "Analytical - Critical evaluation and examination",
    "4": "Persuasive - Convincing and argumentative",
    "5": "Informative - Clear and comprehensive information",
}

DEFAULT_CONFIG = {
    "report_type": "1",
    "tone": "1",
    "domains": [],
    "show_logs": True,
    "websocket_url": "wss://searc.ai/ws",
    "base_url": "https://searc.ai/",
    "timeout": 120,
    "max_retries": 3
}

class SearchFlowConfig:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.searchflow/config.json")
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
        except Exception as e:
            print(f"{C.YELLOW}Warning: Could not load config file: {e}{C.RESET}")

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"{C.YELLOW}Warning: Could not save config: {e}{C.RESET}")

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()

class InterruptHandler:
    def __init__(self):
        self.interrupted = False
        self.websocket = None
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.interrupted = True
        if self.websocket:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(self._close_websocket(), loop)
            else: 
                try:
                    asyncio.run(self._close_websocket())
                except RuntimeError:
                    pass 

    async def _close_websocket(self):
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                pass

class ProgressIndicator:
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.indicators = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.stop_event.clear()
        self.thread.start()

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=1)
            print(f"\r{' ' * (len(self.message) + 10)}\r", end="", flush=True)


    def _animate(self):
        i = 0
        while not self.stop_event.is_set():
            print(f"\r{C.CYAN}{self.indicators[i % len(self.indicators)]} {self.message}...{C.RESET}",
                  end="", flush=True)
            i += 1
            time.sleep(0.1)

class SearchFlowEngine:
    def __init__(self, config: SearchFlowConfig):
        self.config = config
        self.interrupt_handler = InterruptHandler()

    async def search(self,
                    query: str,
                    report_type: str = "summary",
                    tone: str = "Objective",
                    domains: Optional[List[str]] = None,
                    show_logs: bool = True) -> Optional[Dict[str, Any]]:

        uri = self.config.get("websocket_url")
        base_url = self.config.get("base_url")
        domains = domains or []

        headers = {
            "Origin": "https://searc.ai",
            "User-Agent": f"SearchFlow/{__version__} (CLI; Python/{sys.version_info.major}.{sys.version_info.minor})",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        final_report_parts = [] 
        sources = []
        download_links = {}
        message_count = 0
        start_time = time.time()

        progress = None
        if not show_logs:
            progress = ProgressIndicator("AI Research in Progress")
            progress.start()

        print(f"\n{C.BOLD}🚀 SearchFlow Research Initiated:{C.RESET} {QUERY_COLOR}{query}{C.RESET}")
        print(f"{INFO_COLOR}   Report: {report_type} | Tone: {tone} | Domains: {', '.join(domains) if domains else 'Any'}{C.RESET}")
        print(f"{C.YELLOW}   Powered by SearchFlow AI Intelligence{C.RESET}")
        
        self.interrupt_handler.interrupted = False

        try:
            async with websockets.connect(uri, additional_headers=headers,
                                        ping_interval=20, ping_timeout=20,
                                        open_timeout=10) as websocket:

                self.interrupt_handler.websocket = websocket

                payload = {
                    "task": query,
                    "report_type": report_type,
                    "report_source": "web",
                    "tone": tone,
                    "query_domains": domains
                }

                message = f'start {json.dumps(payload)}'
                print(f"{C.YELLOW}📤 Connecting to SearchFlow Intelligence...{C.RESET}")
                await websocket.send(message)
                print(f"{SUCCESS_COLOR}✅ Connected! AI agents are now researching...{C.RESET}")

                if show_logs:
                    print(SEPARATOR)

                research_complete = False
                timeout_count = 0
                max_timeouts = self.config.get("timeout", 120) // 2 # e.g., 120s / 2s/timeout = 60 timeouts

                while not research_complete and not self.interrupt_handler.interrupted:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        message_count += 1
                        timeout_count = 0 

                        await self._process_response(response, show_logs, sources, download_links, final_report_parts)

                        if self._is_research_complete(response):
                            research_complete = True

                    except asyncio.TimeoutError:
                        timeout_count += 1
                        if timeout_count >= max_timeouts:
                            print(f"\n{C.YELLOW}⏰ Research timeout reached after {max_timeouts*2}s of inactivity. Finalizing results...{C.RESET}")
                            research_complete = True
                        elif show_logs and timeout_count % 5 == 0:
                            print(f"{LOG_COLOR}.{C.RESET}", end="", flush=True)
                    except websockets.exceptions.ConnectionClosed:
                        research_complete = True
                        break


                final_report_str = "".join(final_report_parts)
                duration = time.time() - start_time

                if progress:
                    progress.stop()
                
                if self.interrupt_handler.interrupted:
                    print(f"\n{C.YELLOW}🛑 Research process was interrupted.{C.RESET}")
                    # Return partial results if any
                    return await self._finalize_results(final_report_str, sources, download_links,
                                                      message_count, duration, base_url, interrupted=True)


                return await self._finalize_results(final_report_str, sources, download_links,
                                                  message_count, duration, base_url)

        except websockets.exceptions.InvalidStatusCode as e:
            print(f"{ERROR_COLOR}❌ Server error (Status {e.status_code}). The server might be busy or unable to connect. Please try again later.{C.RESET}")
        except websockets.exceptions.ConnectionClosedOK:
            final_report_str = "".join(final_report_parts) 
            duration = time.time() - start_time
            if progress: progress.stop()
            print(f"\n{SUCCESS_COLOR}✅ Research completed and connection closed cleanly.{C.RESET}")
            return await self._finalize_results(final_report_str, sources, download_links, message_count, duration, base_url)
        except websockets.exceptions.WebSocketException as e: 
            print(f"{ERROR_COLOR}❌ WebSocket Connection Error: {e}{C.RESET}")
        except ConnectionRefusedError:
            print(f"{ERROR_COLOR}❌ Connection Refused: Cannot connect to SearchFlow server at {uri}. Is it running?{C.RESET}")
        except KeyboardInterrupt:
            if progress: progress.stop()
            final_report_str = "".join(final_report_parts)
            duration = time.time() - start_time
            print(f"\n{C.YELLOW}🛑 Research interrupted by user.{C.RESET}")
            return await self._finalize_results(final_report_str, sources, download_links,
                                              message_count, duration, base_url, interrupted=True)
        except Exception as e:
            if progress: progress.stop()
            print(f"{ERROR_COLOR}❌ An unexpected error occurred in SearchFlowEngine: {e}{C.RESET}")
            if show_logs or self.config.get("debug_mode", False): 
                traceback.print_exc()
        finally:
            if progress and progress.thread and progress.thread.is_alive():
                progress.stop()
            self.interrupt_handler.websocket = None

        return None


    async def _process_response(self, response: str, show_logs: bool, sources: List,
                              download_links: Dict, final_report_parts: List[str]):
        try:
            data = json.loads(response)
            msg_type = data.get("type")

            if msg_type == "logs":
                await self._handle_log_message(data, show_logs, sources)
            elif msg_type == "report":
                chunk = data.get("output", "")
                final_report_parts.append(chunk) 
                if show_logs:
                    print(f"{REPORT_CHUNK_COLOR}{chunk}{C.RESET}", end="", flush=True)
            elif msg_type == "path":
                await self._handle_path_message(data, download_links, show_logs)
            elif msg_type == "error":
                error_message = data.get("output") or data.get("message", "Unknown error from server.")
                print(f"{ERROR_COLOR}❌ Server-side error: {error_message}{C.RESET}")


        except json.JSONDecodeError:
            if "pong" in response.lower() or "ping" in response.lower():
                if show_logs and self.config.get("debug_mode"): print(f"{LOG_COLOR}Received: {response}{C.RESET}")
            elif show_logs : 
                print(f"{C.YELLOW}📨 Raw (non-JSON): {response[:150]}{'...' if len(response) > 150 else ''}{C.RESET}")


    async def _handle_log_message(self, data: Dict, show_logs: bool, sources: List):
        content = data.get("content", "") 
        output = data.get("output", "")  

        if show_logs:
            log_prefix = f"{LOG_COLOR}ℹ️  [{data.get('source', 'GENERAL').upper()}]" 
            
            if content == "added_source_url":
                metadata = data.get("metadata") 
                url_to_add = None
                if isinstance(metadata, str): url_to_add = metadata
                elif isinstance(output, str) and output.startswith("http"): url_to_add = output

                if url_to_add and url_to_add not in sources:
                    sources.append(url_to_add)
                    print(f"{SOURCE_COLOR}📎 Source Added: {URL_COLOR}{url_to_add}{C.RESET}")
            elif content == "error" or data.get("level") == "error":
                print(f"{ERROR_COLOR}❌ Agent Error: [{data.get('source', 'AGENT')}] {output or content}{C.RESET}")
            else: 
                message_parts = [part for part in [content, output] if part] 
                full_message = " - ".join(message_parts)
                print(f"{log_prefix} {full_message}{C.RESET}")


    async def _handle_path_message(self, data: Dict, download_links: Dict, show_logs: bool):
        if show_logs:
            last_char = sys.stdout.encoding
            print()
            print(f"{PATH_COLOR}🛣️  Report Files Generated:{C.RESET}")

        paths = data.get("output", {})
        base_url = self.config.get('base_url').rstrip('/') 

        for file_type, path_suffix in paths.items():
            if path_suffix:
                if path_suffix.startswith('/'): path_suffix = path_suffix[1:]
                full_url = f"{base_url}/{quote(path_suffix)}"
                download_links[file_type.lower()] = full_url
                if show_logs:
                    print(f"  {SUCCESS_COLOR}🔗 {file_type.upper()}: {URL_COLOR}{full_url}{C.RESET}")

    def _is_research_complete(self, response: str) -> bool:
        try:
            data = json.loads(response)
            if data.get("type") in ["end_of_stream", "complete", "finished", "done", "end"]:
                return True
            if data.get("status") == "completed":
                return True
            if data.get("type") == "logs" and data.get("content") == "report_written":
                return True
        except json.JSONDecodeError:
            if any(marker in response.lower() for marker in ["<|END_OF_STREAM|>", "TASK_COMPLETE"]): 
                 return True
        return False


    async def _finalize_results(self, report: str, sources: List, download_links: Dict,
                              message_count: int, duration: float, base_url: str, interrupted: bool = False) -> Dict[str, Any]:
        print(f"\n{SEPARATOR}")
        if interrupted:
            print(f"{C.BOLD}{C.YELLOW}📊 Partial SearchFlow Research Results 📊{C.RESET}")
        else:
            print(f"{C.BOLD}{C.CYAN}📊 SearchFlow Research Complete 📊{C.RESET}")
        print(f"{INFO_COLOR}   Duration: {duration:.1f}s | Messages Processed: {message_count}{C.RESET}")

        unique_sources = sorted(list(set(s for s in sources if s and s.startswith("http")))) 
        if unique_sources:
            print(f"\n{SOURCE_COLOR}🔗 Sources ({len(unique_sources)}):{C.RESET}")
            for i, source_url in enumerate(unique_sources[:15], 1):
                print(f"  {i}. {URL_COLOR}{source_url}{C.RESET}")
            if len(unique_sources) > 15:
                print(f"  ... and {len(unique_sources) - 15} more.")

        if download_links:
            print(f"\n{SUCCESS_COLOR}⏬ Download Links for Full Reports:{C.RESET}")
            for file_type, link in download_links.items():
                print(f"  🔗 {file_type.upper()}: {URL_COLOR}{link}{C.RESET}")
        elif not interrupted :
            print(f"\n{C.YELLOW}ℹ️ No specific download links were provided for this report.{C.RESET}")


        if report:
            print(f"\n{C.BOLD}{REPORT_CHUNK_COLOR}📋 Report Text Preview ({len(report)} chars):{C.RESET}")
            max_preview_len = 800
            if len(report) > max_preview_len:
                preview = f"{report[:max_preview_len//2]}\n{C.MAGENTA}[... Content Truncated ...]\n{C.WHITE}{report[-(max_preview_len//2):]}"
            else:
                preview = report
            print(f"{C.WHITE}{'-' * 60}{C.RESET}")
            print(preview)
            print(f"{C.WHITE}{'-' * 60}{C.RESET}")
        elif not interrupted:
            print(f"\n{C.YELLOW}ℹ️ No text report content was generated directly in the stream.{C.RESET}")
            if not download_links:
                 print(f"{C.YELLOW}   Please check logs or try a different query/report type if you expected content.{C.RESET}")


        print(f"{SEPARATOR}")
        print(CREDITS)

        return {
            "report": report,
            "sources": unique_sources,
            "download_links": download_links,
            "message_count": message_count,
            "duration": duration,
            "success": not interrupted and (bool(report) or bool(download_links)),
            "interrupted": interrupted
        }


class SearchFlowCLI:
    def __init__(self):
        self.config = SearchFlowConfig()
        self.engine = SearchFlowEngine(self.config)

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="searchflow",
            description=f"{APP_NAME} - AI-Powered Research Platform. {__version__}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  searchflow "impact of AI on climate change mitigation"
  searchflow -t detailed -o formal "latest trends in quantum machine learning"
  searchflow --domains arxiv.org,nature.com,sciencemag.org "CRISPR gene editing ethics"
  searchflow --interactive                 # Start interactive mode
  searchflow --config                      # Configure default settings
  searchflow "Python web frameworks" --output report.md --format markdown

💬 Join our community: https://t.me/ArcAgents
For more help, visit {self.config.get("base_url", "https://github.com/ArcDevs/searchflow")}
{CREDITS}
            """
        )

        parser.add_argument("query", nargs="*", help="The research query. If empty and not in interactive mode, help is shown.")
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

        research_group = parser.add_argument_group('Research Options')
        type_choices = [info['api_value'] for info in REPORT_TYPES.values()] 
        type_help_list = "\n".join([f"    {v['api_value']}: {v['display']}" for k,v in REPORT_TYPES.items()])
        research_group.add_argument(
            "-t", "--type",
            choices=type_choices,
            default=REPORT_TYPES[self.config.get("report_type", "1")]["api_value"],
            help=f"Report type. Choices:\n{type_help_list}\n(default: %(default)s)"
        )

        tone_choices = [t.split(" - ")[0].lower() for t in TONES.values()]
        tone_help_list = "\n".join([f"    {t.split(' - ')[0].lower()}: {t}" for k,t in TONES.items()])
        research_group.add_argument(
            "-o", "--tone",
            choices=tone_choices,
            default=TONES[self.config.get("tone", "1")].split(" - ")[0].lower(),
            help=f"Report tone. Choices:\n{tone_help_list}\n(default: %(default)s)"
        )
        research_group.add_argument("-d", "--domains", nargs="+", metavar="DOMAIN", help="Filter search by specific domains (e.g., arxiv.org nature.com)")
        research_group.add_argument("--no-logs", action="store_true", help="Disable real-time streaming logs during research.")

        interface_group = parser.add_argument_group('Interface Options')
        interface_group.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode for multiple queries.")
        interface_group.add_argument("--config", action="store_true", help="Configure SearchFlow default settings (report type, tone).")

        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument("--output", "-O", metavar="FILEPATH", help="Save the generated report to a file.")
        output_group.add_argument("--format", choices=["text", "markdown", "json"], default="text",
                                  help="Output format for the saved file (default: text). JSON includes all metadata.")

        return parser

    async def run(self, cli_args=None):
        parser = self.create_parser()
        args = parser.parse_args(cli_args)

        if not hasattr(self, '_banner_printed'):
            print(APP_TITLE)
            print(CREDITS)
            print(SEPARATOR)
            self._banner_printed = True


        try:
            if args.config:
                await self._configure()
                return
            elif args.interactive:
                await self._interactive_mode()
            elif args.query:
                query_str = " ".join(args.query)
                
                selected_tone_api_value = args.tone.capitalize()
                api_tone = "Objective"
                for t_key, t_val in TONES.items():
                    if args.tone == t_val.split(" - ")[0].lower():
                        api_tone = t_val.split(" - ")[0]
                        break

                await self._single_search(query_str, args, report_type_api=args.type, tone_api=api_tone)
            else:
                parser.print_help()
                print(f"\n{C.YELLOW}Use 'searchflow --interactive' for interactive mode or 'searchflow <your query>' to search.{C.RESET}")


        except KeyboardInterrupt:
            print(f"\n{C.YELLOW}👋 SearchFlow interrupted. Exiting gracefully.{C.RESET}")
        except Exception as e:
            print(f"{ERROR_COLOR}❌ Unexpected CLI Error: {e}{C.RESET}")
            # traceback.print_exc() # Uncomment for debugging CLI errors

    async def _single_search(self, query: str, args, report_type_api: str, tone_api: str):
        """Perform a single search operation, maps args to engine call."""
        
        result = await self.engine.search(
            query=query,
            report_type=report_type_api,
            tone=tone_api,              
            domains=args.domains or self.config.get("domains", []),
            show_logs=not args.no_logs and self.config.get("show_logs", True)
        )

        if result and args.output:
            await self._save_output(result, args.output, args.format)
        elif result and not result.get("success") and not result.get("interrupted"):
            print(f"{C.YELLOW}⚠️ Search completed but no definitive report or download links were generated.{C.RESET}")


    async def _interactive_mode(self):
        print(f"{C.BOLD}{C.MAGENTA}🎯 Interactive Mode Started{C.RESET}")
        print(f"{C.YELLOW}Type your query, or 'config', 'help', 'set [option] [value]', 'quit'.{C.RESET}")

        current_report_type_api = REPORT_TYPES[self.config.get("report_type", "1")]["api_value"]
        current_tone_api = TONES[self.config.get("tone", "1")].split(" - ")[0]
        current_domains = self.config.get("domains", [])
        current_show_logs = self.config.get("show_logs", True)


        while True:
            try:
                raw_input_str = input(f"\n{PROMPT_COLOR}SearchFlow ({current_report_type_api}/{current_tone_api})> {C.RESET}").strip()

                if not raw_input_str:
                    continue

                command_parts = raw_input_str.lower().split(maxsplit=2)
                command = command_parts[0]

                if command in ["quit", "exit", "q"]:
                    print(f"{C.YELLOW}👋 Exiting Interactive Mode. Goodbye!{C.RESET}")
                    break
                elif command == "help":
                    self._show_interactive_help()
                elif command == "config":
                    await self._configure()
                    current_report_type_api = REPORT_TYPES[self.config.get("report_type", "1")]["api_value"]
                    current_tone_api = TONES[self.config.get("tone", "1")].split(" - ")[0]
                    current_domains = self.config.get("domains", [])

                elif command == "set":
                    if len(command_parts) < 3:
                        print(f"{ERROR_COLOR}Usage: set <option> <value>{C.RESET} (e.g., set type summary, set tone formal, set domains arxiv.org,nature.com)")
                        continue
                    option, value = command_parts[1], command_parts[2]
                    if option == "type":
                        valid_types_api = [info['api_value'] for info in REPORT_TYPES.values()]
                        if value in valid_types_api:
                            current_report_type_api = value
                            print(f"{SUCCESS_COLOR}Report type set to: {value}{C.RESET}")
                        else:
                            print(f"{ERROR_COLOR}Invalid type. Valid: {', '.join(valid_types_api)}{C.RESET}")
                    elif option == "tone":
                        valid_tones_api = [t.split(" - ")[0] for t in TONES.values()]
                        cli_value_lower = value.lower()
                        found_tone = None
                        for t_api in valid_tones_api:
                            if t_api.lower() == cli_value_lower:
                                found_tone = t_api
                                break
                        if found_tone:
                            current_tone_api = found_tone
                            print(f"{SUCCESS_COLOR}Tone set to: {found_tone}{C.RESET}")
                        else:
                            print(f"{ERROR_COLOR}Invalid tone. Valid: {', '.join(t.lower() for t in valid_tones_api)}{C.RESET}")
                    elif option == "domains":
                        current_domains = [d.strip() for d in value.split(',')]
                        print(f"{SUCCESS_COLOR}Domains set to: {', '.join(current_domains) if current_domains else 'Any'}{C.RESET}")
                    elif option == "logs":
                        if value in ["on", "true", "yes"]: current_show_logs = True
                        elif value in ["off", "false", "no"]: current_show_logs = False
                        else: print(f"{ERROR_COLOR}Invalid logs value. Use on/off, true/false, yes/no.{C.RESET}")
                        print(f"{SUCCESS_COLOR}Show logs set to: {'On' if current_show_logs else 'Off'}{C.RESET}")

                    else:
                        print(f"{ERROR_COLOR}Unknown option '{option}'. Valid: type, tone, domains, logs.{C.RESET}")

                else:
                    # Check if user is trying to use CLI commands in interactive mode
                    if raw_input_str.startswith("sf ") or raw_input_str.startswith("searchflow "):
                        print(f"{ERROR_COLOR}❌ Don't use 'sf' or 'searchflow' prefix in interactive mode. Just type the command directly.{C.RESET}")
                        print(f"{C.YELLOW}   Example: Instead of 'sf --config', just type 'config'{C.RESET}")
                        continue
                    
                    query = raw_input_str
                    await self.engine.search(
                        query,
                        report_type=current_report_type_api,
                        tone=current_tone_api,
                        domains=current_domains,
                        show_logs=current_show_logs
                    )

            except KeyboardInterrupt:
                print(f"\n{C.YELLOW}Use 'quit' or 'q' to exit interactive mode. Enter new query or command.{C.RESET}")
                continue
            except EOFError:
                print(f"\n{C.YELLOW}👋 Exiting Interactive Mode (EOF). Goodbye!{C.RESET}")
                break


    async def _configure(self):
        print(f"\n{C.BOLD}{C.CYAN}⚙️  SearchFlow Configuration (Defaults){C.RESET}")
        print(f"{C.WHITE}Current settings are saved to: {self.config.config_path}{C.RESET}")

        # Report type
        print(f"\n{C.YELLOW}1. Default Report Type:{C.RESET}")
        current_default_type_key = self.config.get("report_type", "1")
        for key, info in REPORT_TYPES.items():
            is_current = "✓" if key == current_default_type_key else " "
            print(f"  {is_current} [{key}] {info['display']}")
        try:
            choice = input(f"Select default report type key [{current_default_type_key}]: ").strip()
            if choice in REPORT_TYPES:
                self.config.set("report_type", choice)
            elif not choice: 
                pass
            else:
                print(f"{ERROR_COLOR}Invalid selection.{C.RESET}")
        except (KeyboardInterrupt, EOFError): print(f"\n{C.YELLOW}Configuration aborted.{C.RESET}"); return


        # Tone
        print(f"\n{C.YELLOW}2. Default Report Tone:{C.RESET}")
        current_default_tone_key = self.config.get("tone", "1")
        for key, desc in TONES.items():
            is_current = "✓" if key == current_default_tone_key else " "
            print(f"  {is_current} [{key}] {desc}")
        try:
            choice = input(f"Select default tone key [{current_default_tone_key}]: ").strip()
            if choice in TONES:
                self.config.set("tone", choice)
            elif not choice:
                pass
            else:
                print(f"{ERROR_COLOR}Invalid selection.{C.RESET}")
        except (KeyboardInterrupt, EOFError): print(f"\n{C.YELLOW}Configuration aborted.{C.RESET}"); return

        # Show logs
        print(f"\n{C.YELLOW}3. Default for Showing Real-time Logs:{C.RESET}")
        current_show_logs = self.config.get("show_logs", True)
        choice = input(f"Show logs by default? (yes/no) [{'yes' if current_show_logs else 'no'}]: ").strip().lower()
        if choice in ["yes", "y", "true", "t", "1"]: self.config.set("show_logs", True)
        elif choice in ["no", "n", "false", "f", "0"]: self.config.set("show_logs", False)
        elif not choice: pass
        else: print(f"{ERROR_COLOR}Invalid selection.{C.RESET}")


        print(f"\n{SUCCESS_COLOR}✅ Configuration saved to {self.config.config_path}!{C.RESET}")


    def _show_interactive_help(self):
        print(f"\n{C.BOLD}{C.CYAN}SearchFlow Interactive Mode Help{C.RESET}")
        print(f"""
{C.BOLD}Commands:{C.RESET}
  <your query>          - Perform a research task with current settings.
  set type <type>       - Set report type for this session (e.g., set type summary).
                          Valid types: {', '.join(info['api_value'] for info in REPORT_TYPES.values())}.
  set tone <tone>       - Set report tone for this session (e.g., set tone formal).
                          Valid tones: {', '.join(t.split(" - ")[0].lower() for t in TONES.values())}.
  set domains <d1,d2>   - Set domains for this session (e.g., set domains arxiv.org,nature.com). Leave empty to clear.
  set logs <on|off>     - Toggle real-time logs for this session.
  config                - Configure and save default settings for future sessions.
  help                  - Show this help message.
  quit / q / exit       - Exit interactive mode.

{C.BOLD}Current Settings (Interactive Session Only):{C.RESET}
  You can see current type/tone in the prompt: SearchFlow (type/tone)>
  To change defaults permanently, use 'config'.
        """)


    async def _save_output(self, result: Dict, filename: str, format_type: str):
        try:
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            content_to_save = ""
            if format_type == "json":
                content_to_save = json.dumps(result, indent=2, ensure_ascii=False)
            elif format_type == "markdown":
                content_to_save = self._format_markdown(result)
            else:
                content_to_save = result.get("report", "")
                if not content_to_save and result.get("download_links"):
                    content_to_save += "No direct text report generated in stream.\n\nDownload links:\n"
                    for ft, link in result["download_links"].items():
                        content_to_save += f"- {ft.upper()}: {link}\n"
                if not content_to_save:
                    content_to_save = "No report content or download links found in the result."


            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content_to_save)

            print(f"{SUCCESS_COLOR}✅ Report saved to: {os.path.abspath(filename)}{C.RESET}")
        except Exception as e:
            print(f"{ERROR_COLOR}❌ Error saving file to '{filename}': {e}{C.RESET}")
            # traceback.print_exc() # For debugging saving errors


    def _format_markdown(self, result: Dict) -> str:
        query = result.get("query", "N/A")
        report_type = result.get("report_type", "N/A") 
        tone = result.get("tone", "N/A")

        md = f"# SearchFlow Research Report\n\n"
        md += f"**Query:** `{query}` (Placeholder - actual query not in result dict yet)\n"
        md += f"**Report Type:** {report_type}\n"
        md += f"**Tone:** {tone}\n"
        md += f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        md += f"**Duration:** {result.get('duration', 0):.2f} seconds\n"
        md += f"**Messages Processed:** {result.get('message_count', 0)}\n\n"

        if result.get('interrupted'):
            md += "⚠️ **Note:** This report generation was interrupted and may be incomplete.\n\n"

        if result.get('sources'):
            md += "## 📚 Sources\n\n"
            for i, source_url in enumerate(result['sources'], 1):
                md += f"{i}. <{source_url}>\n" 
            md += "\n"

        if result.get('download_links'):
            md += "## 🔗 Download Links\n\n"
            for file_type, link in result['download_links'].items():
                md += f"- **{file_type.upper()}:** <{link}>\n"
            md += "\n"

        md += "## 📄 Report Text\n\n"
        report_text = result.get('report', '').strip()
        if report_text:
            md += "```text\n"
            md += report_text
            md += "\n```\n"
        elif result.get('download_links'):
            md += "No direct text report was generated in the stream. Please use the download links above.\n"
        else:
            md += "No report text or download links were generated.\n"

        md += f"\n---\n*Generated by {APP_NAME} v{__version__}*"
        return md

def main():
    """Main entry point for the SearchFlow CLI"""
    if sys.platform == "win32" and sys.version_info >= (3,8):
         asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    cli = SearchFlowCLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}👋 SearchFlow process terminated by user.{C.RESET}")
    except Exception as e:
        print(f"{ERROR_COLOR}❌ A critical error occurred: {e}{C.RESET}")

if __name__ == "__main__":
    main()