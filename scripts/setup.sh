#!/usr/bin/env bash
set -euo pipefail

echo "==> Agentic App setup starting..."

# Detect OS
OS="$(uname -s || echo unknown)"
echo "Detected OS: ${OS}"

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    return 1
  fi
}

install_ffmpeg() {
  if ensure_command ffmpeg; then
    echo "ffmpeg already installed"
    return
  fi
  echo "Installing ffmpeg..."
  case "$OS" in
    Darwin)
      if ensure_command brew; then
        brew install ffmpeg
      else
        echo "Homebrew not found. Please install Homebrew: https://brew.sh/"; exit 1
      fi
      ;;
    Linux)
      if ensure_command apt-get; then
        sudo apt-get update -y && sudo apt-get install -y ffmpeg
      elif ensure_command yum; then
        sudo yum install -y epel-release && sudo yum install -y ffmpeg
      else
        echo "Unsupported Linux package manager. Install ffmpeg manually."; exit 1
      fi
      ;;
    *)
      echo "Unknown OS for ffmpeg install. Please install ffmpeg manually."; exit 1
      ;;
  esac
}

install_python_deps() {
  echo "Installing Python dependencies..."
  if ensure_command uv; then
    # Prefer uv if available
    uv pip install --upgrade pip
    if [ -f "pyproject.toml" ]; then
      uv pip install .[dev]
    elif [ -f "requirements.txt" ]; then
      uv pip install -r requirements.txt
    fi
  else
    python3 -m pip install --upgrade pip
    if [ -f "pyproject.toml" ]; then
      python3 -m pip install .[dev]
    elif [ -f "requirements.txt" ]; then
      python3 -m pip install -r requirements.txt
    fi
  fi
}

setup_pre_commit() {
  echo "Setting up pre-commit hook..."
  if ! ensure_command pre-commit; then
    python3 -m pip install pre-commit
  fi
  pre-commit install
  # Optional initial run across the repo
  pre-commit run --all-files || true
}

main() {
  install_ffmpeg
  install_python_deps
  setup_pre_commit
  echo "==> Setup complete. You can now run: python3 ui.py"
}

main "$@"


