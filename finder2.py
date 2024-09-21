#"""
# update to finder.py
# 
# 1. Added user prompts to enable or disable additional features.
# 2. Added a ping test function to check if an IP is reachable.
# 3. Added port checking functionality to scan for common open ports on the target IP.
# 4. Implemented traceroute to map the path packets take to the target IP.
# 5. Added domain name resolution to resolve hostnames to IP addresses.
# 6. Added reverse DNS lookup to find hostnames from IP addresses.
# 7. Added functionality to save the gathered information to a file named {searched_ip}.txt.
# 8. Retained IP geolocation via ipapi and enhanced the display of results.
# 9. All features are now toggleable via user prompts to offer more control during execution.
#"""

import ipapi
import socket
import subprocess
import os
from datetime import datetime
from scripts.banner import banner, banner2, clear, logo
from files import colors
from rgbprint import Color, gradient_print
import importlib

C1 = Color.magenta
C2 = Color.hot_pink

c = colors
clear()
gradient_print(logo, start_color=C1, end_color=C2)

PLUGINS_DIR = "plugins"

# Create plugins directory if it doesn't exist
if not os.path.exists(PLUGINS_DIR):
    os.makedirs(PLUGINS_DIR)

# Ping Test
def ping_ip(ip):
    response = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return response.returncode == 0

# Port Checking
def check_ports(ip, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

# Traceroute
def traceroute(ip):
    response = subprocess.run(["traceroute", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return response.stdout.decode()

# DNS Resolution
def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

# Reverse DNS Lookup
def reverse_dns(ip):
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except socket.herror:
        return None

# Save results to file
def save_to_file(ip, content):
    filename = f"{ip}.txt"
    with open(filename, "a") as file:
        file.write(content)
    print(c.lg + f"Results saved to {filename}\n")

# Load plugins
def load_plugins(load_order=None, omit_files=None):
    """Load plugins from the plugins directory with checks."""
    plugins = []
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            if omit_files and module_name in omit_files:
                continue
            
            # Check if the plugin has the required structure (i.e., a run function)
            plugin_path = os.path.join(PLUGINS_DIR, filename)
            with open(plugin_path, 'r') as f:
                if "def run()" not in f.read():
                    print(f"Plugin '{module_name}' does not have a 'run' function. Skipping.")
                    continue

            try:
                module = importlib.import_module(f"{PLUGINS_DIR.replace('/', '.')}.{module_name}")
                plugins.append(module)
                print(f"Loaded plugin: {module_name}")
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")

    # Sort plugins if a load order is specified
    if load_order:
        plugins.sort(key=lambda x: load_order.index(x.__name__) if x.__name__ in load_order else len(load_order))
    return plugins

def view_plugin(plugin_name):
    """View the content of a plugin."""
    try:
        with open(os.path.join(PLUGINS_DIR, f"{plugin_name}.py"), 'r') as f:
            print(f"\nContent of {plugin_name}.py:\n")
            print(f.read())
    except FileNotFoundError:
        print(f"Plugin '{plugin_name}' not found.")

def edit_plugin(plugin_name):
    """Edit a plugin using a simple text editor."""
    plugin_path = os.path.join(PLUGINS_DIR, f"{plugin_name}.py")
    if os.path.exists(plugin_path):
        os.system(f"nano {plugin_path}")  # Replace 'nano' with your preferred editor
    else:
        print(f"Plugin '{plugin_name}' not found.")

def run_plugins(plugins, function_name="run"):
    """Run a specified function from each loaded plugin."""
    for plugin in plugins:
        if hasattr(plugin, function_name):
            func = getattr(plugin, function_name)
            func()
        else:
            print(f"Plugin '{plugin.__name__}' does not have a function '{function_name}'.")

def program():
    ip = input(c.ran + "Enter target IP (or domain): " + c.ran)

    # Resolve domain to IP if necessary
    if not ip.replace('.', '').isdigit():
        ip = resolve_domain(ip)
        if ip is None:
            print(c.lr + "Unable to resolve domain.")
            return

    content = f"Results for IP: {ip}\n"
    content += f"Time: {datetime.now()}\n\n"

    # 1. Geolocation via ipapi
    location = ipapi.location(ip)
    content += "Geolocation Information:\n"
    for k, v in location.items():
        content += f"{k} : {v}\n"
    print(c.c + "Geolocation info gathered.\n")

    # Ask user to enable/disable various functions
    if input(c.ran + "Ping the IP? (y/n): ").lower() in ['y', 'yes']:
        if ping_ip(ip):
            print(c.lg + f"{ip} is reachable via ping.\n")
            content += f"{ip} is reachable via ping.\n"
        else:
            print(c.lr + f"{ip} is not reachable via ping.\n")
            content += f"{ip} is not reachable via ping.\n"

    if input(c.ran + "Check common ports? (y/n): ").lower() in ['y', 'yes']:
        common_ports = [22, 80, 443, 8080, 21]
        open_ports = check_ports(ip, common_ports)
        if open_ports:
            print(c.lg + f"Open ports on {ip}: {open_ports}\n")
            content += f"Open ports on {ip}: {open_ports}\n"
        else:
            print(c.lr + f"No open ports found on {ip}.\n")
            content += f"No open ports found on {ip}.\n"

    if input(c.ran + "Perform traceroute? (y/n): ").lower() in ['y', 'yes']:
        trace_results = traceroute(ip)
        print(c.lg + "Traceroute results:\n" + trace_results)
        content += f"Traceroute results:\n{trace_results}\n"

    if input(c.ran + "Perform reverse DNS lookup? (y/n): ").lower() in ['y', 'yes']:
        host = reverse_dns(ip)
        if host:
            print(c.lg + f"Reverse DNS for {ip}: {host}\n")
            content += f"Reverse DNS for {ip}: {host}\n"
        else:
            print(c.lr + f"No reverse DNS entry for {ip}.\n")
            content += f"No reverse DNS entry for {ip}.\n"

    # Load and run plugins
    if input(c.ran + "Run plugins? (y/n): ").lower() in ['y', 'yes']:
        load_order_input = input("Enter a comma-separated list of plugins to load in order (leave empty for default): ")
        load_order = load_order_input.split(",") if load_order_input else None
        omit_files_input = input("Enter a comma-separated list of plugins to omit (leave empty for none): ")
        omit_files = omit_files_input.split(",") if omit_files_input else None
        plugins = load_plugins(load_order=load_order, omit_files=omit_files)
        
        # Allow user to view or edit plugins before running
        for plugin in plugins:
            action = input(f"Do you want to view or edit the plugin '{plugin.__name__}'? (view/edit/skip): ").lower()
            if action == 'view':
                view_plugin(plugin.__name__)
            elif action == 'edit':
                edit_plugin(plugin.__name__)
        
        run_plugins(plugins)

    save_to_file(ip, content)

# Main loop
yes = ['y', 'yes']
no = ['n', 'no']

cont = ""
while cont not in no:
    program()
    cont = input(c.lg + "Do you want to continue? [y/n]: ").lower()
    if cont in no:
        clear()
        banner2()
    else:
        clear()
        banner2()
