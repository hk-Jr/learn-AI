import os
import sys
import subprocess
import time
import signal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def get_python_exe():
    venv_py = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable

def main():
    print("=" * 70)
    print(" Intelligent Knowledge Retrieval & Question Answering System (RAG)")
    print("=" * 70)

    python_exe = get_python_exe()
    print(f"[Launcher] Using Python executable: {python_exe}")

    # 1. Start backend process
    print("[Launcher] Starting FastAPI Backend on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BACKEND_DIR)
    )

    # 2. Wait a moment for backend to initialize
    time.sleep(2)

    # 3. Start frontend process
    print("[Launcher] Starting Vite Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"],
        cwd=str(FRONTEND_DIR)
    )

    print("-" * 70)
    print(" [READY] Application is live!")
    print(" -> Frontend:       http://localhost:5173")
    print(" -> Backend API:    http://localhost:8000")
    print(" -> Swagger Docs:   http://localhost:8000/docs")
    print("-" * 70)
    print(" Press Ctrl+C in this terminal to shut down both services.")
    print("-" * 70)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[Launcher] Backend stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[Launcher] Frontend stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n[Launcher] Shutting down services...")
    finally:
        for proc in [frontend_proc, backend_proc]:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("[Launcher] All services terminated.")

if __name__ == "__main__":
    main()

