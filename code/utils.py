import os
import time
import random
import datetime
import hashlib
import colorama
from colorama import Fore, Back, Style
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
data_path = os.getenv('DATA_PATH')

# Initialize colorama
colorama.init(autoreset=True)

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

def colorize(text, color=None):
    """Add color to text using colorama. If no color is specified, make it multicolor."""
    color_dict = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'purple': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    
    colors = [
        Fore.RED,
        Fore.GREEN,
        Fore.BLUE,
        Fore.YELLOW,
        Fore.MAGENTA,
        Fore.CYAN,
        Fore.WHITE
    ]
    
    if color:
        return f"{color_dict.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}"
    
    colored_text = ""
    for i, char in enumerate(text):
        colored_text += f"{colors[i % len(colors)]}{char}"
    return f"{colored_text}{Style.RESET_ALL}"

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
    """Load data from a file in the data folder, creating it if it doesn't exist."""
    filepath = os.path.join(data_path, filename)
    try:
        with open(filepath, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        with open(filepath, 'w') as f:
            return []

def save_data(filename, data):
    """Save data to a file in the data folder."""
    filepath = os.path.join(data_path, filename)
    with open(filepath, 'w') as f:
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

def generate_random_insult():
    """Generate a random insult."""
    insults = [
        "You're as bright as a black hole, and twice as dense.",
        "I'd agree with you but then we'd both be wrong.",
        "You're not stupid; you just have bad luck thinking."
    ]
    return random.choice(insults)

def hash_password(password, salt):
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()