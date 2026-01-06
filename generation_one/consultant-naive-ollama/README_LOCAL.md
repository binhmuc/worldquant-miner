# Running Locally on Windows (Without Docker)

## 🚀 Super Quick Start

1. **First Time Setup:**
   ```cmd
   quick_start.bat
   ```
   This will guide you through everything!

2. **Already Setup? Just Run:**
   ```cmd
   run_local.bat
   ```

That's it! 🎉

---

## 📋 What You Need

- ✅ **Python 3.8+** - [Download](https://www.python.org/downloads/)
- ✅ **Ollama** - Already installed (you mentioned this!)
- ✅ **Cookie.txt** - Your WorldQuant Brain cookies

---

## 🎯 Three Simple Scripts

### 1. `quick_start.bat` - The Easiest Way
**Use this if it's your first time!**

Double-click and it will:
- Check everything is installed
- Create virtual environment
- Install Python packages
- Guide you through cookie setup
- Start the application

### 2. `setup_local.bat` - Setup Environment
**Run this once to prepare everything:**
- Creates Python virtual environment
- Installs all dependencies
- Checks Ollama is working
- Verifies cookie.txt exists

### 3. `run_local.bat` - Run the Application
**Use this after setup:**
- Interactive menu to choose what to run
- Start Alpha Orchestrator (main service)
- Start Machine Miner
- Start Web Dashboard
- Run all services at once

---

## 📝 Step-by-Step Guide

### Step 1: Get Your Cookie

Create a file called `cookie.txt` in this folder with your WorldQuant Brain cookies.

**Quick Method:**
1. Go to https://platform.worldquantbrain.com and login
2. Press F12 → Application → Cookies
3. Copy all cookies as: `key1=value1; key2=value2; ...`
4. Paste into `cookie.txt`

📖 **Detailed guide:** [COOKIE_AUTH.md](COOKIE_AUTH.md)

### Step 2: Run Setup

```cmd
setup_local.bat
```

This takes 2-5 minutes depending on your internet speed.

### Step 3: Start the Application

```cmd
run_local.bat
```

Choose from the menu:
- **Option 1**: Main service (continuous alpha generation)
- **Option 4**: Web dashboard (http://localhost:5000)
- **Option 7**: Start everything

---

## 🎮 Main Menu Options

When you run `run_local.bat`, you'll see:

```
1. Alpha Orchestrator (Continuous)  ← Main service
2. Alpha Orchestrator (Single Batch)
3. Machine Miner
4. Web Dashboard                    ← Monitor at http://localhost:5000
5. Health Check                     ← Test if everything works
6. Alpha Expression Miner
7. Run All Services                 ← Open everything at once
8. Install/Update Models            ← Manage Ollama models
9. Exit
```

**Most Common Usage:**
- Choose **1** for continuous alpha generation
- Choose **4** to see results in web browser
- Choose **7** to run everything

---

## 📊 What Each Service Does

### Alpha Orchestrator (Option 1)
The main service that:
- Generates alpha expressions using AI
- Tests them against historical data
- Saves successful ones to `results/`

**Best for:** Continuous alpha discovery

### Machine Miner (Option 3)
Traditional alpha mining:
- Uses systematic parameter combinations
- Targets specific regions/universes
- Good for thorough coverage

**Best for:** Systematic exploration

### Web Dashboard (Option 4)
Web interface showing:
- Generated alphas
- Success rates
- System status
- Real-time logs

**Access:** http://localhost:5000

---

## 🛠️ Troubleshooting

### "Python is not recognized"
**Solution:** Install Python and check "Add to PATH"
- Download: https://www.python.org/downloads/

### "Ollama is not running"
**Solution:** Start Ollama
```cmd
ollama serve
```

### "cookie.txt not found"
**Solution:** Create it! See [COOKIE_AUTH.md](COOKIE_AUTH.md)

### "Authentication failed"
**Solution:** Cookie expired, get a fresh one
1. Logout and login to WorldQuant Brain
2. Copy new cookies
3. Update cookie.txt

### "Model not found"
**Solution:** Install the model
```cmd
ollama pull deepseek-r1:8b
```

---

## 💡 Tips & Tricks

### Recommended Models for RTX A4000 (16GB VRAM)

```cmd
# Best performance
ollama pull deepseek-r1:8b      # 5.2GB - Recommended!

# Good alternatives
ollama pull deepseek-r1:7b      # 4.7GB
ollama pull qwen2.5-coder:7b    # 4.7GB
ollama pull llama3.2:3b         # 2.0GB - Lightweight
```

### Check What's Installed

```cmd
# Python packages
pip list

# Ollama models
ollama list

# System info
python --version
ollama --version
```

### View Logs

```cmd
# Windows Explorer
explorer logs

# View in notepad
notepad logs\alpha_orchestrator.log
```

### Results Location

All successful alphas saved to:
```
results/
  └── successful_alphas.json
  └── mined_expressions.json
  └── ...
```

---

## 🔄 Daily Usage

After initial setup, your daily workflow is simple:

1. **Start Ollama** (if not auto-running)
   ```cmd
   ollama serve
   ```

2. **Run the application**
   ```cmd
   run_local.bat
   ```

3. **Choose what to run**
   - Option 1 for continuous generation
   - Option 4 to monitor progress

4. **Let it run!** ☕
   - Check results in `results/` folder
   - View dashboard at http://localhost:5000

---

## 📈 Performance

**Expected Performance (RTX A4000):**
- Model loading: 5-10 seconds
- Alpha generation: 10-30 seconds per alpha
- Simulation: 30-60 seconds per test
- Batch of 10 alphas: ~15-30 minutes

**Tips for Better Performance:**
- Use `--max-concurrent 2` for parallel processing
- Use smaller batch sizes (2-5) for faster feedback
- Monitor GPU usage with Task Manager

---

## 🔧 Advanced Usage

### Run Specific Service Directly

```cmd
# Activate virtual environment first
call venv\Scripts\activate

# Then run any script
python alpha_orchestrator.py --mode continuous --batch-size 5
python machine_miner.py --credentials cookie.txt --region USA
python web_dashboard.py
```

### Custom Configuration

Edit the scripts to change:
- Model selection (alpha_orchestrator.py, line 47)
- Batch sizes (run_local.bat)
- Port numbers (web_dashboard.py)
- Mining parameters (machine_miner.py)

### Run on Startup

Create shortcut to `run_local.bat` in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

---

## 📚 Full Documentation

- **Local Setup Guide**: [LOCAL_SETUP.md](LOCAL_SETUP.md) - Complete guide
- **Cookie Authentication**: [COOKIE_AUTH.md](COOKIE_AUTH.md) - Cookie setup
- **Migration Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - From Docker

---

## ❓ Need Help?

1. **Run Health Check**
   ```cmd
   run_local.bat
   # Choose option 5
   ```

2. **Check Logs**
   ```
   logs\alpha_orchestrator.log
   logs\machine_miner.log
   ```

3. **Common Issues**: See [LOCAL_SETUP.md](LOCAL_SETUP.md) troubleshooting section

---

## 🎯 Quick Reference

```cmd
# First time setup
quick_start.bat

# Run application (interactive menu)
run_local.bat

# Direct execution
call venv\Scripts\activate
python alpha_orchestrator.py --mode continuous

# Install models
ollama pull deepseek-r1:8b

# Check status
ollama list
pip list
python health_check.py

# View results
explorer results
explorer logs

# Web dashboard
start http://localhost:5000
```

---

## ✅ Checklist

Before starting:
- [ ] Python 3.8+ installed
- [ ] Ollama installed and running
- [ ] cookie.txt created with your cookies
- [ ] Ran setup_local.bat
- [ ] At least one Ollama model installed

Ready to go? Run `run_local.bat`! 🚀

---

**Made with ❤️ for local execution on Windows**
