import flask
from flask import Flask, render_template, request, redirect,session
import pymysql

conn=pymysql.connect(host='localhost',user='root',passwd='root',db='sample_web')
cursor=conn.cursor()

app = Flask(__name__)
app.secret_key="hema"

admin_username='admin'
admin_password='yaminikanish'

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/adminLogin')
def adminLogin():
    return render_template("adminLogin.html")


@app.route('/adminLoginAction', methods=['POST'])
def adminLoginAction():
    username=request.form.get('username')
    password=request.form.get('password')
    if username==admin_username and password==admin_password:
        session["role"]='admin'
        return redirect('/adminHome')
    else:
        return render_template("message.html", message='Invalid Login details')

@app.route('/adminHome')
def adminHome():
    return render_template('adminHome.html')


@app.route('/customerLogin')
def customerLogin():
    return render_template("customerLogin.html")

@app.route('/customerLoginAction',methods=['post'])
def customerLoginAction():
    email = request.form.get('email')
    password = request.form.get('password')
    count = cursor.execute("select * from customer where email='" + str(email) + "' and password='"+ str(password) +"' ")
    if count > 0:
        #sessions
        customers=cursor.fetchall() #(('01','hema',...))
        session['customer_id']=customers[0][0] #id
        session['role']='customer'
        return redirect("/customerHome")
    else:
        return render_template("message.html", message="Invalid Login Details")

@app.route('/customerHome')
def customerHome():
    return render_template("customerHome.html")

@app.route('/customerProfile')
def customerProfile():
    customer_id=session['customer_id']
    cursor.execute("select * from customer where customer_id='"+ str(customer_id) +"'")
    customers=cursor.fetchall()
    return render_template("customerProfile.html",customer=customers[0])


@app.route('/customerRegistration')
def customerRegistration():
    return render_template("customerRegistration.html")

@app.route('/custRegistrationAction', methods=['post'])
def custRegistrationAction():
    name= request.form.get('name')
    email= request.form.get('email')
    phone= request.form.get('phone')
    password= request.form.get('password')

    #to check for duplicate email id & phone number
    count = cursor.execute("select * from customer where email='" + str(email) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    count = cursor.execute("select * from customer where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")

    cursor.execute("insert into customer(name, email, phone, password) values('"+ str(name) +"', '"+str(email)+"','"+str(phone)+"','"+str(password)+"')")
    conn.commit()
    return render_template("message.html", message="Customer Registration Successful")


@app.route("/customersDetails")
def customersDetails():
    cursor.execute("select * from customer")
    view_customers=cursor.fetchall()
    return render_template('customersDetails.html',view_customers=view_customers)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

app.run(debug=True)