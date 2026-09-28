from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def write_nginx_config(
    config_path: Path,
    ports: list[int],
) -> None:
    servers = "\n".join(
        f"        server 127.0.0.1:{port};"
        for port in ports
    )

    config = f"""
worker_processes 1;

events {{
    worker_connections 1024;
}}

http {{
    upstream ai_backend {{
        least_conn;
{servers}
    }}

    server {{
        listen 8000;

        location / {{
            proxy_pass http://ai_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Preserve streaming responses.
            proxy_buffering off;
            proxy_cache off;
            proxy_read_timeout 300s;
        }}
    }}
}}
""".strip()

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config, encoding="utf-8")


def wait_until_healthy(
    ports: list[int],
    processes: list[subprocess.Popen],
    timeout_seconds: int = 120,
) -> None:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        for process in processes:
            if process.poll() is not None:
                raise RuntimeError(
                    f"An API process exited with code {process.returncode}."
                )

        all_healthy = True

        for port in ports:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/health",
                    timeout=2,
                ) as response:
                    if response.status != 200:
                        all_healthy = False
            except (OSError, urllib.error.URLError):
                all_healthy = False

        if all_healthy:
            return

        time.sleep(1)

    raise TimeoutError("API instances did not become healthy in time.")


def stop_processes(
    processes: list[subprocess.Popen],
) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        if process.poll() is None:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run multiple local API instances behind Nginx."
    )
    parser.add_argument(
        "--instances",
        type=int,
        choices=(2, 4, 8),
        required=True,
    )
    parser.add_argument(
        "--nginx-exe",
        required=True,
        help=r"Full path to nginx.exe, for example C:\nginx\nginx.exe",
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable to use for Uvicorn.",
    )
    parser.add_argument(
        "--base-port",
        type=int,
        default=8001,
    )
    parser.add_argument(
        "--nginx-config",
        default="scale-nginx.conf",
    )

    args = parser.parse_args()

    nginx_exe = Path(args.nginx_exe).resolve()
    python_exe = Path(args.python_exe).resolve()
    config_path = Path(args.nginx_config).resolve()

    if not nginx_exe.is_file():
        parser.error(f"Nginx executable not found: {nginx_exe}")

    if not python_exe.is_file():
        parser.error(f"Python executable not found: {python_exe}")

    ports = [
        args.base_port + index
        for index in range(args.instances)
    ]

    write_nginx_config(config_path, ports)

    nginx_cwd = nginx_exe.parent
    subprocess.run(
        [str(nginx_exe), "-t", "-c", str(config_path)],
        cwd=nginx_cwd,
        check=True,
    )

    api_processes: list[subprocess.Popen] = []
    log_handles = []
    nginx_started = False

    try:
        for index, port in enumerate(ports):
            instance_env = os.environ.copy()

            # Run scheduled jobs on only one of the API instances.
            instance_env["ENABLE_BACKGROUND_SCHEDULERS"] = (
                "true" if index == 0 else "false"
            )

            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_handle = (log_dir / f"api-{port}.log").open(
                "a",
                encoding="utf-8",
            )
            log_handles.append(log_handle)

            process = subprocess.Popen(
                [
                    str(python_exe),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                env=instance_env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            api_processes.append(process)

        wait_until_healthy(ports, api_processes)

        subprocess.Popen(
            [
                str(nginx_exe),
                "-c",
                str(config_path),
            ],
            cwd=nginx_cwd,
        )
        nginx_started = True

        print(
            f"{args.instances} API instances are ready behind Nginx."
        )
        print("Base URL: http://127.0.0.1:8000")
        print("Press Ctrl+C to stop the instances.")

        while True:
            for process in api_processes:
                if process.poll() is not None:
                    raise RuntimeError(
                        "An API instance exited. Check its log in ./logs."
                    )
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping API instances...")
    finally:
        if nginx_started:
            subprocess.run(
                [str(nginx_exe), "-c", str(config_path), "-s", "quit"],
                cwd=nginx_cwd,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        stop_processes(api_processes)

        for log_handle in log_handles:
            log_handle.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())