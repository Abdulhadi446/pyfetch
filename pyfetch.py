#!/usr/bin/env python3
import os
import platform
import socket
import subprocess
import sys


def get(key):
    try:
        with open(f"/sys/class/dmi/id/{key}") as f:
            return f.read().strip()
    except:
        return "Unknown"


def cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except:
        return "Unknown"


def get_distro():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    return line.split("=")[1].strip('"')
    except:
        pass
    return "Linux"


def get_uptime():
    uptime = cmd("cat /proc/uptime | awk '{print int($1)}'")
    if uptime == "Unknown":
        return "Unknown"
    seconds = int(uptime)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {mins}m"
    return f"{hours}h {mins}m"


def get_memory():
    try:
        with open("/proc/meminfo") as f:
            total = used = available = 0
            for line in f:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    available = int(line.split()[1]) // 1024
            used = total - available
            return f"{used}MiB / {total}MiB"
    except:
        return "Unknown"


def get_cpu():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except:
        pass
    return cmd("lscpu | grep 'Model name' | cut -d: -f2 | xargs")


def get_kernel():
    return platform.release()


def get_host():
    return get("product_name") or get("board_name") or "Unknown"


def get_os():
    return get_distro()


def get_resolution():
    res = cmd("xrandr 2>/dev/null | grep '*' | head -1 | awk '{print $1}'")
    return res if res != "Unknown" else "Unknown"


def get_shell():
    return os.environ.get("SHELL", "Unknown").split("/")[-1]


def get_de():
    session = os.environ.get("XDG_CURRENT_DESKTOP", "")
    if session:
        return session
    session = cmd("echo $DESKTOP_SESSION")
    return session if session != "Unknown" else "Unknown"


def get_gpu():
    try:
        gpus = cmd("lspci | grep -i vga | cut -d: -f3").split("\n")
        return gpus[0].strip() if gpus else "Unknown"
    except:
        return "Unknown"


colors = [
    "\033[38;2;122;189;199m",
    "\033[38;2;163;195;163m",
    "\033[38;2;210;153;153m",
    "\033[38;2;204;187;136m",
    "\033[38;2;163;189;163m",
    "\033[38;2;163;163;163m",
]
reset = "\033[0m"


def main():
    info = [
        ("OS", get_os()),
        ("Host", get_host()),
        ("Kernel", get_kernel()),
        ("Uptime", get_uptime()),
        ("Shell", get_shell()),
        ("Resolution", get_resolution()),
        ("DE", get_de()),
        ("CPU", get_cpu()),
        ("GPU", get_gpu()),
        ("Memory", get_memory()),
    ]

    logo = [
        "     _____ ",
        "    /     \\",
        "   |  O O  |",
        "   |   ^   |",
        "    \\_____/",
        "       |   ",
        "    --+--  ",
        "       |   ",
    ]

    max_label_len = max(len(x[0]) for x in info)
    logo_width = max(len(l) for l in logo)

    for i, line in enumerate(logo):
        color = colors[i % len(colors)]
        if i < len(info):
            label = info[i][0]
            value = info[i][1]
            spacing = " " * (max_label_len - len(label) + 1)
            print(f"{color}{line:<{logo_width}}{reset} {label}:{spacing}{value}")
        else:
            print(f"{color}{line:<{logo_width}}{reset}")

    for i in range(len(logo), len(info)):
        label = info[i][0]
        value = info[i][1]
        spacing = " " * (max_label_len - len(label) + 1)
        print(f"{' ' * logo_width} {label}:{spacing}{value}")


if __name__ == "__main__":
    main()
