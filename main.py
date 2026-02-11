"""
OpenCLAW Autonomous Agent — Main Entry Point
=============================================
Usage:
    python main.py run       # Start 24/7 autonomous operation
    python main.py once      # Run one cycle (testing)
    python main.py status    # Show agent status
    python main.py health    # Start health check server only
"""

import os
import sys
import logging
import threading
from datetime import datetime

from config import config
from core.autonomous_loop import AutonomousLoop

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level, logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(config.state_dir, "openclaw-agent.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("OpenCLAW")

# Ensure state directory exists
os.makedirs(config.state_dir, exist_ok=True)


def start_health_server():
    """Start a minimal HTTP health check server for Render/Railway."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health" or self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "status": "healthy",
                    "agent": config.identity.name,
                    "timestamp": datetime.now().isoformat(),
                    "uptime": "active",
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/metrics":
                from core.state_manager import StateManager
                state = StateManager(config.state_dir)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(state.get_metrics(), default=str).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass  # Suppress access logs

    port = config.port
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health server listening on port {port}")
    server.serve_forever()


def main():
    # Validate config
    warnings = config.validate()
    for w in warnings:
        logger.warning(f"Config: {w}")

    command = sys.argv[1] if len(sys.argv) > 1 else "run"

    if command == "run":
        # Start health server in background thread
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()

        # Start main agent loop
        loop = AutonomousLoop(config)
        loop.run()

    elif command == "once":
        loop = AutonomousLoop(config)
        loop.run_once()

    elif command == "status":
        from core.state_manager import StateManager
        from core.strategy_reflector import StrategyReflector
        state = StateManager(config.state_dir)
        reflector = StrategyReflector(state)
        print(reflector.get_status_report())

    elif command == "health":
        start_health_server()

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
