from flask import Flask, render_template, request, redirect, url_for, session
import oracledb
import pandas as pd
import os

def connect_to_db():

    try:
        
       # cx_Oracle.init_oracle_client()

        dsn = oracledb.makedsn('oracle.wpi.edu', 1521, sid = 'ORCL')

        db = oracledb.connect(user = 'zzhang18',
                               password = 'ZZHANG18',
                               dsn = dsn)
        return db
        
    except oracledb.DatabaseError as e:
        raise
    

def fetch_data(sql, params = None):
    '''
    Execute SQL statement to pull data and store in dataframe
    '''
    
    try:
        cursor = connect_to_db().cursor()
        cursor.execute(sql, params or [])
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] # Extract column names
        df = pd.DataFrame(data, columns=columns) # Create dataframe
        cursor.close() # Close connection

        return df

    except oracledb.DatabaseError as e:
        raise
        

def insert_data(sql, data):
    '''
    Documentation: https://python-oracledb.readthedocs.io/en/latest/user_guide/batch_statement.html
    '''

    try:
        con = connect_to_db()
        cursor = con.cursor()

        cursor.executemany(sql, data)

        con.commit()
        cursor.close()
               
    except cx_Oracle.DatabaseError as e:
        raise
        

def update(sql, data):
    '''
    Documentation: https://python-oracledb.readthedocs.io/en/latest/user_guide/batch_statement.html

    '''
    try:

        con = connect_to_db()
        cursor = con.cursor()

        cursor.executemany(sql, data)

        con.commit()
        cursor.close()
               
    except cx_Oracle.DatabaseError as e:
        raise
        

# Create instance
app = Flask(__name__)

# Secret key for session
app.secret_key = os.urandom(24)

@app.route("/") # Route is the place to go (/ represents the base url or the homepage)
def home_page():
    return render_template('./employee/SignIn.html')

# @app.route('/product/<int:commodityID>')
# def product_detail(commodityID):
    
#     custID=session.get('custID') #Fetch from session
#     conn=connect_to_db()
#     cursor=conn.cursor()
#     cursor.execute("SELECT name, price FROM commodity_store WHERE commodityID=:id",[commodityID])
#     product=cursor.fetchone()

#     #Fetch Reviews
#     cursor.execute("""SELECT m.memberName, r.rating, r.comment, TO_CHAR(r.reviewDate, 'YYYY-MM-DD') FROM REVIEW r JOIN customer c ON r.custID=c.custID JOIN member m ON c.custID = m.custID WHERE r.commodityID=:id ORDER BY r.reviewDate DESC""", [commodityID])
#     reviews=cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('product_detail.html', product=product, reviews=reviews)


@app.route('/employee/signin', methods=['POST'])
def employee_signin():
    ssn = request.form['ssn']
    password = request.form['password']

    # Connect to db
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if the employee exists
    cursor.execute("SELECT * FROM EMPLOYEE WHERE ssn=:ssn AND password=:password", [ssn, password])
    employee_data = cursor.fetchone()

    if employee_data:
        # Store employee data in session
        session['ssn'] = employee_data[0]
        session['name'] = employee_data[1]
        session['birthday'] = employee_data[2]
        session['salary'] = employee_data[3]
        session['position'] = employee_data[4]
        if session['position'] == 'cashier':
            return render_template('employee/cashier/cashier.html', personal_info=session)
        elif session['position'] == 'custodian':
            return render_template('employee/custodian/custodian.html', personal_info=session)
        elif session['position'] == 'inventory_manager':
            return render_template('employee/inventory_manager/inventory_manager.html', personal_info=session)
        elif session['position'] == 'stock_clerk':
            return render_template('employee/stock_clerk/stock_clerk.html', personal_info=session)
        else:
            return "Invalid position"
    else:
        return "Invalid credentials"
    
@app.route('/employee/basic_info', methods=['GET'])
def display_basic_info():
    if session['position'] == 'cashier':
        return render_template('employee/cashier/cashier.html', personal_info=session)
    elif session['position'] == 'custodian':
        return render_template('employee/custodian/custodian.html', personal_info=session)
    elif session['position'] == 'inventory_manager':
        return render_template('employee/inventory_manager/inventory_manager.html', personal_info=session)
    elif session['position'] == 'stock_clerk':
        return render_template('employee/stock_clerk/stock_clerk.html', personal_info=session)
    else:
        return "Invalid position"

@app.route('/employee/inventory_manager/inventory.html', methods=['GET'])
def inventory_lookup():
    session['inventory_id'] = []
    conn=connect_to_db()
    cursor=conn.cursor()
    result = cursor.execute("select * from monitor where ssn=:ssn", [session['ssn']])
    for row in result:
        session['inventory_id'].append(row[1])
    cursor.close()
    # Fetch data from the corresponding inventory
    inventory_items = []
    cursor=conn.cursor()
    for iid in session['inventory_id']:
        result = cursor.execute("select * from commodity_store where iid = :id", [iid])
        inventory_items = inventory_items + result.fetchall()
    cursor.close()
    conn.close()
    return render_template('/employee/inventory_manager/inventory.html', items=inventory_items)

@app.route('/employee/inventory_manager/alert.html', methods=['GET'])
def alert_lookup():
    session['inventory_id'] = []
    conn=connect_to_db()
    cursor=conn.cursor()
    result = cursor.execute("select * from monitor where ssn=:ssn", [session['ssn']])
    for row in result:
        session['inventory_id'].append(row[1])
    cursor.close()
    # Fetch data from the corresponding inventory
    alerts = []
    cursor=conn.cursor()
    for iid in session['inventory_id']:
        result = cursor.execute("select * from inventory_alerts_send A join commodity_store B on A.commodityID = B.commodityID where B.iid = :id", [iid])
        alerts = alerts + result.fetchall()
    cursor.close()
    conn.close()
    print(alerts)
    return render_template('/employee/inventory_manager/alert.html', items=alerts)

if __name__ == '__main__':
    app.run(debug=True)

