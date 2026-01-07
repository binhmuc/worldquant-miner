from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
import time
import subprocess
import threading
from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, List, Optional
from pathlib import Path
from credential_manager import CredentialManager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlphaDashboard:
    def __init__(self):
        self.status_file = "dashboard_status.json"
        self.log_file = "alpha_orchestrator.log"
        self.submission_log_file = "submission_log.json"
        self.results_dir = "results"
        self.logs_dir = "logs"
        
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "gpu": self.get_gpu_status(),
            "ollama": self.get_ollama_status(),
            "orchestrator": self.get_orchestrator_status(),
            "worldquant": self.get_worldquant_status(),
            "recent_activity": self.get_recent_activity(),
            "statistics": self.get_statistics()
        }
        return status
    
    def get_gpu_status(self) -> Dict:
        """Get GPU status and utilization."""
        try:
            # Try to get GPU info from nvidia-smi
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    parts = lines[0].split(', ')
                    if len(parts) >= 5:
                        return {
                            "status": "active",
                            "name": parts[0],
                            "memory_used_mb": int(parts[1]),
                            "memory_total_mb": int(parts[2]),
                            "utilization_percent": int(parts[3]),
                            "temperature_c": int(parts[4]),
                            "memory_percent": round((int(parts[1]) / int(parts[2])) * 100, 1)
                        }
        except Exception as e:
            logger.warning(f"Could not get GPU status: {e}")
        
        return {"status": "unknown", "error": "GPU information not available"}
    
    def get_ollama_status(self) -> Dict:
        """Get Ollama service status."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return {
                    "status": "running",
                    "models": [model.get("name", "") for model in models],
                    "model_count": len(models)
                }
        except Exception as e:
            logger.warning(f"Could not get Ollama status: {e}")
        
        return {"status": "not_responding", "error": "Ollama service not available"}
    
    def get_orchestrator_status(self) -> Dict:
        """Get orchestrator status from Docker container logs or local process."""
        status = {
            "status": "unknown",
            "last_activity": None,
            "current_mode": "continuous",
            "next_mining": None,
            "next_submission": None
        }

        try:
            # First, check if orchestrator is running as a local process
            is_running = False
            try:
                if os.name == 'nt':  # Windows
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                                          capture_output=True, text=True, timeout=5)
                    if 'alpha_orchestrator' in result.stdout:
                        is_running = True
                else:  # Linux/Mac
                    result = subprocess.run(['pgrep', '-f', 'alpha_orchestrator.py'],
                                          capture_output=True, text=True, timeout=5)
                    if result.stdout.strip():
                        is_running = True
            except:
                pass

            # Check log file for recent activity
            log_file = 'alpha_orchestrator.log'
            if os.path.exists(log_file):
                try:
                    # Check file modification time
                    mtime = os.path.getmtime(log_file)
                    current_time = time.time()
                    time_diff = current_time - mtime

                    # Read last 50 lines of log
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_lines = lines[-50:] if len(lines) > 50 else lines

                        if recent_lines:
                            last_line = recent_lines[-1].strip()
                            status["last_activity"] = last_line

                            # If log was updated in last 5 minutes and process is running
                            if time_diff < 300 and is_running:
                                status["status"] = "active"
                            elif time_diff < 300:
                                status["status"] = "idle"
                            elif is_running:
                                status["status"] = "stale"
                            else:
                                status["status"] = "stopped"

                            # Check for errors in recent logs
                            for line in reversed(recent_lines):
                                if any(keyword in line for keyword in ["alpha generator", "generating alpha", "Running alpha", "Started alpha"]):
                                    if status["status"] == "unknown":
                                        status["status"] = "active"
                                    break
                                elif any(keyword in line for keyword in ["Error", "FATAL", "Exception", "Failed"]) and "INFO" not in line:
                                    status["status"] = "error"
                                    break
                except Exception as e:
                    logger.warning(f"Error reading log file: {e}")
            elif is_running:
                status["status"] = "starting"

            # Also try Docker container if local process not found
            if status["status"] == "unknown":
                try:
                    result = subprocess.run([
                        "docker", "logs", "--tail", "50", "naive-ollma-gpu"
                    ], capture_output=True, text=True, timeout=10)

                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0]:
                            status["status"] = "active_docker"
                            status["last_activity"] = lines[-1].strip() if lines else None
                except:
                    pass

            # Check submission schedule (outside Docker check)
            if os.path.exists(self.submission_log_file):
                try:
                    with open(self.submission_log_file, 'r') as f:
                        data = json.load(f)
                        last_submission = data.get("last_submission_date")
                        if last_submission:
                            last_date = datetime.fromisoformat(last_submission)
                            next_submission = last_date + timedelta(days=1)
                            next_submission = next_submission.replace(hour=14, minute=0, second=0, microsecond=0)
                            status["next_submission"] = next_submission.isoformat()
                except Exception as e:
                    logger.warning(f"Error reading submission log: {e}")

            # Calculate next mining time (every 6 hours)
            try:
                now = datetime.now()
                hours_since_midnight = now.hour + now.minute / 60
                next_mining_hour = ((int(hours_since_midnight // 6) + 1) * 6) % 24
                next_mining = now.replace(hour=int(next_mining_hour), minute=0, second=0, microsecond=0)
                if next_mining <= now:
                    next_mining += timedelta(days=1)
                status["next_mining"] = next_mining.isoformat()
            except Exception as e:
                logger.warning(f"Error calculating next mining time: {e}")
                
        except Exception as e:
            logger.warning(f"Could not get orchestrator status: {e}")
        
        return status
    
    def get_worldquant_status(self) -> Dict:
        """Check WorldQuant Brain API status using cookie authentication."""
        try:
            cookie_file = Path("cookie.txt")
            if cookie_file.exists():
                credential_manager = CredentialManager()
                if credential_manager.load_from_file(cookie_file):
                    if credential_manager.validate_credentials():
                        return {"status": "connected", "message": "Authentication successful"}
                    else:
                        return {"status": "auth_failed", "message": "Cookie validation failed"}
                else:
                    return {"status": "error", "message": "Failed to load cookie"}
            else:
                return {"status": "no_credentials", "message": "cookie.txt not found"}
        except Exception as e:
            logger.warning(f"Could not check WorldQuant status: {e}")

        return {"status": "unknown", "message": "Could not verify connection"}
    
    def get_recent_activity(self) -> List[Dict]:
        """Get recent activity from local log files or Docker container logs."""
        activities = []

        try:
            # Try local log file first
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        line = line.strip()
                        if line and not line.startswith('---'):
                            try:
                                if ' - ' in line:
                                    parts = line.split(' - ', 2)
                                    if len(parts) >= 3:
                                        timestamp_str = parts[0]
                                        level = parts[1]
                                        message = parts[2]
                                        activities.append({
                                            "timestamp": timestamp_str,
                                            "message": f"{level} - {message}",
                                            "type": "info" if "INFO" in level else "error" if "ERROR" in level else "warning" if "WARNING" in level else "debug"
                                        })
                                else:
                                    activities.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "message": line,
                                        "type": "unknown"
                                    })
                            except:
                                activities.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": line,
                                    "type": "unknown"
                                })
                return activities

            # Fallback: Try Docker container logs
            result = subprocess.run([
                "docker", "logs", "--tail", "20", "naive-ollma-gpu"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Get last 20 lines
                for line in lines[-20:]:
                    line = line.strip()
                    if line and not line.startswith('---'):
                        # Parse timestamp and message
                        try:
                            # Try to parse Docker log format
                            if 'time=' in line:
                                # Docker log format: time=2025-08-10T21:48:18.314Z level=INFO source=server.go:637 msg="..."
                                parts = line.split('msg="')
                                if len(parts) > 1:
                                    timestamp_part = parts[0].split('time=')[1].split(' ')[0]
                                    message = parts[1].rstrip('"')
                                    timestamp = datetime.fromisoformat(timestamp_part.replace('Z', '+00:00'))
                                    activities.append({
                                        "timestamp": timestamp.isoformat(),
                                        "message": message,
                                        "type": "info" if "INFO" in line else "error" if "ERROR" in line else "warning" if "WARNING" in line else "debug"
                                    })
                                else:
                                    activities.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "message": line,
                                        "type": "unknown"
                                    })
                            elif ' - ' in line:
                                # Standard log format
                                timestamp_str, message = line.split(' - ', 1)
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                activities.append({
                                    "timestamp": timestamp.isoformat(),
                                    "message": message,
                                    "type": "info" if "INFO" in message else "error" if "ERROR" in message else "warning" if "WARNING" in message else "debug"
                                })
                            else:
                                activities.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": line,
                                    "type": "unknown"
                                })
                        except:
                            activities.append({
                                "timestamp": datetime.now().isoformat(),
                                "message": line,
                                "type": "unknown"
                            })
            else:
                # Fallback to local log file
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-20:]:
                            line = line.strip()
                            if line and not line.startswith('---'):
                                try:
                                    if ' - ' in line:
                                        timestamp_str, message = line.split(' - ', 1)
                                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                        activities.append({
                                            "timestamp": timestamp.isoformat(),
                                            "message": message,
                                            "type": "info" if "INFO" in message else "error" if "ERROR" in message else "warning" if "WARNING" in message else "debug"
                                        })
                                except:
                                    activities.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "message": line,
                                        "type": "unknown"
                                    })
        except Exception as e:
            logger.warning(f"Could not read recent activity: {e}")
        
        return activities[-10:]  # Return last 10 activities
    
    def get_statistics(self) -> Dict:
        """Get statistics about generated alphas and results."""
        stats = {
            "total_alphas_generated": 0,
            "successful_alphas": 0,
            "failed_alphas": 0,
            "last_24h_generated": 0,
            "last_24h_successful": 0
        }
        
        try:
            # Count files in results directory
            if os.path.exists(self.results_dir):
                result_files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
                stats["total_alphas_generated"] = len(result_files)
                
                # Count successful alphas (files with content)
                for file in result_files:
                    file_path = os.path.join(self.results_dir, file)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if data and len(data) > 0:
                                stats["successful_alphas"] += 1
                    except:
                        stats["failed_alphas"] += 1
                
                # Count last 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                for file in result_files:
                    file_path = os.path.join(self.results_dir, file)
                    if os.path.getmtime(file_path) > cutoff_time.timestamp():
                        stats["last_24h_generated"] += 1
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                if data and len(data) > 0:
                                    stats["last_24h_successful"] += 1
                        except:
                            pass
                            
        except Exception as e:
            logger.warning(f"Could not get statistics: {e}")
        
        return stats
    
    def get_logs(self, lines: int = 50) -> List[str]:
        """Get recent logs from local file or Docker container."""
        logs = []
        try:
            # Try local log file first
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines_list = f.readlines()
                    logs = lines_list[-lines:] if len(lines_list) > lines else lines_list
                    return [line.strip() for line in logs if line.strip()]

            # Fallback: Try Docker container
            result = subprocess.run([
                "docker", "logs", "--tail", str(lines), "naive-ollma-gpu"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                logs = result.stdout.strip().split('\n')
        except Exception as e:
            logger.warning(f"Could not read logs: {e}")

        return [line.strip() for line in logs if line.strip()]
    
    def get_alpha_generator_logs(self, lines: int = 50) -> List[str]:
        """Get alpha generator specific logs from local file."""
        logs = []
        try:
            # Try alpha_generator_ollama.log first
            alpha_log_file = 'alpha_generator_ollama.log'
            if os.path.exists(alpha_log_file):
                with open(alpha_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines_list = f.readlines()
                    logs = lines_list[-lines:] if len(lines_list) > lines else lines_list
                    return [line.strip() for line in logs if line.strip()]

            # Fallback: Try Docker container and filter for alpha generator content
            result = subprocess.run([
                "docker", "logs", "--tail", str(lines * 2), "naive-ollma-gpu"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                all_logs = result.stdout.strip().split('\n')
                # Filter for alpha generator related logs
                alpha_logs = []
                for line in all_logs:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in [
                        'alpha', 'generator', 'generating', 'ollama', 'model', 'prompt',
                        'response', 'idea', 'factor', 'worldquant', 'submission'
                    ]):
                        alpha_logs.append(line)
                logs = alpha_logs[-lines:] if len(alpha_logs) > lines else alpha_logs
            else:
                # Fallback to local log file
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r') as f:
                        lines_list = f.readlines()
                        logs = lines_list[-lines:] if len(lines_list) > lines else lines_list
        except Exception as e:
            logger.warning(f"Could not read alpha generator logs: {e}")
        
        return [line.strip() for line in logs if line.strip()]
    
    def trigger_mining(self) -> Dict:
        """Trigger manual alpha expression mining."""
        try:
            result = subprocess.run([
                "python", "alpha_orchestrator.py",
                "--mode", "miner",
                "--credentials", "./cookie.txt"
            ], capture_output=True, text=True, timeout=300)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def trigger_submission(self) -> Dict:
        """Trigger manual alpha submission."""
        try:
            result = subprocess.run([
                "python", "alpha_orchestrator.py",
                "--mode", "submitter",
                "--credentials", "./cookie.txt",
                "--batch-size", "3"
            ], capture_output=True, text=True, timeout=600)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def trigger_alpha_generation(self) -> Dict:
        """Trigger manual alpha generation."""
        try:
            result = subprocess.run([
                "python", "alpha_orchestrator.py",
                "--mode", "generator",
                "--credentials", "./cookie.txt",
                "--batch-size", "1"
            ], capture_output=True, text=True, timeout=300)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global dashboard instance
dashboard = AlphaDashboard()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    return jsonify(dashboard.get_system_status())

@app.route('/api/logs')
def api_logs():
    """API endpoint for logs."""
    lines = request.args.get('lines', 50, type=int)
    return jsonify({"logs": dashboard.get_logs(lines)})

@app.route('/api/alpha_logs')
def api_alpha_logs():
    """API endpoint for alpha generator specific logs."""
    lines = request.args.get('lines', 50, type=int)
    return jsonify({"logs": dashboard.get_alpha_generator_logs(lines)})

@app.route('/api/trigger_mining', methods=['POST'])
def api_trigger_mining():
    """API endpoint to trigger manual mining."""
    result = dashboard.trigger_mining()
    return jsonify(result)

@app.route('/api/trigger_submission', methods=['POST'])
def api_trigger_submission():
    """API endpoint to trigger manual submission."""
    result = dashboard.trigger_submission()
    return jsonify(result)

@app.route('/api/trigger_alpha_generation', methods=['POST'])
def api_trigger_alpha_generation():
    """API endpoint to trigger manual alpha generation."""
    result = dashboard.trigger_alpha_generation()
    return jsonify(result)

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh status."""
    return jsonify(dashboard.get_system_status())

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Alpha Generator Dashboard...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Ollama WebUI: http://localhost:3000")
    print("Ollama API: http://localhost:11434")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
