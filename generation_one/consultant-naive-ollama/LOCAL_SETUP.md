# Local Setup Guide (Windows)

This guide will help you run the WorldQuant Alpha Mining system locally on Windows **without Docker**, using your locally installed Ollama.

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation

2. **Ollama** (Already installed on your system)
   - Verify with: `ollama --version`
   - Should be running on `http://localhost:11434`

3. **Git** (Optional, for cloning the repository)
   - Download from: https://git-scm.com/downloads

### Optional but Recommended

- **CUDA** (for GPU acceleration with Ollama)
- **Visual Studio Code** (for editing files)

## Quick Start

### Step 1: Setup Environment

Run the setup script to prepare your environment:

```cmd
setup_local.bat
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install Python dependencies
- ✅ Create necessary directories (results/, logs/)
- ✅ Check Ollama installation
- ✅ Verify cookie.txt exists

### Step 2: Get Your Cookie

You need to create a `cookie.txt` file with your WorldQuant Brain authentication cookies.

#### Quick Method:
1. Open https://platform.worldquantbrain.com in your browser
2. Login to your account
3. Press **F12** to open Developer Tools
4. Go to **Application** tab → **Cookies** → `https://platform.worldquantbrain.com`
5. Copy all cookies in this format: `key1=value1; key2=value2; key3=value3`
6. Create `cookie.txt` file and paste the cookie string

#### Example cookie.txt:
```
_gcl_au=1.1.524283951.1766295055; _ga=GA1.1.17466726069820b83e5d6113c8; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; _ga_9RN6WVT1K1=GS2.1.s1767541796...
```

📖 **See [COOKIE_AUTH.md](COOKIE_AUTH.md) for detailed instructions**

### Step 3: Install Ollama Models

Install the recommended models for your GPU:

```cmd
# For RTX A4000 (16GB VRAM) - Recommended
ollama pull deepseek-r1:8b

# Alternative models
ollama pull deepseek-r1:7b       # 4.7GB
ollama pull qwen2.5-coder:7b     # 4.7GB
ollama pull llama3.2:3b          # 2.0GB
ollama pull gemma2:2b            # 1.6GB
```

Verify models are installed:
```cmd
ollama list
```

### Step 4: Run the Application

Use the interactive menu script:

```cmd
run_local.bat
```

This will show a menu with options:
1. **Alpha Orchestrator (Continuous)** - Main service for continuous alpha generation
2. **Alpha Orchestrator (Single Batch)** - Run one batch of alphas
3. **Machine Miner** - Traditional alpha mining
4. **Web Dashboard** - Web interface on port 5000
5. **Health Check** - Verify system is working
6. **Alpha Expression Miner** - Mine expression variations
7. **Run All Services** - Open all services in separate windows
8. **Install/Update Models** - Manage Ollama models
9. **Exit**

## Running Individual Services

### Alpha Orchestrator (Main Service)

The orchestrator is the main service that generates and tests alphas continuously.

**Continuous Mode:**
```cmd
python alpha_orchestrator.py --mode continuous --batch-size 2 --max-concurrent 2
```

**Single Batch Mode:**
```cmd
python alpha_orchestrator.py --mode single --batch-size 10
```

**Options:**
- `--mode`: `continuous` or `single`
- `--batch-size`: Number of alphas per batch (default: 10)
- `--max-concurrent`: Max concurrent simulations (default: 2)

### Machine Miner

Traditional alpha mining for specific regions/universes:

```cmd
python machine_miner.py --credentials cookie.txt --region USA --universe TOP3000
```

**Options:**
- `--region`: USA, GLB, EUR, ASI, CHN
- `--universe`: TOP3000, TOP1000, TOP500, etc.

### Web Dashboard

Web interface for monitoring alpha generation:

```cmd
python web_dashboard.py
```

Access at: http://localhost:5000

### Alpha Expression Miner

Mine variations of successful alphas:

```cmd
python alpha_expression_miner_continuous.py --credentials cookie.txt --mining-interval 6
```

**Options:**
- `--mining-interval`: Hours between mining cycles (default: 6)

## Running All Services Together

To run all services simultaneously in separate windows:

```cmd
# Using the menu
run_local.bat
# Then select option 7

# Or manually open separate terminals for each:
# Terminal 1:
python alpha_orchestrator.py --mode continuous --batch-size 2 --max-concurrent 2

# Terminal 2:
python machine_miner.py --credentials cookie.txt --region USA --universe TOP3000

# Terminal 3:
python web_dashboard.py
```

## Directory Structure

```
consultant-naive-ollama/
├── run_local.bat              # Main execution script (interactive menu)
├── setup_local.bat            # Setup environment script
├── cookie.txt                 # Your WorldQuant cookies (create this)
├── requirements.txt           # Python dependencies
├── venv/                      # Virtual environment (created by setup)
├── results/                   # Alpha results saved here
├── logs/                      # Log files
│   ├── alpha_orchestrator.log
│   ├── machine_miner.log
│   └── ...
├── alpha_orchestrator.py      # Main orchestrator
├── machine_miner.py           # Traditional miner
├── web_dashboard.py           # Web interface
└── credential_manager.py      # Cookie authentication manager
```

## Configuration

### Environment Variables

You can set these in your terminal before running:

```cmd
# Ollama configuration
set OLLAMA_HOST=0.0.0.0
set OLLAMA_GPU_LAYERS=20
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_GPU_MEMORY_UTILIZATION=0.8

# Python configuration
set PYTHONUNBUFFERED=1

# CUDA configuration (for GPU)
set CUDA_VISIBLE_DEVICES=0
```

### Modifying Scripts

Edit the Python files to customize behavior:

**alpha_orchestrator.py:**
- Line 47-53: Model fleet configuration
- Line 258+: Main orchestrator settings

