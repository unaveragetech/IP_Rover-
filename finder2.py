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

C1 = Color.magenta
C2 = Color.hot_pink

c = colors
clear()
gradient_print(logo, start_color=C1, end_color=C2)


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

    save_to_file(ip, content)


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
