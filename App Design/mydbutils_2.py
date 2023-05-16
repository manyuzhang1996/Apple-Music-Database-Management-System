from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

def read_db_configuration(filename = 'config_sjsu_daydayup_wh2.ini', section = 'mysql'):
    parser = ConfigParser()
    parser.read(filename)
    
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
        
def make_connection():
    try:
        db_config = read_db_configuration()            
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            return conn

    except Error as e:
        print('Connection failed.')
        print(e)
        
        return None

def do_query(sql):
    cursor = None
    
    # Connect to the database.
    conn = make_connection()
        
    if conn != None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql)

        except Error as e:
            print('Query failed')
            print(e)
            
            return [(), 0]

    # Return the fetched data as a list of tuples,
    # one tuple per table row.
    if conn != None:
        rows = cursor.fetchall()
        count = cursor.rowcount
            
        conn.close()
        return [rows, count]
    else:
        return [(), 0]
