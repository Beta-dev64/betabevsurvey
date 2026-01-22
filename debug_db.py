#!/usr/bin/env python3
import sqlite3
import os

def check_database():
    db_path = os.environ.get('DATABASE_PATH', 'dangote_execution.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("=== USERS ===")
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    for row in users:
        print(f'ID: {row[0]}, Username: {row[1]}, Role: {row[4]}, Region: {row[5]}, State: {row[6] or "None"}, LGA: {row[7] or "None"}')
    
    print("\n=== OUTLETS (First 10) ===")
    c.execute('SELECT id, urn, outlet_name, region, state FROM outlets LIMIT 10')
    outlets = c.fetchall()
    for row in outlets:
        print(f'ID: {row[0]}, URN: {row[1]}, Name: {row[2]}, Region: {row[3]}, State: {row[4] or "None"}')
    
    print(f"\nTotal outlets: {len(outlets)}")
    
    print("\n=== OUTLETS BY REGION ===")
    c.execute('SELECT region, COUNT(*) FROM outlets GROUP BY region')
    regions = c.fetchall()
    for row in regions:
        print(f'Region: {row[0]}, Count: {row[1]}')
    
    print("\n=== EXECUTIONS ===")
    c.execute('SELECT COUNT(*) FROM executions WHERE status = "Completed"')
    completed_count = c.fetchone()[0]
    print(f'Completed executions: {completed_count}')
    
    c.execute('SELECT COUNT(*) FROM executions')
    total_executions = c.fetchone()[0]
    print(f'Total executions: {total_executions}')
    
    # Test outlet access for each field agent region
    print("\n=== OUTLET ACCESS BY FIELD AGENT REGION ===")
    
    # Get unique regions from field agents
    c.execute('''
    SELECT DISTINCT region FROM users 
    WHERE role = 'field_agent' AND region IS NOT NULL
    ''')
    agent_regions = [row[0] for row in c.fetchall()]
    
    for region in agent_regions:
        print(f"\n--- Region: {region} ---")
        
        # Count field agents in this region
        c.execute('''
        SELECT COUNT(*) FROM users 
        WHERE role = 'field_agent' AND UPPER(region) = UPPER(?)
        ''', (region,))
        agent_count = c.fetchone()[0]
        
        # Count available outlets for this region
        c.execute('''
        SELECT COUNT(*) FROM outlets o
        WHERE UPPER(o.region) = UPPER(?)
        AND o.id NOT IN (
            SELECT DISTINCT outlet_id FROM executions
            WHERE status = 'Completed' AND outlet_id IS NOT NULL
        )
        ''', (region,))
        available_count = c.fetchone()[0]
        
        print(f"Field agents: {agent_count}, Available outlets: {available_count}")
        
        # Show sample outlets if any exist
        if available_count > 0:
            c.execute('''
            SELECT o.id, o.urn, o.outlet_name, o.region, o.state 
            FROM outlets o
            WHERE UPPER(o.region) = UPPER(?)
            AND o.id NOT IN (
                SELECT DISTINCT outlet_id FROM executions
                WHERE status = 'Completed' AND outlet_id IS NOT NULL
            )
            LIMIT 3
            ''', (region,))
            sample_outlets = c.fetchall()
            
            print("Sample outlets:")
            for outlet in sample_outlets:
                print(f'  - {outlet[1]}: {outlet[2]} ({outlet[3]}, {outlet[4] or "No State"})')
        
        # Show sample field agents in this region
        c.execute('''
        SELECT username, state, lga FROM users 
        WHERE role = 'field_agent' AND UPPER(region) = UPPER(?) 
        LIMIT 3
        ''', (region,))
        sample_agents = c.fetchall()
        
        print("Sample field agents:")
        for agent in sample_agents:
            print(f'  - {agent[0]} ({agent[1] or "No State"}, {agent[2] or "No LGA"})')
    
    conn.close()

if __name__ == "__main__":
    check_database()