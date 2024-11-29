import re
import logging
import os

def print_directory_structure(root_dir, ignore_dirs=None):
    """
    Prints the directory structure of the given root directory, ignoring specified directories.
    
    Args:
        root_dir (str): The root directory to start from.
        ignore_dirs (list): A list of directory names to ignore (optional).

    # Example usage:

    ```
    igd = ['.venv', '.venv_lsa', '__pycache__', '.git', '.vscode', 'Data', 'lsa', 'lsa_alt', 'Report', 'text-similarity-master', 'Image', 'Logs']
    print_directory_structure('./', ignore_dirs=igd)
    ```
    """
    if ignore_dirs is None:
        ignore_dirs = []

    # Ensure all directory names in ignore_dirs are in lowercase for case-insensitive comparison
    ignore_dirs = [d.lower() for d in ignore_dirs]

    for root, dirs, files in os.walk(root_dir):
        # Convert the current directory names to lowercase for comparison
        dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs]

        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{sub_indent}{f}')

def process_names(name: str, altName: str):
    processed_name = ''
    
    # If the name is fully uppercase, keep it as is
    if altName.isupper():
        altName = 'None'
    if name.isupper():
        altName = 'None'
    elif bool(re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', name)):
        altName = 'None'
    else:
        # Insert a space before each capital letter (not at the beginning)
        altName = re.sub(r'(?<!^)(?=[A-Z])', ' ', altName)

    return altName

# class GuildProfileReader:

class My_Logger:
    '''Custom logger class'''

    def __init__(self, logger_name, log_level=logging.DEBUG, filename='debug'):
        '''
        logger_name: name of logger
        log_level: logging level
            CRITICAL: 50
            ERROR: 40
            WARNING: 30
            INFO: 20
            DEBUG: 10
        filename: name of log file
        '''
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        # Check if the logger already has handlers
        if not self.logger.hasHandlers():
            self._setup_console_handler()
            filename = f'logs/{filename}.log'
            self._setup_file_handler(filename)
        self.logger.propagate = False

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        msg_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%H:%M:%S'
        formatter = logging.Formatter(msg_format, date_format)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        msg_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%H:%M:%S'
        formatter = logging.Formatter(msg_format, date_format)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, message, level=logging.INFO, indent_level=0):
        '''
        level:
            CRITICAL: 50
            ERROR: 40
            WARNING: 30
            INFO: 20
            DEBUG: 10
        '''
        indent = '    ' * indent_level
        formatted_message = f'{indent}{message}'
        self.logger.log(level, formatted_message)