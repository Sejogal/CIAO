"""
Windows-only dev entrypoint. `python -m uvicorn app.main:app` lets uvicorn
create its event loop (ProactorEventLoop, Windows' asyncio default) before
app/main.py is ever imported, so setting the loop policy there is too
late. Setting it here, before uvicorn itself is imported, is not.

ProactorEventLoop doesn't implement add_reader/add_writer, which aiomqtt
needs - without the selector policy the MQTT background task silently
fails to connect on every attempt. Linux (every real deployment) doesn't
have this problem, so production just runs `uvicorn app.main:app`
directly - this script is local dev convenience only.

Usage: venv/Scripts/python.exe run_dev.py [--port 8000] [--no-reload]
"""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import argparse

import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=args.port,
        reload=not args.no_reload,
    )
