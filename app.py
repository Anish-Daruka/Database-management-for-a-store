from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Models
class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    Item_SKU = db.Column(db.String, primary_key=True)
    Item_Name = db.Column(db.String, nullable=False)
    Item_Price = db.Column(db.Float, nullable=False)
    Item_Qty = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    __tablename__ = 'customers'
    c_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_name = db.Column(db.String, nullable=False)
    c_email = db.Column(db.String, unique=True, nullable=False)
    c_contact = db.Column(db.String)

class Staff(db.Model):
    __tablename__ = 'staff'
    s_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_name = db.Column(db.String, nullable=False)
    s_email = db.Column(db.String, unique=True, nullable=False)
    s_password = db.Column(db.String)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    t_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_ID = db.Column(db.Integer, db.ForeignKey('customers.c_ID'), nullable=False)
    t_date = db.Column(db.Date, nullable=False)
    t_amount = db.Column(db.Float, nullable=False)
    t_category = db.Column(db.String, nullable=False)

    customer= db.relationship('Customer', backref='transactions')


def fitrandomvalue():
    # Add random values to InventoryItem table
    for _ in range(5):
        item = InventoryItem(
            Item_SKU=f'SKU{random.randint(1000, 9999)}',
            Item_Name=f'Item{random.randint(1, 100)}',
            Item_Price=round(random.uniform(10.0, 100.0), 2),
            Item_Qty=random.randint(1, 50)
        )
        db.session.add(item)

    # Add random values to Customer table
    for _ in range(5):
        customer = Customer(
            c_name=f'Customer{random.randint(1, 100)}',
            c_email=f'customer{random.randint(1, 100)}@example.com',
            c_contact=f'{random.randint(1000000000, 9999999999)}'
        )
        db.session.add(customer)

    # Add random values to Staff table
    for _ in range(5):
        staff = Staff(
            s_name=f'Staff{random.randint(1, 100)}',
            s_email=f'staff{random.randint(1, 100)}@example.com',
            s_password='password'
        )
        db.session.add(staff)

    # Add random values to Transaction table
    for _ in range(5):
        transaction = Transaction(
            c_ID=random.randint(1, 5),
            t_date=datetime.now().date(),
            t_amount=round(random.uniform(20.0, 200.0), 2),
            t_category=f'Category{random.randint(1, 5)}'
        )
        db.session.add(transaction)

    db.session.commit()



@app.route('/customers', methods=['GET'])
def get_customers():
    return render_template('customers.html',check=0, customers=Customer.query.all())


@app.route('/customer/<int:customer_id>/transactions', methods=['GET'])
def get_customer_transactions(customer_id):
    customer = Customer.query.get_or_404(customer_id)  # Fetch the customer or return 404 if not found
    transactions = Transaction.query.filter_by(c_ID=customer_id).all()  # Get all transactions for the customer
    return render_template('transactions.html', customers=0,transactions=transactions)



@app.route('/addcustomer', methods=['GET', 'POST'])
def addcustomer():
    if request.method == 'POST':
        customer_name = request.form.get('c_name')
        customer_email = request.form.get('c_email')
        customer_contact = request.form.get('c_contact')
        new_customer = Customer(c_name=customer_name, c_email=customer_email, c_contact=customer_contact)
        db.session.add(new_customer)
        db.session.commit() 
        return render_template('customers.html', check=1, customers=Customer.query.all())
    return render_template('customers.html', check=1, customers=Customer.query.all())



@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        item_sku = request.form.get('Item_SKU')
        item_name = request.form.get('Item_Name')
        item_price = request.form.get('Item_Price')
        item_qty = request.form.get('Item_Qty')
        new_item = InventoryItem(Item_SKU=item_sku, Item_Name=item_name, Item_Price=item_price, Item_Qty=item_qty)
        db.session.add(new_item)
        db.session.commit()
    print(request.method)
    return render_template('inventory.html', inventory=InventoryItem.query.all())

@app.route('/stafflist', methods=['GET', 'POST'])
def stafflist():
    if request.method == 'POST':
        staff_ID = request.form.get('s_ID')
        staff_name = request.form.get('s_name')
        staff_email = request.form.get('s_email')
        staff_password = request.form.get('s_password')
        new_staff = Staff(s_ID=staff_ID, s_name=staff_name, s_email=staff_email, s_password=staff_password)
        db.session.add(new_staff)
        db.session.commit()
        return render_template('stafflist.html', staff=Staff.query.all())
    return render_template('stafflist.html', staff=Staff.query.all())



@app.route('/staff', methods=['GET','POST'])
def staff():
    if request.method == 'POST':
            if request.form['action'] == 'login':
                staff_ID = request.form.get('staff_ID')
                password = request.form.get('password')
                staff = Staff.query.filter_by(s_ID=int(staff_ID), s_password=password).first()
                print(password)
                if staff:
                    return render_template('staffdetail.html',staff=Staff.query.filter_by(s_ID=int(staff_ID)).all())
                else:
                    return 'Invalid ID or password'
            elif request.form['action'] == 'adminlogin': 
                password = request.form.get('password')
                if password=='1000':
                    request.method = 'GET'
                    return stafflist()
                else:
                    return "Incorrect Password"   
        
    return render_template('staff.html')


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        customer_id = request.form.get('c_ID')
        transaction_date = request.form.get('T_date')
        transaction_amount = request.form.get('T_amount')
        transaction_category = request.form.get('T_category')
        new_transaction = Transaction(c_ID=customer_id, t_date=transaction_date, t_amount=transaction_amount, t_category=transaction_category)
        db.session.add(new_transaction)
        db.session.commit()
    return render_template('transactions.html', customers=1, transactions=Transaction.query.all())

@app.route('/')
def index():      
     return render_template('index.html')


if(__name__ == '__main__'):
    #  with app.app_context():
    #      db.create_all()
    #      fitrandomvalue() # Add random values to the tables
     app.run(debug=True, port=9000)




def fitvalue():
    # Add random values to InventoryItem table
    for _ in range(5):
        item = InventoryItem(
            Item_SKU=f'SKU{random.randint(1000, 9999)}',
            Item_Name=f'Item{random.randint(1, 100)}',
            Item_Price=round(random.uniform(10.0, 100.0), 2),
            Item_Qty=random.randint(1, 50)
        )
        db.session.add(item)

    # Add random values to Customer table
    for _ in range(5):
        customer = Customer(
            c_name=f'Customer{random.randint(1, 100)}',
            c_email=f'customer{random.randint(1, 100)}@example.com',
            c_contact=f'{random.randint(1000000000, 9999999999)}'
        )
        db.session.add(customer)

    # Add random values to Staff table
    for _ in range(5):
        staff = Staff(
            s_name=f'Staff{random.randint(1, 100)}',
            s_email=f'staff{random.randint(1, 100)}@example.com',
            s_password='password'
        )
        db.session.add(staff)

    # Add random values to Transaction table
    for _ in range(5):
        transaction = Transaction(
            c_ID=random.randint(1, 5),
            t_date=datetime.now().date(),
            t_amount=round(random.uniform(20.0, 200.0), 2),
            t_category=f'Category{random.randint(1, 5)}'
        )
        db.session.add(transaction)

    db.session.commit()