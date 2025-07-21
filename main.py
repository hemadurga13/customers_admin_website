import pymysql
import flask
import os
from flask import request, Flask, render_template, redirect,session


conn=pymysql.connect(host="localhost",user="root",password="root",db="shopping")
cursor=conn.cursor()

app=Flask(__name__)

admin_username="admin"
admin_password="admin"

app.secret_key="adminhema123kani"

app_root=os.path.dirname(os.path.abspath(__file__))
products_root=app_root+"\\static\\products"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/adminLogin")
def admin():
    return render_template("adminLogin.html")

@app.route("/adminLoginAction", methods=["POST"])
def adminLoginAction():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == admin_username and password == admin_password:
        session["role"] = 'admin'
        return redirect('/adminHome')
    else:
        return render_template("message.html", message='Invalid Login details')


@app.route('/adminHome')
def adminHome():
    return render_template('adminHome.html')


@app.route('/adminAddLocations')
def adminAddLocations():
    cursor.execute("select * from locations")
    locations = cursor.fetchall()
    return render_template('adminAddLocations.html',locations=locations)

@app.route('/adminAddLocationsAction', methods=["POST"])
def adminAddLocationsAction():
    location_name=request.form.get('location')

    # to check for duplicate location

    count = cursor.execute("select * from locations where location_name='" + str(location_name) + "'")
    if count > 0:
        return render_template("adminmessage.html", adminmessage="Location Already Exists")

    cursor.execute("insert into locations(location_name) values('" + str(location_name) + "')")
    conn.commit()
    return render_template("adminmessage.html", adminmessage="Location Added Successfully")

@app.route("/viewSellers")
def viewSellers():
    cursor.execute("select * from sellers")
    sellers=cursor.fetchall()
    return render_template("viewSellers.html",sellers=sellers)


@app.route("/set_status")
def set_status():
    seller_id = request.args.get("seller_id")
    status = request.args.get("status")
    if(status=="UNVERIFIED"):
        cursor.execute("update sellers set status='VERIFIED' where seller_id='"+str(seller_id)+"'  ")
    else:
        cursor.execute("update sellers set status='UNVERIFIED' where seller_id='"+str(seller_id)+"'  ")
    conn.commit()
    return redirect("/viewSellers")



@app.route('/viewDelivery')
def viewDelivery():
    cursor.execute("select * from delivery_agencies")
    agencies = cursor.fetchall()
    cursor.execute("select * from locations")
    locations = cursor.fetchall()
    return render_template("viewDelivery.html", agencies =agencies, locations=locations)


