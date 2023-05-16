from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

def read_config(config_file = 'config-school.ini', section = 'mysql'):
    parser = ConfigParser()
    parser.read(config_file)
    
    config = {}
    
    if parser.has_section(section):
        # Parse the configuration file.
        items = parser.items(section)
        
        # Construct the parameter dictionary.
        for item in items:
            config[item[0]] = item[1]
            
    else:
        raise Exception(f'Section [{section}] missing ' + \
                        f'in config file {filename}')
    
    return config
        
def make_connection(config_file = 'config-school.ini', section = 'mysql'):
    try:
        db_config = read_config(config_file, section)
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            return conn

    except Error as e:
        print('Connection failed.')
        print(e)
        
        return None

def do_query_return_all(conn, sql):
    cursor = None
        
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        # Return the all fetched data as a list of tuples,
        # one tuple per table row.
        rows = cursor.fetchall()
        count = cursor.rowcount
        
        cursor.close()
        return [rows, count]

    except Error as e:
        print('Query failed')
        print(e)

        cursor.close()
        return [(), 0]
