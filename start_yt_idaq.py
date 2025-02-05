import os
import platform
import subprocess
import time
import sys

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Check if debug mode is enabled (via CLI arg or env variable)
DEBUG_MODE = "--debug" in sys.argv or os.getenv("DEBUG") == "true"

def start_process(command, log_file, debug_file=None):
    """Starts a process with separate normal and debug logs."""
    with open(log_file, "w") as log:
        if debug_file:
            with open(debug_file, "w") as debug_log:
                process = subprocess.Popen(command, shell=True, stdout=log, stderr=debug_log)
        else:
            process = subprocess.Popen(command, shell=True, stdout=log, stderr=log)  # No debug log for normal mode
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
services = {
    "Django server": "python manage.py runserver",
    "Celery Beat": "celery -A image_visibility beat --scheduler image_visibility.schedulers.CustomScheduler --loglevel=INFO",
    "Celery Worker": "celery -A image_visibility worker --pool=solo --loglevel=info"
    if platform.system() == "Windows"
    else "celery -A image_visibility worker --loglevel=info",
    "Celery Flower": "celery -A image_visibility flower",
}

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
    for name, process in processes.items():
        process.terminate()
        print(f"{name} terminated.")
