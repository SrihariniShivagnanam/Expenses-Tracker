from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my-database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), unique=True, nullable=False)
     password = db.Column(db.String(60), nullable=False)
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    expensename = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for diff paths
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))  # Redirect to the homepage

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def add():
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    expense = Expense.query.filter_by(id=id).first()
    db.session.delete(expense)
    db.session.commit()
    return redirect('/expenses')


@app.route('/expenses')
def expenses():
    expenses_list = Expense.query.all()
    total = sum(expense.amount for expense in expenses_list)
    t_business = sum(expense.amount for expense in expenses_list if expense.category == 'business')
    t_other = sum(expense.amount for expense in expenses_list if expense.category == 'other')
    t_food = sum(expense.amount for expense in expenses_list if expense.category == 'food')
    t_entertainment = sum(expense.amount for expense in expenses_list if expense.category == 'entertainment')

    return render_template('expenses.html', expenses=expenses_list,
                           total=total, t_business=t_business, t_other=t_other,
                           t_food=t_food, t_entertainment=t_entertainment)


@app.route('/edit/<int:id>')
def updateexpense(id):
    expense = Expense.query.filter_by(id=id).first()
    return render_template('updateexpense.html', expense=expense)

@app.route('/edit', methods=['POST'])
def edit():
    id = request.form['id']
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    category = request.form['category']

    expense = Expense.query.filter_by(id=id).first()
    expense.date = date
    expense.expensename = expensename
    expense.amount = amount
    expense.category = category

    db.session.commit()
    return redirect('/expenses')

@app.route('/addexpense', methods=['POST', 'GET'])
def addexpense():
    if request.method == 'POST':
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form['category']
        expense = Expense(date=date, expensename=expensename, amount=amount, category=category)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully', 'success')
        return redirect('/expenses')

    return render_template('add.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)