@app.route('/addDeliveryAction',methods=["POST"])
def addDeliveryAction():
    name=request.form.get("name")
    phone=request.form.get("phone")
    password=request.form.get("password")
    location_id=request.form.get("location_id")

    #counting for duplicate location place by phone number

    count = cursor.execute("select * from delivery_agencies where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("adminmessage.html", adminmessage="Delivery Agency Already Exists")

    cursor.execute("insert into delivery_agencies(agency_name,phone,password,location_id) values ('"+ str(name) +"', '"+ str(phone) +"','"+ str(password) +"','"+ str(location_id) +"')")
    conn.commit()
    return render_template("adminmessage.html", adminmessage='Delivery Agency Added Successfully')


@app.route("/deliveryAgencyLogin")
def deliveryAgencyLogin():
    return render_template("deliveryAgencyLogin.html")

@app.route("/deliveryHome")
def deliveryHome():
    return render_template("deliveryHome.html")

@app.route("/deliveryAgencyAction", methods=["POST"])
def deliveryAgencyAction():
    name=request.form.get("name")
    password=request.form.get("password")
    count = cursor.execute("select * from delivery_agencies where agency_name='" + str(name) + "' and password='" + str(password) + "' ")
    deliveryAgencies = cursor.fetchall()

    if count > 0:
        # sessions
        session['agency_id']=deliveryAgencies[0][0]
        session['role']='Delivery Agent'
        return redirect("/deliveryHome")
    else:
        return render_template("message.html", message="Invalid Login Details")



@app.route("/customerRegistration")
def customerRegistration():
    cursor.execute("select * from locations")
    locations = cursor.fetchall()
    return render_template("customerRegistration.html", locations=locations)


@app.route("/customerRegistrationAction", methods=["POST"])
def customerRegistrationAction():
    customer_name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    address = request.form.get('address')
    location_id = request.form.get('location_id')
    password = request.form.get('password')


    # to check for duplicate email id & phone number

    count = cursor.execute("select * from customers where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")

    count = cursor.execute("select * from customers where email='" + str(email) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")


    cursor.execute("insert into customers(customer_name, phone, email, password, address, location_id) values('" + str(customer_name) + "', '" + str(phone) + "','" + str(email) + "','" + str(password) + "', '"+str(address)+"', '"+ str(location_id) +"')")
    conn.commit()
    return render_template("message.html", message="Customer Registration Successful")

@app.route("/customerLogin")
def customerLogin():
    return render_template("customerLogin.html")

@app.route("/customerHome")
def customerHome():
    return render_template("customerHome.html")

@app.route('/customerLoginAction',methods=['post'])
def customerLoginAction():
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute("select * from customers where email='" + str(email) + "' and password='"+ str(password) +"' ")
    customer= cursor.fetchone()
    if customer:
        #sessions
        session['customer_id']=customer[0] #id
        session['role']='customer'
        return redirect('/customerHome')
    else:
        return render_template("message.html", message="Invalid Login Details")

@app.route('/viewProducts')
def viewProducts():
    

    cursor.execute("select * from sellers")
    sellers = cursor.fetchall()


    seller_id= request.args.get("seller_id")

    category_id = request.args.get("category_id")

    sub_category_id = request.args.get("sub_category_id")

    product_name = request.args.get("product_name")
    
    if seller_id==None:
        seller_id=""
    
    if category_id==None:
        category_id=""
        
    if sub_category_id==None:
        sub_category_id=""
    
    if product_name==None:
        product_name=""

    sql = ""
    if seller_id=="" and category_id=="" and sub_category_id=="":
        sql= "select * from products where product_name like '%" +str(product_name)+ "%'"
        # print(sql)
    
    elif seller_id!="" and category_id=="" and sub_category_id=="":
        sql="select * from products where seller_id='"+str(seller_id)+"' and product_name like '%" +str(product_name)+ "%'"
        # print(sql)

    elif seller_id == "" and category_id != "" and sub_category_id == "":
        sql = " select * from products where sub_category_id in (select sub_category_id from sub_categories where category_id='" + str(
            category_id) + "') and product_name like '%" +str(product_name)+ "%' "
        # print(sql)

    elif seller_id=="" and category_id=="" and sub_category_id!="":
        sql="select * from products where sub_category_id='"+str(sub_category_id)+"' and product_name like '%"+str(product_name)+"%'"
        # print(sql)

    elif seller_id != "" and category_id != "" and sub_category_id != "":
        sql = " select * from products where seller_id='"+str(seller_id)+"' and sub_category_id in (select sub_category_id from sub_categories where category_id='" + str(
            category_id) + "') and sub_category_id='"+str(sub_category_id)+"' and product_name like '%" + str(product_name) + "%' "
        # print(sql)

    elif seller_id != "" and category_id != "" and sub_category_id == "":
        sql = " select * from products where seller_id='" + str(
            seller_id) + "' and sub_category_id in (select sub_category_id from sub_categories where category_id='" + str(
            category_id) + "') and product_name like '%" + str(
            product_name) + "%' "

    cursor.execute(sql)
    products = cursor.fetchall()
    if category_id!="":
        cursor.execute("select * from sub_categories where category_id='"+str(category_id)+"'")
    else:
        cursor.execute("select * from sub_categories")
    sub_categories = cursor.fetchall()
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render_template('viewProducts.html', sellers =sellers, product_name= product_name,categories =categories , sub_categories = sub_categories, products=products, seller_id=seller_id, category_id=category_id, sub_category_id=sub_category_id, str=str)

@app.route("/shoppingCart")
def shoppingCart():
    product_id= request.args.get('product_id')
    quantity= request.args.get('quantity')

    if 'customer_id' not in session:
        return redirect('/customerLogin')
    customer_id = session['customer_id']
    
    cursor.execute("select * from products where product_id='"+str(product_id)+"'")
    products = cursor.fetchone()

    if products is None:
        return "Error"

    seller_id= products[6]
    return render_template("shoppingCart.html", seller_id= seller_id, product_id=product_id,quantity=quantity, customer_id=customer_id)


@app.route("/sellerRegistration")
def sellerRegistration():
    cursor.execute("select * from locations")
    locations=cursor.fetchall()
    return render_template("sellerRegistration.html",locations=locations)

@app.route("/sellerRegistrationAction", methods=["POST"])
def sellerRegistrationAction():
    seller_name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    location_id = request.form.get('location_id')
    password = request.form.get('password')
    # to check for duplicate email id & phone number

    count = cursor.execute("select * from sellers where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")

    count = cursor.execute("select * from sellers where email='" + str(email) + "'")
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    cursor.execute("insert into sellers(seller_name, phone, email, location_id, password) values('" + str(seller_name) + "', '" + str(phone) + "','" + str(email) + "','"+ str(location_id) +"','" + str(password) + "')")
    conn.commit()
    return render_template("message.html", message="Seller Registration Successful")


@app.route("/sellerLogin")
def sellerLogin():
    return render_template("sellerLogin.html")


@app.route("/sellerHome")
def sellerHome():
    return render_template("sellerHome.html")

@app.route('/sellerLoginAction', methods=["POST"])
def sellerLoginAction():
    email = request.form.get('email')
    password = request.form.get('password')
    count = cursor.execute("select * from sellers where email='" + str(email) + "' and password='"+ str(password) +"' ")
    if count > 0:
        sellers = cursor.fetchall()
        session['seller_id']=sellers[0][0]
        status=sellers[0][5]
        session['role']='seller'
        if status=='VERIFIED':
            return redirect("/sellerHome")
        else:
            return render_template("message.html",message="Not Yet VERIFIED by the Administrator")
    else:
        return render_template("message.html", message="Invalid Login Details")

#seller
@app.route('/addProducts')
def addProducts():
    if 'seller_id' not in session:
        return redirect('/sellerLogin')

    seller_id = session['seller_id']
    category_id=request.args.get('category_id')


    product_id = request.args.get("product_id")
    cursor.execute("select * from products where product_id='" + str(product_id) + "'")
    details = cursor.fetchone()

    cursor.execute("select * from categories")
    categories=cursor.fetchall()

    query="select * from sub_categories"

    if category_id:
        cursor.execute("select * from sub_categories where category_id='" + str(category_id) + "'")
    else:
        cursor.execute(query)
    sub_categories = cursor.fetchall()

    cursor.execute("select * from products where seller_id='" + str(seller_id) + "'")
    products = cursor.fetchall()

    return render_template('addProducts.html',seller_id=seller_id,categories=categories,  sub_categories=sub_categories,products=products,details=details,get_sub_category_id_by_sub_category_name=get_sub_category_id_by_sub_category_name)


def get_sub_category_id_by_sub_category_name(sub_category_id):
    cursor.execute("select * from sub_categories where sub_category_id='"+str(sub_category_id)+"'")
    sub_category_name=cursor.fetchone()
    return sub_category_name



@app.route('/addProductsAction',methods=["POST"])
def addProductsAction():
    if 'seller_id' not in session:
        return redirect('/sellerLogin')

    seller_id = session['seller_id']
    name=request.form.get('name')
    description=request.form.get('description')
    image=request.files.get('image')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    sub_category_id = request.form.get('sub_category_id')

    if image and image.filename:
        filename = image.filename
        save_path = os.path.join(products_root, filename)
        image.save(save_path)
    else:
        return render_template("sellermessage.html", sellermessage="Image upload failed or missing")

    cursor.execute("insert into products(product_image,product_name,description,price,quantity,sub_category_id,seller_id) values('"+str(filename)+"', '"+str(name)+"', '"+str(description)+"', '"+str(price)+"', '"+str(quantity)+"', '"+str(sub_category_id)+"', '"+str(seller_id)+"' )")
    conn.commit()
    return render_template("sellermessage.html",sellermessage="Product Added Successfully")


@app.route('/editProducts')
def editProducts():
    product_id=request.args.get("product_id")
    cursor.execute("select * from products where product_id='"+ str(product_id) +"'")
    details=cursor.fetchone()
    return render_template("editProducts.html",details=details)

@app.route('/editProductsAction',methods=["POST"])
def editProductsAction():
    product_id=request.form.get('product_id')
    name=request.form.get('name')
    description=request.form.get('description')
    # image=request.files.get('image')
    price=request.form.get('price')
    quantity=request.form.get('quantity')
    # sub_category_id=request.args.get('sub_category_id')
    cursor.execute("update products set product_name='"+ str(name) +"',description= '"+ str(description) +"', price= '"+ str(price) +"', quantity='"+ str(quantity) +"' where product_id='"+str(product_id)+"'")
    conn.commit()
    return redirect('/addProducts')


@app.route('/addCategories')
def addCategories():
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render_template("addCategories.html",categories=categories)

@app.route('/addCategoriesAction', methods=["POST"])
def addCategoriesAction():
    name=request.form.get("name")
    cursor.execute("insert into categories(category_name) values ('"+ str(name) +"')")
    conn.commit()
    return render_template("adminmessage.html",adminmessage="Category Added Successfully")

@app.route('/addSubCategories')
def addSubCategories():

    cursor.execute("select * from categories")
    categories=cursor.fetchall()

    category_id=request.args.get("category_id")
    cursor.execute("select * from sub_categories")
    if category_id!=None:
        query="select * from sub_categories where category_id='"+str(category_id)+"'"
    else:
        query="select * from sub_categories"
    cursor.execute(query)
    subCategories=cursor.fetchall()
    return render_template("addSubCategories.html",categories=categories,subCategories=subCategories,get_category_id_by_category_name=get_category_id_by_category_name,  category_id=category_id, str=str)


def get_category_id_by_category_name(category_id):
    cursor.execute("select * from categories where category_id='"+str(category_id)+"'")
    category_name=cursor.fetchone()
    return category_name



@app.route('/addSubCategoriesAction', methods=["POST"])
def addSubCategoriesAction():
    name=request.form.get("name")
    category_id=request.form.get("category_id")
    cursor.execute("insert into sub_categories(sub_category_name, category_id) values ('"+ str(name) +"', '"+str(category_id)+"')")
    conn.commit()
    return render_template("adminmessage.html",adminmessage="Sub Category Added Successfully")


@app.route("/logout")
def logout():
    return redirect('/')

app.run(debug=True)