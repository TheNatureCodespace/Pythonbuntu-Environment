import os
import time
import shutil
import stat
import subprocess
import sys
import socket
import json

crn = "user"
ccn = "environment"
username = crn
computer = ccn
current_directory = os.getcwd()  # Initialize to the actual working directory
prompt_color = 'reset'  # Default prompt color is reset (no color)
command_history = []  # List to store command history
command_aliases = {}  # Dictionary to hold command aliases
command_list = ["help","about","exit","clear", "pwd", "ls", ]

# ANSI color codes for customization
color_codes = {
    'reset': "\033[0m", 
    'red': "\033[31m",
    'green': "\033[32m", 
    'yellow': "\033[33m", 
    'blue': "\033[34m", 
    'magenta': "\033[35m", 
    'cyan': "\033[36m", 
    'white': "\033[37m"
}

def set_prompt_color(color):
    """Set the prompt color using ANSI escape codes."""
    return color_codes.get(color.lower(), color_codes['reset'])

# Function to list active processes
def list_processes():
    """Displays a list of active processes using the 'ps' command."""
    print(f"{'PID':<8} {'Name':<25} {'Status':<15} {'CPU%':<10} {'Memory%':<10}")
    print("-" * 75)
    # Execute the 'ps' command using subprocess for better output handling
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    print(result.stdout)  # Print the standard output of the 'ps' command

