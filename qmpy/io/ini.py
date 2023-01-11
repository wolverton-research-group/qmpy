# qmpy/io/ini.py
# Module to handle reading from/writing into .ini (also .cfg) files

# Py2 ConfigParser = Py3 configparser
try:
    import configparser
except ImportError as err:
    import ConfigParser as configparser


class INIError(Exception):
    """Base class to handle errors associated with reading/writing INI files."""
    pass


def read(filename=None):
    """
    Converts sections/options in INI files into a Python dictionary.

    (Note: Python3 provides this functionality already with the
    `ConfigParser.read()` function. This is mostly for compatibility between
    Python 2 and 3.)

    Args:
        filename:
            String with the path to the CSLD INI file to read from

    Returns:
        Two-level dictionary with the following structure:
        {
            "section1": {
                "option1": "value1",
                "option2": "value2",
                ...
            },
            "section2": {
                "option1": "value1",
                "option2": "value2",
                ...
            },
            ...
        }

        NOTE #1: No type-conversion is performed for parsed values. They are
        returned as strings, similar to the proxy-dictionary returned by
        Python3's `ConfigParser.read()` function.

        NOTE #2: Empty/None values in the CSLD INI file are skipped entirely
        but empty sections are retained in the resulting dictionary.

    """
    if filename is None:
        return {}
    config = configparser.ConfigParser()
    config.read(filename)
    config_as_dict = {}
    for section in config.sections():
        config_as_dict[section] = {}
        for option in config.options(section):
            value = config.get(section, option, raw=True)
            if value.strip().lower() == 'none' or value.strip() == '':
                continue
            config_as_dict[section][option] = value
    return config_as_dict


def write(data_dict=None, filename=None):
    """
    Writes dictionary data to file in the .ini/.cfg format.

    Args:
        data_dict:
            Dictionary to be written to file. By design, only two levels of
            the dictionary are written to file and rest of the dictionary is
            ignored.

        filename:
            String with the full path to the file into which the dictionary
            should be written.

    Returns:
        None.

    """
    if not data_dict:
        return
    if not filename:
        err_msg = 'Name of the file to write into not specified'
        raise INIError(err_msg)
    config = configparser.ConfigParser()
    for section, options in data_dict.items():
        config.add_section(section)
        for option, value in options.items():
            config.set(section, option, value)
    with open(filename, 'w') as fw:
        config.write(fw)