**machine_miner.py:**
- Region and universe settings

**web_dashboard.py:**
- Port configuration (default: 5000)

## Troubleshooting

### Python Issues

**Problem:** `Python is not recognized`
```cmd
# Solution: Add Python to PATH
# 1. Find Python installation (usually C:\Users\YourName\AppData\Local\Programs\Python\Python3X)
# 2. Add to PATH in System Environment Variables
```

**Problem:** `Failed to create virtual environment`
```cmd
# Solution: Install venv module
python -m pip install --user virtualenv
```

### Ollama Issues

**Problem:** `Ollama is not running`
```cmd
# Solution 1: Start Ollama service
ollama serve

# Solution 2: Restart Ollama
# Close Ollama from system tray and restart from Start Menu
```

**Problem:** `Model not found`
```cmd
# Solution: Pull the model
ollama pull deepseek-r1:8b

# List available models
ollama list
```

**Problem:** `VRAM out of memory`
```cmd
# Solution: Use smaller model
ollama pull gemma2:2b  # Only 1.6GB

# Or reduce GPU layers
set OLLAMA_GPU_LAYERS=10
```

### Cookie Authentication Issues

**Problem:** `Authentication failed`
```
# Solution: Get fresh cookies
1. Logout from WorldQuant Brain
2. Login again
3. Copy new cookies from browser
4. Update cookie.txt
```

**Problem:** `Cookie file not found`
```cmd
# Solution: Create cookie.txt in project directory
echo your_cookie_string_here > cookie.txt
```

### Network Issues

**Problem:** `Connection timeout`
```cmd
# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# Check if WorldQuant API is accessible
curl https://api.worldquantbrain.com/users/self
```

### Import Errors

**Problem:** `ModuleNotFoundError`
```cmd
# Solution: Reinstall dependencies
pip install -r requirements.txt

# Or specific package
pip install requests pandas torch
```

## Performance Tips

### GPU Optimization

1. **Monitor VRAM usage:**
   ```cmd
   # Use Task Manager > Performance > GPU
   # Or install: nvidia-smi
   ```

2. **Adjust model size** based on VRAM:
   - 16GB VRAM: deepseek-r1:8b (5.2GB)
   - 8GB VRAM: qwen2.5-coder:7b or llama3.2:3b
   - 4GB VRAM: gemma2:2b (1.6GB)

3. **Reduce concurrent operations:**
   ```cmd
   python alpha_orchestrator.py --max-concurrent 1
   ```

### CPU Optimization

If running on CPU only:
```cmd
set OLLAMA_NUM_PARALLEL=2
python alpha_orchestrator.py --batch-size 5
```

### Disk Space

- Each model: 1-5GB
- Logs grow over time
- Results directory grows with alphas

**Clean up old logs:**
```cmd
del /Q logs\*.log.old
```

## Monitoring

### View Logs

```cmd
# Real-time log viewing (PowerShell)
Get-Content logs\alpha_orchestrator.log -Wait -Tail 50

# Or use Notepad++, VSCode, etc.
notepad logs\alpha_orchestrator.log
```

### Check Results

```cmd
# View results directory
dir results

# View specific result file
type results\successful_alphas.json
```

### Web Dashboard

Access the web dashboard at http://localhost:5000 to:
- View generated alphas
- See success rates
- Monitor system health
- Check logs in real-time

## Scheduled Execution

### Run on Windows Startup

Create a shortcut to `run_local.bat` and place it in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Task Scheduler

Use Windows Task Scheduler to run at specific times:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 9 AM)
4. Action: Start a program → `run_local.bat`

## Stopping Services

### Stop Running Service

- Press **Ctrl+C** in the terminal
- Or close the terminal window

### Stop All Services

If you started all services (option 7), close each window individually.

### Emergency Stop

```cmd
# Kill all Python processes (use with caution!)
taskkill /F /IM python.exe

# Kill specific script
taskkill /F /FI "WINDOWTITLE eq Alpha Orchestrator*"
```

## Updating

### Update Code

```cmd
# If using Git
git pull origin main

# Or download latest version manually
```

### Update Dependencies

```cmd
# Activate virtual environment
call venv\Scripts\activate

# Update all packages
pip install --upgrade -r requirements.txt
```

### Update Ollama Models

```cmd
# Update all models
ollama pull deepseek-r1:8b
ollama pull deepseek-r1:7b
# ... etc
```

## Comparison: Docker vs Local

| Aspect | Docker | Local |
|--------|--------|-------|
| **Setup** | Complex | Simple |
| **Ollama** | Bundled | Use existing |
| **Performance** | Slight overhead | Native |
| **Resource Usage** | Higher | Lower |
| **Updates** | Rebuild image | Just git pull |
| **Debugging** | Harder | Easier |
| **Isolation** | Better | None |

## Next Steps

1. ✅ Setup complete? → Run `run_local.bat`
2. ✅ Cookie configured? → Check [COOKIE_AUTH.md](COOKIE_AUTH.md)
3. ✅ Models installed? → Run `ollama list`
4. ✅ Everything working? → Start generating alphas!

## Getting Help

- **Cookie Authentication**: See [COOKIE_AUTH.md](COOKIE_AUTH.md)
- **Migration from Docker**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Cookie Implementation**: See [COOKIE_IMPLEMENTATION_SUMMARY.md](COOKIE_IMPLEMENTATION_SUMMARY.md)
- **Health Check**: Run `python health_check.py`

## Additional Resources

- **WorldQuant Brain**: https://platform.worldquantbrain.com
- **Ollama**: https://ollama.com
- **Python**: https://www.python.org
- **DeepSeek Models**: https://ollama.com/library/deepseek-r1

---

**Ready to start?** Run `setup_local.bat` and then `run_local.bat`! 🚀
