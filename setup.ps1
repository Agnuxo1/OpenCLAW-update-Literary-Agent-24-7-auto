# OpenCLAW Agent — Windows Setup Script
# Usage: .\setup.ps1

param(
    [string]$Command = "setup"
)

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenCLAW Autonomous Agent — Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

switch ($Command) {
    "setup" {
        # Check Python
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            Write-Host "ERROR: Python not found. Install Python 3.11+" -ForegroundColor Red
            exit 1
        }
        Write-Host "Python: $((python --version))" -ForegroundColor Green

        # Install dependencies
        Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
        pip install -r "$ProjectDir\requirements.txt"

        # Create .env if not exists
        if (-not (Test-Path "$ProjectDir\.env")) {
            Copy-Item "$ProjectDir\.env.example" "$ProjectDir\.env"
            Write-Host "`n.env created from template." -ForegroundColor Green
            Write-Host "IMPORTANT: Edit .env with your actual API keys!" -ForegroundColor Red
        }

        # Create state directory
        New-Item -ItemType Directory -Path "$ProjectDir\state" -Force | Out-Null

        Write-Host "`nSetup complete!" -ForegroundColor Green
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  1. Edit .env with your API keys"
        Write-Host "  2. python main.py once    # Test single cycle"
        Write-Host "  3. python main.py run     # Start 24/7 agent"
    }
    "test" {
        python "$ProjectDir\tests\test_smoke.py"
    }
    "run" {
        python "$ProjectDir\main.py" run
    }
    "status" {
        python "$ProjectDir\main.py" status
    }
    default {
        Write-Host "Usage: .\setup.ps1 [setup|test|run|status]"
    }
}
