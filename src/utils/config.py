from configparser import ConfigParser
from typing import Dict


def get_config(filename: str, section: str) -> Dict[str, str]:
    parser = ConfigParser()
    parser.read(filename)
    result = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            result[param[0]] = param[1]
    else:
        raise Exception(f"section {section} not found in the {filename} file.")

    return result


def write_config(db_config: Dict[str, str], filename: str, section: str):
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        parser.add_section(section)
        for key, value in db_config.items():
            parser.set(section, key, value)

        with open(filename, 'w') as f:
            parser.write(f)
    else:
        raise Exception(f"the section already exists")

