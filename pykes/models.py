# pykes/models.py
import sqlite3
from datetime import datetime
import os

DB_PATH = os.environ.get('DATABASE_PATH', 'dangote_execution.db')
UPLOAD_FOLDER = 'static/uploads'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create outlets table
    c.execute('''
    CREATE TABLE IF NOT EXISTS outlets (
        id INTEGER PRIMARY KEY,
        urn TEXT UNIQUE,
        outlet_name TEXT,
        customer_name TEXT,
        address TEXT,
        phone TEXT,
        outlet_type TEXT,
        local_govt TEXT,
        state TEXT,
        region TEXT
    )
    ''')

    # Create users table (execution agents)
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        role TEXT,
        region TEXT,
        state TEXT,
        lga TEXT
    )
    ''')

    # Create executions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS executions (
        id INTEGER PRIMARY KEY,
        outlet_id INTEGER,
        agent_id INTEGER,
        execution_date TEXT,
        before_image TEXT,
        after_image TEXT,
        latitude REAL,
        longitude REAL,
        notes TEXT,
        products_available TEXT,
        execution_score REAL,
        status TEXT,
        FOREIGN KEY (outlet_id) REFERENCES outlets (id),
        FOREIGN KEY (agent_id) REFERENCES users (id)
    )
    ''')

    # Check if outlets are already populated
    c.execute("SELECT COUNT(*) FROM outlets")
    if c.fetchone()[0] == 0:
        # Populate sample data
        outlets = [
            ('DCP/19/SW/ED/1000001', 'FAMS STEEL COMPANY 2', 'FAMOUS EBESUNUN', '156, USELU LAGOS ROAD, BENIN', '7039539773', 'Shop', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000002', 'FAMS STEEL COMPANY', 'FAMOUS EBESUNUN', '162, USELU LAGOS ROAD, BENIN', '7039539773', 'Shop', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000003', 'IGWE CONSTRUCTION 1', 'IGWE WILFRED', '214, LAGOS/BENIN ROAD, UGBOWO, BENIN', '8052220480', 'Shop', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000004', 'ALEXO HOLDING ENT', 'ALEX CHIDIMA', '3,ISIOR VILLAGE, BESIDE PETOM FILLING STATION.BENIN/LAGOS ROAD', '8182728117', 'Shop', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000005', 'IFE ENT.', 'IFEANYI OKEKE', 'OPP. KONKON FILLING STATION,EVBUOMORE QTRS ,ISIOR BENIN', '8035551600', 'CONTAINER', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000006', 'OGHAS CEMENT', 'TONY UCHE', '13A, LAGOS/BENIN ROAD, ISIOR,BENIN', '8032813962', 'Shop', 'EGOR', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000007', 'ONOS CEMENT', 'ONOS SAMUEL', 'AGEN JUNCTION, LAGOS BENIN EXPRESS ROAD', '8037208594', 'CONTAINER', 'OVIA NORTH EAST', 'EDO', 'SW'),
            ('DCP/19/SW/ED/1000008', 'OSAS K 1', 'OSAS KELVIN', '112, nitel road, off lagos benin road', '8037455230', 'CONTAINER', 'EGOR', 'EDO', 'SW')
        ]

        for outlet in outlets:
            c.execute('''
            INSERT INTO outlets (urn, outlet_name, customer_name, address, phone, outlet_type, local_govt, state, region)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', outlet)

        # Add sample users
        users = [
            ('admin', 'admin123', 'Admin User', 'admin', 'ALL'),
            ('agent1', 'agent123', 'John Doe', 'field_agent', 'SW'),
            ('agent2', 'agent123', 'Jane Smith', 'field_agent', 'SW')
        ]

        for user in users:
            c.execute('''
            INSERT INTO users (username, password, full_name, role, region)
            VALUES (?, ?, ?, ?, ?)
            ''', user)

    conn.commit()
    conn.close()

    # Ensure upload directory exists
    if not os.path.exists(UPLOAD_FOLDER):
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create upload directory {UPLOAD_FOLDER}: {e}")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn