import os
import platform
import subprocess
import time
import sys
from datetime import datetime
import shutil  # For moving files

# Check if debug mode is enabled (via CLI arg or env variable)
DEBUG_MODE = "--debug" in sys.argv or os.getenv("DEBUG") == "true"

def backup_log(file_path):
    """Move old log files to backup_logs folder with a timestamp."""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_logs/{os.path.basename(file_path)}_{timestamp}.log"

        # Retry mechanism for moving the file
        retries = 5
        for _ in range(retries):
            try:
                shutil.move(file_path, backup_filename)  # Move file to backup_logs
                print(f"Successfully backed up log: {file_path} to {backup_filename}")
                break  # Successfully moved, exit loop
            except PermissionError:
                print(f"Permission error on {file_path}. Retrying...")
                time.sleep(1)  # Wait before retrying
        else:
            print(f"Failed to move {file_path} after {retries} attempts.")

def start_process(command, log_file, debug_file=None):
    """Starts a process with separate normal and debug logs."""
    # Backup old logs before starting a new one
    backup_log(log_file)
    if debug_file:
        backup_log(debug_file)

    # Open new log files (overwrite mode)
    with open(log_file, "w") as log:
        if debug_file:
            with open(debug_file, "w") as debug_log:
                process = subprocess.Popen(command, shell=True, stdout=log, stderr=debug_log)
                print(f"Started process with command: {command}")
        else:
            process = subprocess.Popen(command, shell=True, stdout=log, stderr=log)
            print(f"Started process with command: {command}")
        return process

def add_debug_mode(cmd):
    """Adds debug flags to the command if debug mode is enabled."""
    if DEBUG_MODE:
        if "runserver" in cmd:
            return f"{cmd} --verbosity 3"  # Django debug mode
        elif "celery" in cmd:
            return f"{cmd} --loglevel=DEBUG"  # Celery debug mode
        elif "flower" in cmd:
            return f"{cmd} --logging=DEBUG"  # Flower debug mode
    return cmd

# Define services and commands
services = {}

# Add Redis server for Linux first
if platform.system() == "Linux":
    services["Redis Server"] = "redis-server"

# Update service commands with concurrency and auto-scaling for Linux
services.update({
    "Django server": "python manage.py runserver 0.0.0.0:8000",
    "Celery Beat": "celery -A image_visibility beat --scheduler image_visibility.schedulers.CustomScheduler --loglevel=INFO",
    "Celery Worker": f"celery -A image_visibility worker --pool=prefork --loglevel=info"
    if platform.system() == "Linux"  # Apply only on Linux
    else "celery -A image_visibility worker --pool=solo --loglevel=info",  # Default for Windows
    "Celery Flower": "celery -A image_visibility flower"
})

# Start all processes with normal and debug logs based on mode
processes = {
    name: start_process(
        add_debug_mode(cmd),  # Apply debug mode if needed
        f"logs/{name.lower().replace(' ', '_')}.log",  # Normal log
        f"logs/{name.lower().replace(' ', '_')}_debug.log" if DEBUG_MODE else None  # Debug log only in debug mode
    ) for name, cmd in services.items()
}

print("All services started in " + ("DEBUG" if DEBUG_MODE else "NORMAL") + " mode!")

# Monitor processes
try:
    while True:
        for name, process in processes.items():
            if process.poll() is not None:  # Process has stopped
                print(f"{name} has stopped!")

                # Log service stop in the appropriate log file
                with open(f"logs/{name.lower().replace(' ', '_')}.log", "a") as log:
                    log.write(f"\n{name} has stopped!\n")
                if DEBUG_MODE:
                    with open(f"logs/{name.lower().replace(' ', '_')}_debug.log", "a") as debug_log:
                        debug_log.write(f"\n{name} has stopped!\n")
        time.sleep(5)  # Check every 5 seconds
except KeyboardInterrupt:
    print("Shutting down all services...")

    # Terminate all processes first
    for name, process in processes.items():
        process.terminate()
        print(f"{name} terminated...")

    # Wait a bit to ensure logs are released
    time.sleep(2)

    # Backup logs after processes have been shut down
    for name in services.keys():
        log_file = f"logs/{name.lower().replace(' ', '_')}.log"
        debug_file = f"logs/{name.lower().replace(' ', '_')}_debug.log"

        backup_log(log_file)
        if DEBUG_MODE:
            backup_log(debug_file)

    print("All services shut down and logs backed up.")