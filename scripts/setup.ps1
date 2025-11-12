Param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '==> Agentic App setup starting...' -ForegroundColor Green

function Ensure-Command($Name) {
    return (Get-Command $Name -ErrorAction SilentlyContinue) -ne $null
}

function Install-FFmpeg {
    if (Ensure-Command ffmpeg) {
        Write-Host 'ffmpeg already installed'
        return
    }

    Write-Host 'Installing ffmpeg...'
    if ($IsWindows) {
        if (Ensure-Command choco) {
            choco install -y ffmpeg
        } elseif (Ensure-Command winget) {
            winget install -e --id Gyan.FFmpeg
        } else {
            throw 'Please install Chocolatey (https://chocolatey.org) or Winget to install ffmpeg.'
        }
    } else {
        throw 'This script is for Windows. Use scripts/setup.sh for macOS/Linux.'
    }
}

function Install-PythonDeps {
    Write-Host 'Installing Python dependencies...'
    if (Ensure-Command uv) {
        uv pip install --upgrade pip
        if (Test-Path 'pyproject.toml') {
            uv pip install .[dev]
        } elseif (Test-Path 'requirements.txt') {
            uv pip install -r requirements.txt
        }
    } else {
        py -3 -m pip install --upgrade pip
        if (Test-Path 'pyproject.toml') {
            py -3 -m pip install .[dev]
        } elseif (Test-Path 'requirements.txt') {
            py -3 -m pip install -r requirements.txt
        }
    }
}

function Setup-PreCommit {
    Write-Host 'Setting up pre-commit hook...'
    if (-not (Ensure-Command pre-commit)) {
        py -3 -m pip install pre-commit
    }
    pre-commit install
    pre-commit run --all-files | Out-Null
}

Install-FFmpeg
Install-PythonDeps
Setup-PreCommit

Write-Host '==> Setup complete. You can now run: python ui.py' -ForegroundColor Green


