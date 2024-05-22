from flask import Flask,render_template,redirect,request,url_for,flash,abort,session,Response,jsonify
import mysql.connector
from datetime import datetime
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer
from key import salt,secret_key,salt2,salt3
from stoken import token
from cmail import sendmail
from otp import genotp
import os
#import re
import stripe
import pdfkit
stripe.api_key='sk_test_51MMsHhSGj898WTbYXSx509gD14lhhXs8Hx8ipwegdytPB1Bkw0lJykMB0yGpCux95bdw1Gk9Gb9nJIWzPEEDxSqf00GEtCqZ8Y'
config=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

app=Flask(__name__)
app.secret_key=b'\xdaA\xd7ZJA\x0c\xb6w\x18@\xb6'
mydb=mysql.connector.connect(host="localhost",user="root",password="premkumar123",db='amma')
app.config['SESSION_TYPE']='filesystem'
Session(app)
@app.route('/')
def welcome():
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select * from property')
    count=cursor.fetchall()
    return render_template('homepage.html',count=count)
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        user=request.form['username']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password']
       
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from user where email=%s',[email])
            count=cursor.fetchone()[0]
            if count == 0:  # Check if count is equal to 0
                # Proceed with sign-up process
                data={'username':user,'mobile':mobile,'email':email,'address':address,'password':password}
                subject='The Confirmation Link For Homefind Website'
                body=f"Click on the link to confirm {url_for('confirm',token=token(data,salt=salt),_external=True)}"
                sendmail(to=email,subject=subject,body=body)
                flash('Verfication link has sent to email')
                return redirect(url_for('login'))
            else:
                raise Exception
        except Exception as e:
            flash('User already exists')
            return redirect(url_for('login'))
    return render_template('signup.html')
@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
        abort(404,'link expired')
    else:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into user(id,username,phone_no,email,address,password) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s)',[data['username'],data['mobile'],data['email'],data['address'],data['password']])
        mydb.commit()
        cursor.close()
        flash('Your details has registered successfully')
        return redirect(url_for('login'))
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('welcome'))
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from user where email=%s and password=%s',[email,password])
            count=cursor.fetchone()[0]
            print(count)
            if count==0:
                raise Exception
        except Exception as e:
            flash('username or password are incorrect')
            return redirect(url_for('login'))
        else:
            session['user']=email
            if not session.get(email):
                session[email]={}
            return redirect(url_for('welcome'))
    return render_template('login.html')
@app.route('/choose1')
def choose1():
    return render_template('choose1.html')
@app.route('/choose2')
def choose2():
    return render_template('choose2.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))
@app.route('/agent_signup', methods=['GET', 'POST'])
def agent_signup():
    if request.method == 'POST':
        user=request.form['username']
        mobile=request.form['phone_number']
        email=request.form['email']
        agency_name=request.form['agency_name']
        address=request.form['address']
        password=request.form['password']
        license_number=request.form['license_number']
        
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from agent where email=%s',[email])
            count=cursor.fetchone()[0]
            print(count)
            if count == 1:
                raise Exception
        except Exception as e:
            flash('user already existed')
            return redirect(url_for('login'))
        else:
            data={'username':user,'mobile':mobile,'email':email,'address':address,'password':password,'license_number':license_number,'agency_name':agency_name}
            subject='The Confirmation Link For HomeFinding app'
            body=f"Click on the link to confirm {url_for('agent_confirm',token=token(data,salt=salt),_external=True)}"
            sendmail(to=email,subject=subject,body=body)
        
        flash('Verification link has been sent to your email')
        return redirect(url_for('agent_login'))  # Redirect to agent login page after signup
    return render_template('agent_signup.html')
@app.route('/agent_confirm/<token>')
def agent_confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
        abort(404,'link expired')
    else:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into agent(id,username,phone_number,email,address,password,agency_name,license_number) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s)',[data['username'],data['mobile'],data['email'],data['address'],data['password'],data['agency_name'],data['license_number']])
        mydb.commit()
        cursor.close()
        flash('Your details has registered successfully')
        return redirect(url_for('agent_login'))
@app.route('/agent_login', methods=['GET', 'POST'])
def agent_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Your authentication logic goes here
        # Example: Check if email and password match with records in the agent table
        
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from agent where email=%s and password=%s',[email,password])
            count=cursor.fetchone()[0]
            print(count)
            if count==0:
                raise Exception
        except Exception as e:
            flash('username or password are incorrect')
            return redirect(url_for('agent_login'))
        else:
            session['agent']=email
            if not session.get(email):
                session[email]={}
            return redirect(url_for('agent_dashboard'))  # Redirect to the agent dashboard
    
        
    return render_template('agentlogin.html')
