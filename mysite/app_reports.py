from flask import Blueprint, jsonify, request
import sqlite3
import json
import random
import os

reports_bp = Blueprint('reports', __name__)

# Database helper function
def get_db_connection():
    db_path = os.environ.get('DATABASE_PATH', 'dangote_execution.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@reports_bp.route('/reports/product_availability')
def product_availability_report():
    # Get filter parameters
    region = request.args.get('region', 'all')
    date_range = request.args.get('date_range', 'month')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Define Dangote product list
    DANGOTE_PRODUCTS = [
        "Dangote Ordinary Portland Cement 42.5R",
        "Dangote Ordinary Portland Cement 42.5N",
        "Dangote Falcon Portland Cement",
        "Dangote 3X Cement",
        "Dangote BlocMaster Cement"
    ]
    
    # Get all executions with product data
    query = '''
    SELECT e.id, e.products_available, o.region, o.state, o.local_govt, o.outlet_name, e.execution_date
    FROM executions e
    JOIN outlets o ON e.outlet_id = o.id
    WHERE e.products_available IS NOT NULL
    '''
    
    # Add region filter if specified
    params = []
    if region != 'all':
        query += " AND o.region = ?"
        params.append(region)
    
    # Add date filter - in a real app, this would be implemented
    # For demo purposes, we'll skip this
    
    c.execute(query, params)
    executions = c.fetchall()
    conn.close()
    
    # Process data
    product_stats = {product: {'available': 0, 'not_available': 0} for product in DANGOTE_PRODUCTS}
    product_by_region = {}
    
    # For demo, generate some sample data
    if len(executions) == 0:
        return jsonify(generate_sample_product_data(DANGOTE_PRODUCTS))
    
    # Process real data if available
    for exe in executions:
        products = json.loads(exe['products_available']) if exe['products_available'] else {}
        
        for product in DANGOTE_PRODUCTS:
            if product in products and products[product]:
                product_stats[product]['available'] += 1
            else:
                product_stats[product]['not_available'] += 1
            
            # Region stats
            if exe['region'] not in product_by_region:
                product_by_region[exe['region']] = {product: {'available': 0, 'not_available': 0} for product in DANGOTE_PRODUCTS}
            
            if product in products and products[product]:
                product_by_region[exe['region']][product]['available'] += 1
            else:
                product_by_region[exe['region']][product]['not_available'] += 1
    
    return jsonify({
        'product_stats': product_stats,
        'product_by_region': product_by_region
    })

@reports_bp.route('/reports/execution_summary')
def execution_summary_report():
    # Get filter parameters
    region = request.args.get('region', 'all')
    date_range = request.args.get('date_range', 'month')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get outlet counts
    query = "SELECT COUNT(*) as total FROM outlets"
    params = []
    
    if region != 'all':
        query += " WHERE region = ?"
        params.append(region)
    
    c.execute(query, params)
    total_outlets = c.fetchone()['total']
    
    # Get execution counts
    query = '''
    SELECT COUNT(DISTINCT e.outlet_id) as executed_outlets, COUNT(*) as total_executions 
    FROM executions e
    JOIN outlets o ON e.outlet_id = o.id
    '''
    
    if region != 'all':
        query += " WHERE o.region = ?"
        params = [region]
    else:
        params = []
    
    c.execute(query, params)
    execution_stats = c.fetchone()
    
    # If no data, generate sample data
    if not execution_stats or execution_stats['executed_outlets'] == 0:
        conn.close()
        return jsonify(generate_sample_execution_data())
    
    # Get execution by region
    query = '''
    SELECT o.region, COUNT(DISTINCT e.outlet_id) as executed, COUNT(DISTINCT o.id) as total
    FROM outlets o
    LEFT JOIN executions e ON o.id = e.outlet_id
    '''
    
    if region != 'all':
        query += " WHERE o.region = ?"
        query += " GROUP BY o.region"
        c.execute(query, [region])
    else:
        query += " GROUP BY o.region"
        c.execute(query)
    
    execution_by_region = {}
    for row in c.fetchall():
        execution_by_region[row['region']] = {
            'executed': row['executed'],
            'total': row['total'],
            'percentage': round((row['executed'] / row['total']) * 100, 2) if row['total'] > 0 else 0
        }
    
    conn.close()
    
    return jsonify({
        'total_outlets': total_outlets,
        'executed_outlets': execution_stats['executed_outlets'],
        'total_executions': execution_stats['total_executions'],
        'coverage_percentage': round((execution_stats['executed_outlets'] / total_outlets) * 100, 2) if total_outlets > 0 else 0,
        'execution_by_region': execution_by_region
    })

@reports_bp.route('/reports/image_analysis')
def image_analysis_report():
    # In a real application, this would perform actual image analysis
    # For this prototype, we'll return sample data
    return jsonify(generate_sample_image_analysis())

# Helper functions to generate sample data for demo
def generate_sample_product_data(product_list):
    regions = ['SW', 'SE', 'NC', 'NW', 'NE']
    
    product_stats = {}
    product_by_region = {}
    
    for product in product_list:
        available = random.randint(20, 100)
        not_available = random.randint(10, 50)
        product_stats[product] = {
            'available': available,
            'not_available': not_available
        }
    
    for region in regions:
        product_by_region[region] = {}
        for product in product_list:
            available = random.randint(5, 30)
            not_available = random.randint(3, 15)
            product_by_region[region][product] = {
                'available': available,
                'not_available': not_available
            }
    
    return {
        'product_stats': product_stats,
        'product_by_region': product_by_region
    }

def generate_sample_execution_data():
    regions = ['SW', 'SE', 'NC', 'NW', 'NE']
    total_outlets = random.randint(100, 200)
    executed_outlets = random.randint(50, total_outlets)
    
    execution_by_region = {}
    for region in regions:
        regional_total = random.randint(15, 50)
        regional_executed = random.randint(5, regional_total)
        execution_by_region[region] = {
            'executed': regional_executed,
            'total': regional_total,
            'percentage': round((regional_executed / regional_total) * 100, 2)
        }
    
    return {
        'total_outlets': total_outlets,
        'executed_outlets': executed_outlets,
        'total_executions': executed_outlets + random.randint(5, 20),
        'coverage_percentage': round((executed_outlets / total_outlets) * 100, 2),
        'execution_by_region': execution_by_region
    }

def generate_sample_image_analysis():
    regions = ['SW', 'SE', 'NC', 'NW', 'NE']
    
    total_images = random.randint(100, 150)
    compliant_count = random.randint(60, total_images)
    compliant_percentage = (compliant_count / total_images) * 100
    
    by_region = {}
    for region in regions:
        by_region[region] = {
            'compliant_percentage': random.randint(60, 95)
        }
    
    categories = [
        'Product Placement',
        'Branding Visibility',
        'Stock Organization',
        'Pricing Displays',
        'Overall Cleanliness'
    ]
    
    by_category = {}
    for category in categories:
        by_category[category] = {
            'score': random.randint(60, 95)
        }
    
    return {
        'overall': {
            'total_images': total_images,
            'compliant_count': compliant_count,
            'compliant_percentage': compliant_percentage
        },
        'by_region': by_region,
        'by_category': by_category
    }