def kill_process(pid):
    """Terminates a process by its PID."""
    try:
        os.kill(pid, 9)  # 9 is the signal for forceful termination (SIGKILL)
        print(f"Process {pid} terminated successfully.")
    except ProcessLookupError:
        print(f"Error: Process with PID {pid} not found.")
    except PermissionError:
        print(f"Error: Insufficient permissions to terminate process {pid}.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def handle_listalias():
    if command_aliases:
        print("Current aliases:")
        for alias, command in command_aliases.items():
            print(f"{alias} -> {command}")
    else:
        print("No aliases set.")

# Dictionary to hold environment variables
env_vars = {
    'HOME': os.path.expanduser("~"),
    'USER': os.environ.get("USER") or "default_user",  # Fallback to 'default_user' if USER is not set
    'PWD': os.getcwd()
}

def resolve_env_vars(command):
    """Replace environment variables in the command with their values."""
    for var, value in env_vars.items():
        command = command.replace(f"${{{var}}}", value)
    return command

def setenv(var_name, value):
    """Sets an environment variable."""
    env_vars[var_name] = value
    print(f"{var_name} set to {value}")

def custom_ping(host, port=80, timeout=2):
    """
    Check if a host is reachable by attempting to connect to it.
    """
    try:
        print(f"\nPinging {host}...\n")
        start_time = time.time()
        
        # Create a socket and connect to the host
        with socket.create_connection((host, port), timeout):
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            print(f"Reply from {host}: time={latency:.2f}ms\n")
    except socket.timeout:
        print(f"Request timed out for {host}.")
    except socket.gaierror:
        print(f"Ping request could not find host {host}. Please check the name and try again.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Save the current configuration to a JSON file
def save_config():
    config = {
        'username': username,
        'computer': computer,
        'current_directory': current_directory,
        'prompt_color': prompt_color,
        'command_history': command_history,
        'command_aliases': command_aliases,
        'env_vars': env_vars
    }
    
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print("Configuration saved to 'config.json'.")

# Load the configuration from a JSON file
def load_config():
    global username, computer, current_directory, prompt_color, command_history, command_aliases, env_vars
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                
                # Load configuration values
                username = config.get('username', 'user')
                computer = config.get('computer', 'environment')
                current_directory = config.get('current_directory', os.getcwd())
                prompt_color = config.get('prompt_color', 'reset')
                command_history = config.get('command_history', [])
                command_aliases = config.get('command_aliases', {})
                env_vars = config.get('env_vars', {})
                
            print("Configuration loaded from 'config.json'.")
        else:
            print("No existing configuration file found, using default settings.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Provide a clear error message if loading or parsing the config fails
        print(f"Error loading configuration: {str(e)}")
        print("Using default settings.")

        # You could also decide to create a new config file or reset settings here if needed.


def main():

    load_config()  # Load configuration from file at startup
    
    print("\nPythonbuntu Environment")
    print("\nType 'help' For A List Of Commands\n")

    while True:
        # Show prompt with customizable color
        prompt = f"{set_prompt_color(prompt_color)}{username}@{computer}:{current_directory}$ {color_codes['reset']}"
        command = input(prompt).strip()

        # Resolve environment variables like $USER, $HOME, etc.
        command = resolve_env_vars(command)

        # Save the command to the history list
        if command:
            command_history.append(command)

        # Handle commands
        if command == "exit":
            # Confirm exit with the user
            confirm = input("\nAre you sure you want to exit? (y/n): ").strip().lower()
            if confirm == "y" or confirm == "yes":
                save_config()  # Save configuration before exiting
                os.system('cls' if os.name == 'nt' else 'clear')
                break  # Exit the loop and terminate the program
            else:
                print("")
        elif command == "":
            print("")
        elif command == "ps":
            list_processes()
        elif command.startswith("kill"):
            try:
                # Extract the PID from the command
                args = command.split()
                if len(args) != 2:
                    print("\nUsage: kill <PID>\n")
                else:
                    pid = int(args[1])
                    kill_process(pid)
            except ValueError:
                print("\nInvalid PID. Please enter a numeric value.\n")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}\n")
        elif command == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\nPythonbuntu Environment v1.6 (Beta)")
            print("\nType 'help' For A List Of Commands\n")
            continue  # Skip the rest of the loop and show the prompt again
        elif command == "listalias":
            handle_listalias()
        elif command == "pwd":
            print(current_directory)
        elif command.startswith("ls"):
            try:
                # Check if the command includes -a or -l or both
                args = command.split()
                show_details = "-l" in args
                show_all = "-a" in args
                
                # List files in the current directory, including hidden ones if -a is specified
                files = os.listdir(current_directory)
                
                if show_all:
                    # Include hidden files (those starting with '.')
                    files = os.listdir(current_directory)
                else:
                    # Filter out hidden files (those starting with '.')
                    files = [file for file in files if not file.startswith('.')]
                
                # If -l option is provided, show file details
                if show_details:
                    for file in files:
                        file_path = os.path.join(current_directory, file)
                        stats = os.stat(file_path)
                        
                        # File permissions
                        permissions = stat.filemode(stats.st_mode)
                        
                        # File size
                        size = stats.st_size
                        
                        # Last modified time
                        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                        
                        # Display the details
                        print(f"{permissions} {stats.st_nlink:>3} {stats.st_uid:>5} {stats.st_gid:>5} {size:>10} {modified_time} {file}")
                else:
                    # Just list the file names without extra details
                    for file in files:
                        print(file)

            except PermissionError:
                print("\nPermission Denied. Cannot list files in this directory.")
            except FileNotFoundError:
                print("\nDirectory not found.")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
        elif command.startswith("mkdir"):
            try:
                # Extract the directory name from the command
                dir_name = command[6:].strip()
                if dir_name == "":
                    print("\nPlease provide a directory name.\n")
                else:
                    # Create the new directory
                    new_dir_path = os.path.join(current_directory, dir_name)
                    os.makedirs(new_dir_path, exist_ok=False)  # Raises error if the directory already exists
                    print(f"Directory '{dir_name}' created successfully.\n")
            except FileExistsError:
                print(f"\nError: Directory '{dir_name}' already exists.\n")
            except PermissionError:
                print("\nPermission Denied. Cannot create the directory.\n")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
        elif command.startswith("setalias"):
            parts = command.split()
            if len(parts) == 3:
                alias = parts[1]
                actual_command = parts[2]
                command_aliases[alias] = actual_command
                print(f"Alias '{alias}' set to '{actual_command}'.")
            else:
                print("\nUsage: setalias <alias> <command>\n")
        elif command.startswith("unalias"):
            parts = command.split()
            if len(parts) == 2:
                alias = parts[1]
                if alias in command_aliases:
                    del command_aliases[alias]
                    print(f"Alias '{alias}' removed.")
                else:
                    print(f"\nAlias '{alias}' not found.")
            else:
                print("\nUsage: unalias <alias>\n")

        if command.startswith("ping"):
            args = command.split()
            if len(args) != 2:
                print("\nUsage: ping <hostname or IP address>\n")
            else:
                host = args[1]
                try:
                    custom_ping(host)
                except FileNotFoundError:
                    print("\nError: The 'ping' command is not available or executable on this system.\n")
                except Exception as e:
                    print(f"\nAn error occurred: {str(e)}\n")

        elif command.startswith("rm"):
            try:
                # Extract the file or directory name from the command
                args = command.split()
                if len(args) == 1:
                    print("\nPlease specify a file or directory to remove.\n")
                elif len(args) == 2:
                    item_name = args[1].strip()
                    item_path = os.path.join(current_directory, item_name)
                    
                    if os.path.isfile(item_path):
                        os.remove(item_path)  # Remove the file
                        print(f"\nFile '{item_name}' removed successfully.\n")
                    elif os.path.isdir(item_path):
                        print("\nUse 'rm -r' to remove a directory.\n")
                    else:
                        print(f"\nError: '{item_name}' not found.\n")
                elif len(args) == 3 and args[1] == "-r":
                    # Handle recursive removal for directories
                    dir_name = args[2].strip()
                    dir_path = os.path.join(current_directory, dir_name)

                    if os.path.isdir(dir_path):
                        # Using shutil.rmtree to recursively remove a directory and its contents
                        shutil.rmtree(dir_path)  # Remove non-empty directory
                        print(f"\nDirectory '{dir_name}' and all its contents removed successfully.\n")
                    else:
                        print(f"\nError: '{dir_name}' is not a directory.\n")
            except PermissionError:
                print("\nPermission Denied. Cannot remove the file or directory.\n")
            except FileNotFoundError:
                print("\nFile or directory not found.\n")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}\n")
        elif command.startswith("cp"):
            try:
                # Extract source and destination from the command
                args = command.split()
                if len(args) != 3:
                    print("\nUsage: cp <source> <destination>\n")
                else:
                    source = args[1].strip()
                    destination = args[2].strip()
                    source_path = os.path.join(current_directory, source)
                    destination_path = os.path.join(current_directory, destination)

                    # Check if source exists
                    if not os.path.exists(source_path):
                        print(f"\nError: Source '{source}' not found.\n")
                    elif os.path.isdir(source_path):
                        # If the source is a directory, copy recursively
                        if os.path.isdir(destination_path):
                            print(f"\nError: '{destination}' is a directory. Specify a new destination path.\n")
                        else:
                            shutil.copytree(source_path, destination_path)
                            print(f"\nDirectory '{source}' copied to '{destination}' successfully.\n")
                    else:
                        # If it's a file, copy it
                        if os.path.isdir(destination_path):
                            destination_path = os.path.join(destination_path, os.path.basename(source))  # File will be copied inside the destination directory
                        shutil.copy2(source_path, destination_path)  # copy2 to preserve metadata
                        print(f"\nFile '{source}' copied to '{destination}' successfully.\n")
            except PermissionError:
                print("\nPermission Denied. Cannot copy the file or directory.\n")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}\n")
        elif command == "help":
            print("\nAvailable Commands:\n")
            print("------------------\n")
            print("General Operatinons:\n")
            print("    help - Show this help message")
            print("    about - About the Pythonbuntu Environment")
            print("    exit - Exit the Pythonbuntu Environment")
            print("    clear - Clear the screen")
            print("\nDirectory / File Operations:\n")
            print("    pwd - Show current directory")
            print("    ls - List files in current directory")
            print("    mkdir - Create a new directory")
            print("    rm - Remove a file or directory")
            print("    cp - Copy files and directories")
            print("    cat - Show the contents of a file")
            print("    touch - Create an empty file or update the timestamp of a file")
            print("    cd - Change the current directory")
            print("\nCustomization Operations:\n")
            print("    promptcolor - Change the color of the prompt")
            print("    setenv - Set an environment variable")
            print("    setalias - Create a shortcut for a command (e.g., 'setalias ll \"ls -l\"')")
            print("    unalias - Remove a shortcut for a command (e.g., 'unalias ll')")
            print("    listalias - Lists the created alias in the system's memory")
            print("\nInternet Operations:\n")
            print("    ping - Pings the specified hostname or IP address")
            print("\nRoot Operations:\n")
            print("    crn - Change root username")
            print("    ccn - Change computer name")
            print("\nOther Operations:\n")
            print("    history - Show command history")
            print("    kill    - Terminate a process by specifying its Process ID (PID). Use this to send a termination signal.")
            print("    ps      - List all active processes running on the system, displaying process IDs (PID), names, status, CPU usage, and memory usage.")
            print("")
        else:
            print(f"\nCommand '{command}' not recognized. Type 'help' for a list of commands.")

# Start the terminal
if __name__ == "__main__":
    main()