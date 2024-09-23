import re
import logging
import os

invalid_chars = '<>:"/\|?*｜\n. '
invalid_char_pattern = '|'.join(map(re.escape, invalid_chars))
webname_filter = re.compile(invalid_char_pattern)
'''re object with pattern: '<>:"/\|?*｜\\n .\''''

url_regex = re.compile(r"^(?P<protocol>[a-z\-]+)?:?(?P<slash>\/\/)?(?P<host>[a-zA-Z0-9\./]+)?(?P<port>:\d+)?$")
'''re object with pattern to filter url'''

en_str_regex = re.compile(r'[a-zA-Z0-9_.:/-]+')
'''re object with pattern to filter english string'''

lineid_regex = re.compile(r'[a-zA-Z0-9@_.-]+')
'''re object with pattern to filter english string'''

idcard_regex = re.compile(r'[A-Z][1289][0-9]{8}(?![0-9])')
'''re object with pattern to filter ID card number'''

# TODO: Add function documentation
def parse_url(text: str):
    '''Parse url from string
    
    '''

    urls = []
    text = sep_english(text)
    words = text.split()
    
    for part in words:
        match = url_regex.match(part)
        if match and match.group('protocol') and match.group('host'):
            # print(f"protocol {match.group('protocol')}")  # Outputs: http
            # print(f"host {match.group('host')}")  # Outputs: example.com
            # print(f"port {match.group('port')}")  # Outputs: :80
            urls.append(part)
    
    return urls

def parse_lineid(input_string: str):
    '''Parse Line ID from string
    
    '''

    words  = lineid_regex.findall(input_string)

    for line_id in words:
        input_string = input_string.replace(line_id, f' {line_id} ', 1)

    return input_string.split()

def sep_english(input_string: str):
    '''Apped head and end with spaces to english string'''
    # Use regular expression to find English words and URLs
    english_words = en_str_regex.findall(input_string)

    # Add space before and after each English word
    for word in english_words:
        input_string = input_string.replace(word, f' {word} ', 1)

    return input_string

def is_contain_IDcard(input_string: str):
    '''Check if a string contains ID card number.'''

    id_number = idcard_regex.search(input_string)
    if id_number is not None:
        if validate_IDcard(id_number.group(0)):
            return True
    return False

def validate_IDcard(ID: str):
    '''Validate ID card number'''
    validate_weight = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]
    checksum = 0
    base = ord('A')
    special_cases = {'I': 34, 'O': 35, 'W': 32, 'X': 30, 'Y': 31, 'Z': 33}

    n0 = special_cases.get(ID[0], ord(ID[0]) - base + 10)
    ID = ID.replace(ID[0], str(n0))

    for index in range(0, len(ID)):
        checksum += int(ID[index]) * validate_weight[index]
    if checksum%10 != 0:
        return False
    return True

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

class Debug_Logger:
    '''Custom logger class'''

    def __init__(self, logger_name, log_level=logging.DEBUG, filename='debug.log'):
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