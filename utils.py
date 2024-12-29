import os
import time
import random
import datetime
from colorama import Fore, Back, Style

def clear_console():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_with_delay(text, delay=0.03):
    """Print text character by character with a delay."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def roll_dice(sides=6):
    """Roll a dice with specified number of sides."""
    return random.randint(1, sides)

def colorize(text, color):
    """Add color to text using colorama."""
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'purple': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    return f"{colors.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}"

def get_valid_input(prompt, valid_options=None, is_numeric=False):
    """Get validated input from user."""
    while True:
        response = input(prompt).strip()
        if not response:
            print("Input cannot be empty. Please try again.")
            continue
        if is_numeric:
            try:
                return int(response)
            except ValueError:
                print("Please enter a valid number.")
                continue
        if valid_options and response not in valid_options:
            print(f"Please enter one of: {', '.join(valid_options)}")
            continue
        return response

def load_data(filename):
    """Load data from a file, creating it if it doesn't exist."""
    try:
        with open(filename, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        with open(filename, 'w') as f:
            return []

def save_data(filename, data):
    """Save data to a file."""
    with open(filename, 'w') as f:
        if isinstance(data, list):
            f.write('\n'.join(str(item) for item in data))
        else:
            f.write(str(data))

def timestamp():
    """Get current timestamp in readable format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def pretty_print(title, content, width=50):
    """Print content in a formatted box."""
    print('='* width)
    print(f"{title:^{width}}")
    print('='* width)
    print(content)
    print('='* width) 