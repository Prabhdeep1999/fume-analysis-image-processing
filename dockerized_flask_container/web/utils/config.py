from configparser import ConfigParser

def config(filename='./req_files/database.ini', section='postgresql'):
    """Config Parser for the database.ini config file 

    Args:
        filename (str, optional): Path to .ini file (config file). Defaults to 'req_files/database.ini'.
        section (str, optional): section in .ini file to extract. Defaults to 'postgresql'.

    Raises:
        Exception: If the section is not in .ini file an exception is raised

    Returns:
        db (dict): Dictionary of all the relevant information needed to connect to Postgresql database
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db