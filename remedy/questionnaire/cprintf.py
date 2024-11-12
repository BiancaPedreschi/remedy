import sys

def cprintf(color, message):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
    }
    end_color = '\033[0m'
    if color in colors:
        sys.stdout.write(colors[color] + message + end_color)
    else:
        sys.stdout.write(message)

