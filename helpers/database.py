import mysql.connector as sql
from mysql.connector import Error

def connect_to_database() -> sql.MySQLConnection:
    """Create a connection to the database using the correct credentials."""
    try:
        connection = sql.connect(
            host='localhost',
            user='root',
            password='Alvin@2016',
            database='isuikwuato'
        )
        if connection.is_connected():
            return connection
        else:
            print("Connection failed.")
            return None
    except Error as e:
        print("Error:", e)
        return None

def get_facility_name_from_db(connection: sql.MySQLConnection) -> str:
    try:
        cursor = connection.cursor()
        query = """
            SELECT property_value
            FROM global_property
            WHERE property='Facility_Name'
        """
        cursor.execute(query)
        facility_name = cursor.fetchone()[0]
        return facility_name
    except Error as e:
        print("MySQL Error:", e)
        return False

