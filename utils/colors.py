import sys

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def c(text, color):
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text

def info(msg): print(f"{c('[+]', Colors.GREEN)} {msg}")
def warn(msg): print(f"{c('[!]', Colors.YELLOW)} {msg}")
def error(msg): print(f"{c('[-]', Colors.RED)} {msg}")
def debug(msg): print(f"{c('[*]', Colors.BLUE)} {msg}")
def header(msg): print(
    f"\n{c('='*60, Colors.CYAN)}\n{c(msg, Colors.HEADER + Colors.BOLD)}\n{c('='*60, Colors.CYAN)}")
def sub(msg): print(f"  {c('->', Colors.CYAN)} {msg}")
def success(msg): print(f"{c('[+]', Colors.GREEN)} {c(msg, Colors.BOLD)}")
