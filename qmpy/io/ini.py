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