@app.route('/agentlogout')
def agent_logout():
    if session.get('agent'):
        session.pop('agent')
        return redirect(url_for('welcome'))
    return redirect(url_for('welcome'))
@app.route('/forget',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        email=request.form['id']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from user where email=%s',[email])
        count=cursor.fetchone()[0]
        cursor.close()
        try:
            if count != 1:
                raise Exception
        except Exception as e:
            flash('pls register first')
            return redirect(url_for('signup'))
        else:
            subject='The password Reset link has sent to your email'
            body=f"The link password reset is: {url_for('verify',token=token(email,salt=salt2),_external=True)}"
            sendmail(to=email,subject=subject,body=body)
            flash('The Reset link has sent mail pls verify it')
            return redirect(url_for('forgot'))
    return render_template('forgot.html')
@app.route('/verify/<token>',methods=['GET','POST'])
def verify(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt2,max_age=180)
    except Exception as e:
        abort(404,'link expired')
    else:
        if request.method=='POST':
            npassword=request.form['npassword']
            cpassword=request.form['cpassword']
            if npassword==cpassword:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update user set password=%s where email=%s',[npassword,data])
                mydb.commit()
                cursor.close()
                flash('password has been updated')
                return redirect(url_for('login'))
            else:
                flash('Mismatched password confirmation')
                return render_template('newpassword.html')
    return render_template('newpassword.html')
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if session.get('agent') or session.get('user'):
        if request.method == 'POST':
            
            property_title = request.form.get('title')
            property_description = request.form.get('description')
            property_price = request.form.get('price')
            property_bedrooms = request.form.get('bedrooms')
            property_bathrooms = request.form.get('bathrooms')
            property_location = request.form.get('location')
            property_type = request.form.get('property_type')
            size = request.form.get('size')  # Additional field: Size
            direction_faced = request.form.get('direction_faced')  # Additional field: Direction faced
            year_built = request.form.get('year_built')  # Additional field: Year built
            amenities = request.form.get('amenities')  # Additional field: Amenities
            floor_plan = request.form.get('floor_plan')  # Additional field: Floor plan
            parking = request.form.get('parking')  # Additional field: Parking
            property_condition = request.form.get('property_condition')  # Additional field: Property condition
            view = request.form.get('view')  # Additional field: View
            added_by_user = request.form['added_by_id']  # Additional field: Added by user (optional)
            owner_id = request.form['owner_id']
              # Additional field: Added by user (optional)
            purpose=request.form.get('purpose')
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT id FROM user WHERE email=%s', [owner_id])
            user_id = cursor.fetchone()[0]
            if session.get('user'):
                agent_id=None
                cursor.execute('select bin_to_uuid(id) from user where email=%s', [added_by_user])
                count = cursor.fetchone()[0]
            elif session.get('agent'):
                cursor.execute('select bin_to_uuid(id) from agent where email=%s',[session.get('agent')])
                count=cursor.fetchone()[0]
                agent_id=count
            cursor.close()
            property_image = request.files['image'] 
            filename = property_image.filename
            path = os.path.dirname(os.path.abspath(__file__))
            static_path = os.path.join(path, 'static')
            property_image.save(os.path.join(static_path, filename))
            
            cursor = mydb.cursor(buffered=True)
            cursor.execute('INSERT INTO property (title, description, price, bedrooms, bathrooms, location, property_type, added_by_user, image_url, size, direction_faced, year_built, amenities, floor_plan, parking, property_condition, view,added_by_id,owner_id,purpose,agent_id) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,uuid_to_bin(%s),%s,%s,uuid_to_bin(%s))',
                           [property_title, property_description, property_price, property_bedrooms, property_bathrooms, property_location, property_type, added_by_user, filename, size, direction_faced, year_built, amenities, floor_plan, parking, property_condition, view,count,user_id,purpose,agent_id])
            mydb.commit()
            flash('Details submitted successfully')
            if session.get('agent'):
                return redirect(url_for('agent_dashboard'))
            if session.get('user'):
                return redirect(url_for('welcome'))
            
            
    return render_template('addproperty.html')
@app.route('/agent_dashboard')
def agent_dashboard():
    if 'agent' not in session:
        return redirect(url_for('agent_login'))
    else:
        cursor = mydb.cursor(buffered=True)
        
        # Fetch agent ID
        cursor.execute('SELECT bin_to_uuid(id) FROM agent WHERE email=%s', [session.get('agent')])
        agent_id = cursor.fetchone()[0]
        
        # Fetch properties associated with the agent
        cursor.execute('SELECT * FROM property WHERE agent_id=uuid_to_bin(%s)', [agent_id])
        properties = cursor.fetchall()
        print(properties)
        
        # Fetch distinct users who have sent messages to the agent
        cursor.execute('SELECT DISTINCT sender_id FROM chat_messages WHERE receiver_id=uuid_to_bin(%s)', [agent_id])
        user_ids = cursor.fetchall()
        print(user_ids)
        
        # Fetch user details
        users = []
        for user_id in user_ids:
            cursor.execute('SELECT bin_to_uuid(id), email FROM user WHERE id=%s', [user_id[0]])
            user_details = cursor.fetchone()
            users.append(user_details)
        
        cursor.close()

        # Render the agent dashboard template
        return render_template('agent_dashboard.html', properties=properties, users=users)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        # Redirect to the user login page if not logged in
        return redirect(url_for('login'))
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(id) from user where email=%s', [session.get('user')])
        user_id = cursor.fetchone()[0]

        # Fetch properties added by the user
        cursor.execute('select * from property where added_by_id=uuid_to_bin(%s) and added_by_user=%s', [user_id,session.get('user')])
        properties = cursor.fetchall()
        print(properties)

        # Fetch users who inquired about the user's properties
        cursor.execute('select distinct sender_id from chat_messages where property_id in (select id from property where added_by_id=%s and added_by_user=%s)', [user_id,session.get('user')])
        users = cursor.fetchall()
        print(users)
        l = []
        for i in users:
            cursor.execute('SELECT bin_to_uuid(id), email FROM user WHERE id=%s', [i[0]])
            user_info = cursor.fetchone()
            l.append(user_info)

        cursor.close()

        # Render the user dashboard template
        return render_template('user_dashboard.html', properties=properties, users=l)

@app.route('/dash/<type>')
def dash(type):
    if 'user' in session:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(id) from user where email=%s', [session.get('user')])
        user_id = cursor.fetchone()[0]
        
        cursor.execute('''SELECT id, title, description, price, bedrooms, bathrooms, location, property_type, 
        bin_to_uuid(agent_id), bin_to_uuid(owner_id), bin_to_uuid(added_by_id), added_by_user, image_url, size, direction_faced, 
       year_built, amenities, floor_plan, property_condition, view, status, purpose, parking
FROM property 
WHERE purpose=%s''', [type])
        count = cursor.fetchall()
        return render_template('dash.html', count=count,user_id=user_id)
    return redirect(url_for('login'))

@app.route('/dash1/<type>')
def dash1(type):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select * from property where  parking like %s',[type+'%'])
    count=cursor.fetchall()
    print(count)
    return render_template('dash.html',count=count)
@app.route('/agent_selection',methods=['GET','POST'])
def agent_selection():
    cursor=mydb.cursor(buffered=True)
    cursor.execute('''SELECT bin_to_uuid(id), username, email, password, phone_number, agency_name, license_number, created_at, updated_at, address FROM agent
        ''')
    count=cursor.fetchall()
    return render_template('selectagent.html',count=count)
@app.route('/uchat/<agentId>/<propertyId>', methods=['GET', 'POST'])
def uchat(agentId, propertyId):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT bin_to_uuid(id) FROM user WHERE email=%s', [session.get('user')])
        user_id = cursor.fetchone()[0]

        # Handle None propertyId
        if propertyId == 'None':
            propertyId = None

        # Fetch messages related to the specific property and participants
        cursor.execute("""
            SELECT chat_id, bin_to_uuid(sender_id), bin_to_uuid(receiver_id), message, created_at, file_path, property_id 
            FROM chat_messages 
            WHERE (property_id = %s OR %s IS NULL) AND (
                (sender_id = uuid_to_bin(%s) AND receiver_id = uuid_to_bin(%s)) 
                OR (sender_id = uuid_to_bin(%s) AND receiver_id = uuid_to_bin(%s))
            )
            ORDER BY created_at
        """, (propertyId, propertyId, user_id, agentId, agentId, user_id))
        messages = cursor.fetchall()

        sender = [msg for msg in messages if msg[1] == user_id]
        receiver = [msg for msg in messages if msg[2] == user_id]

        if request.method == 'POST':
            message = request.form['Message']
            file = request.files.get('file')
            filename = None
            if file:
                filename = genotp() + '.jpg'
                path = os.path.dirname(os.path.abspath(__file__))
                static_path = os.path.join(path, 'static')
                file.save(os.path.join(static_path, filename))

            # Adjust the insert query to handle None propertyId
            cursor.execute("""
                INSERT INTO chat_messages (sender_id, receiver_id, property_id, message, file_path) 
                VALUES (uuid_to_bin(%s), uuid_to_bin(%s), %s, %s, %s)
            """, (user_id, agentId, propertyId, message, filename))
            mydb.commit()

            # Fetch the inserted message's property_id (if propertyId was None)
            if propertyId is None:
                cursor.execute("""
                    SELECT * FROM chat_messages 
                    WHERE sender_id = uuid_to_bin(%s) AND receiver_id = uuid_to_bin(%s) AND message = %s
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id, agentId, message))
                propertyId='None'

            return redirect(url_for('uchat', agentId=agentId, propertyId=propertyId))

        return render_template('chatting.html', sender=sender, receiver=receiver, sender_id=user_id, receiver_id=agentId, property_id=propertyId)
    return redirect(url_for('login'))
# @app.route('/chat/<uid>/<propertyId>', methods=['GET', 'POST'])
# def chat(uid, propertyId):
@app.route('/chat/<uid>/<propertyId>', methods=['GET', 'POST'])
def chat(uid, propertyId):
    if session.get('agent'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT BIN_TO_UUID(id) FROM agent WHERE email=%s', [session.get('agent')])
        agent_id = cursor.fetchone()[0]

        # Handle propertyId being 'None'
        propertyId = propertyId if propertyId != 'None' else None

        # Fetch all messages between the agent and the user
        cursor.execute("""
            SELECT chat_id, BIN_TO_UUID(sender_id), BIN_TO_UUID(receiver_id), message, created_at, file_path, property_id 
            FROM chat_messages 
            WHERE (
                (sender_id = UUID_TO_BIN(%s) AND receiver_id = UUID_TO_BIN(%s)) 
                OR (sender_id = UUID_TO_BIN(%s) AND receiver_id = UUID_TO_BIN(%s))
            )
            ORDER BY created_at
        """, (agent_id, uid, uid, agent_id))
        messages = cursor.fetchall()

        # Group messages by property_id
        grouped_messages = {}
        for msg in messages:
            property_id = msg[6]
            if property_id not in grouped_messages:
                grouped_messages[property_id] = []
            grouped_messages[property_id].append(msg)

        if request.method == 'POST':
            message = request.form['Message']
            file = request.files.get('file')
            filename = None
            if file:
                filename = genotp() + '.jpg'
                path = os.path.dirname(os.path.abspath(__file__))
                static_path = os.path.join(path, 'static')
                file.save(os.path.join(static_path, filename))
            
            cursor.execute(
                'INSERT INTO chat_messages (sender_id, receiver_id, property_id, message, file_path) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s), %s, %s, %s)',
                (agent_id, uid, propertyId, message, filename)
            )
            mydb.commit()
            return redirect(url_for('chat', uid=uid,propertyId=propertyId))
        return render_template('agent_chat.html', grouped_messages=grouped_messages, sender_id=agent_id, receiver_id=uid, property_id=propertyId)
    return redirect(url_for('agent_login'))

@app.route('/cart/<int:id1>/<name>/<dis>/<property_type>/<price>/<img>/<location>/<area>/<status>')
def cart(id1,name,dis,property_type,price,img,location,area,status):
    if not session.get('user'):
        return redirect(url_for('login'))
    print(session.get('user'))
    if id1 not in session[session.get('user')]:
        session[session.get('user')][id1]=[id1,name,dis,price,img,property_type,location,area,status,1]
        session.modified=True
        flash(f'{name} added to cart')
        return redirect(url_for('welcome'))
    flash('Item already existed')
    return redirect(url_for('welcome'))
@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    items = session.get(session.get('user')) if session.get(session.get('user')) else 'empty'
    cursor = mydb.cursor(buffered=True)
    cursor.execute('select * from property')
    properties = cursor.fetchall()
    print("Properties:", properties)
    
    if items == 'empty':
        return 'No products were added'
    
    print("Items:", items)  # Debugging line to print items
    
    combined_data = []
    property_dict = {str(prop[0]): prop for prop in properties}  # Create a dictionary with property ID as key
    
    for key, item in items.items():
        property_id = str(key)
        property_data = property_dict.get(property_id)  # Match the property id in item
        if property_data:
            combined_data.append((item, property_data))
        else:
            print(f"No matching property found for item: {item}")
    
    return render_template('cart.html', combined_data=combined_data)


@app.route('/remove/<int:item>')
def remove(item):
    if session.get('user'):
        print(session[session.get('user')])
        session[session.get('user')].pop(item)
        return redirect(url_for('viewcart'))
    return redirect(url_for('login')) 

@app.route('/pay/<itemid>/<name>/<float:price>',methods=['GET','POST'])
def pay(itemid,name,price):
    if session.get('user'):
        username=session.get('user')
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',itemid=itemid,name=username,total=price,_external=True),
            line_items=[
                {
                    'price_data':{
                        'product_data':{
                            'name':name,
                        },
                        'unit_amount':int(price*100),
                        'currency':'inr',
                    },
                    'quantity':1,
                },
                ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<itemid>/<name>/<total>')
def success(itemid,name,total):
    if session.get('user'):
        user=session.get('user')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select id from user where email=%s', [user])
        count = cursor.fetchone()[0]
        cursor.execute('select owner_id,agent_id from property where id=%s',[itemid])
        var1=cursor.fetchone()
        print(var1)
        cursor.execute('insert into sale(property_id,sale_price,buyer_id,seller_id,agent_id) values(%s,%s,%s,%s,%s)',[itemid,total,count,var1[0],var1[1]])
        
        cursor.execute('update property set status="sold" where id=%s',[itemid])
        mydb.commit()
        cursor.close()
        return redirect(url_for('orders'))
    return redirect(url_for('login'))
@app.route('/orders')
def orders():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(id) from user where email=%s', [session.get('user')])
        count = cursor.fetchone()[0]
        cursor.execute('''SELECT
    s.id AS sale_id,
    s.sale_price,
    s.sale_date,
    p.title AS property_title,
    p.location AS property_location,
    u.username AS buyer_username
    
FROM
    sale s
JOIN
    property p ON s.property_id = p.id
JOIN
    user u ON s.buyer_id = u.id where 
 buyer_id=uuid_to_bin(%s)''',[count])
        count=cursor.fetchall()
        cursor.close()
        return render_template('orders.html',orders=count)
    return render_template('login')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        location = request.form.get('location')
        property_type = request.form.get('property_type')
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')
        size = request.form.get('size')

        # Construct the query
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM property WHERE 1=1"

        if location:
            query += f" AND location LIKE '%{location}%'"

        if property_type:
            query += f" AND property_type = '{property_type}'"

        if min_price:
            query += f" AND price >= {float(min_price)}"

        if max_price:
            query += f" AND price <= {float(max_price)}"

        if size:
            query += f" AND size = '{size}'"

        # Execute the query
        cursor.execute(query)
        search_results = cursor.fetchall()

        cursor.close()
        print(search_results)
        return render_template('search_results.html', results=search_results)

    return render_template('search_form.html')
@app.route('/billdetails/<ordid>.pdf')
def invoice(ordid):
    cursor = mydb.cursor(buffered=True)

    # Fetch sale details
    cursor.execute('SELECT * FROM sale WHERE id = %s', [ordid])
    order = cursor.fetchone()
    if not order:
        return "Order not found", 404

    sale_id = order[0]
    property_id = order[1]
    seller_id = order[2]
    agent_id = order[3]
    buyer_id = order[4]
    sale_price = order[5]
    sale_date = order[6]

    # Fetch buyer details
    cursor.execute('SELECT username, phone_no, address, email FROM user WHERE id = %s', [buyer_id])
    buyer = cursor.fetchone()
    if not buyer:
        return "Buyer not found", 404

    uname = buyer[0]
    uphnumber = buyer[1]
    uaddress = buyer[2]
    uemail = buyer[3]

    # Fetch property details
    cursor.execute('SELECT title, description, price, bedrooms, bathrooms, location FROM property WHERE id = %s', [property_id])
    property = cursor.fetchone()
    if not property:
        return "Property not found", 404

    property_title = property[0]
    property_description = property[1]
    property_price = property[2]
    property_bedrooms = property[3]
    property_bathrooms = property[4]
    property_location = property[5]

    # Fetch seller details
    cursor.execute('SELECT username, phone_no, address, email FROM user WHERE id = %s', [seller_id])
    seller = cursor.fetchone()
    if not seller:
        return "Seller not found", 404

    sname = seller[0]
    sphnumber = seller[1]
    saddress = seller[2]
    semail = seller[3]

    # Render the HTML template with fetched data
    html = render_template(
        'bill.html', 
        uname=uname, uaddress=uaddress, uphnumber=uphnumber, uemail=uemail,
        property_title=property_title, property_description=property_description, 
        property_price=property_price, property_bedrooms=property_bedrooms, 
        property_bathrooms=property_bathrooms, property_location=property_location,
        sale_price=sale_price, sale_date=sale_date,
        sname=sname, sphnumber=sphnumber, saddress=saddress, semail=semail
    )

    # Generate PDF from HTML
    pdf = pdfkit.from_string(html, False, configuration=config)
    response = Response(pdf, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response


app.run(debug=True)