from flask import Flask, render_template, request, flash, url_for, redirect, session
from sqlalchemy import or_
from models import db, User, Parking_Lot, Spot_status, Parking_Spot, Reserve_Parking_Spot
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from matplotlib import pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key"                      #password
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///parking.db'    #path of database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False              #hides any errors thrown when changes made 

#connecting db with flask application 
db.init_app(app)

@app.route("/")
def homepage():
    return render_template('homepage.html')

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():  #check if user is admin
        admin = User(username='admin',full_name='Administrator', 
                     phone_number = 9827467382, email='admin@gmail.com',
                     password=generate_password_hash('admin123'),role='admin') #predefine admin details
        db.session.add(admin)
        db.session.commit()

@app.route("/admin_login", methods=['POST', 'GET'])
def admin_login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']    #username or email
        password = request.form['password']
        admin = User.query.filter(or_(User.username==unique_id, User.email==unique_id), User.role=='admin').first()

        if admin and check_password_hash(admin.password, password):
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        phone_number = int(request.form['phone_number'])
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')

        new_user = User(username=username, full_name=full_name, phone_number=phone_number, email=email, password=generate_password_hash(password), role=role)
            
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('register.html')


@app.route("/user_login", methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        password = request.form['password']

        user = User.query.filter(or_(User.email==unique_id, User.username==unique_id), User.role=='user').first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect('../user_dashboard')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('user_login.html')

@app.route("/admin_dashboard")
def admin_dashboard():
    lots = Parking_Lot.query.all()
    return render_template("admin_dashboard.html", lots=lots, Spot_status=Spot_status)

@app.route("/create_lot", methods =['GET', 'POST'])
def create_lot():
    if request.method=="POST":
        city=request.form['city']
        location=request.form['location']
        base_price=float(request.form['base_price'])
        price=float(request.form['price'])
        max_spots=int(request.form['max_spots'])

        new_lot = Parking_Lot(city=city, location=location, base_price=base_price, price=price, max_spots=max_spots)

        db.session.add(new_lot)
        db.session.commit()

        for i in range(1, max_spots+1):
            new_spot = Parking_Spot(lot_id=new_lot.lot_id, spot_no=i, status=Spot_status.vacant)
            db.session.add(new_spot)

        db.session.commit() 

        flash('Parking Lot creation successful! View parking lots', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template("create_lot.html")

@app.route("/edit_del_lot", methods=['GET', 'POST'])
def edit_del_lot():
    lots = Parking_Lot.query.all()
    cities = sorted(set(lot.city for lot in lots))
    if request.method=="POST":
        city=request.form['city']
        location=request.form['location']
        action=request.form.get('action')

        if city and location:
            selected_lot = Parking_Lot.query.filter_by(city=city, location=location).first()

        if action=='edit':
            return redirect(url_for("edit_lot", lot_id=selected_lot.lot_id))
        elif action=='delete':
            return redirect(url_for("del_lot", lot_id=selected_lot.lot_id))
        
    return render_template("edit_del_lot.html", lots=lots, cities=cities)

@app.route("/registered_users")
def registered_users():
    users = User.query.all()
    return render_template("registered_users.html", users=users)

@app.route("/admin_parking_history")
def admin_parking_history():
    reserved_spots = Reserve_Parking_Spot.query.order_by(Reserve_Parking_Spot.parking_time.desc()).all() 
    return render_template("admin_parking_history.html", reserved_spots=reserved_spots)


@app.route("/user_dashboard")
def user_dashboard():
    username = session.get('username', 'user')
    user_id = session.get('user_id')
    
    lots = Parking_Lot.query.all()

    active_reserved_spot = Reserve_Parking_Spot.query.filter_by(user_id=user_id, is_active=True).first()
    reserved_spot_id = active_reserved_spot.spot_id if active_reserved_spot else None
    is_active = True if active_reserved_spot else False 

    return render_template("user_dashboard.html", username=username, lots=lots,
                           Spot_status=Spot_status, spot_id=reserved_spot_id, is_active=is_active)

@app.route("/select_lot", methods=["GET", "POST"])
def select_lot():
    lots = Parking_Lot.query.all()
    cities = sorted(set(lot.city for lot in lots))

    if request.method == "POST":
        city = request.form.get('city')
        location = request.form.get('location')
        

        if city and location:
            selected_lot = Parking_Lot.query.filter_by(city=city, location=location).first()
            lot_id=selected_lot.lot_id
            lot = Parking_Lot.query.get(lot_id)

            if selected_lot:
                return render_template("book_spot.html", lot_id=lot_id, lot=lot, Spot_status=Spot_status)
    return render_template("select_lot.html", lots=lots, cities=cities)

@app.route("/book_spot/<int:lot_id>", methods=["GET", "POST"])
def book_spot(lot_id):
    lot=Parking_Lot.query.get(lot_id)
    vacant_spot = next((spot for spot in lot.spot if spot.status == Spot_status.vacant), None)

    if request.method == "POST":
        if not vacant_spot:
            flash("No vacant spot available to book.", "danger")
            return redirect(url_for("book_spot", lot_id=lot_id))

        vacant_spot.status = Spot_status.occupied
        reserved_spot = Reserve_Parking_Spot(
            user_id=session.get("user_id"),
            lot_id=lot_id,
            spot_id=vacant_spot.spot_id,
            status=Spot_status.occupied,
            parking_time=datetime.now(),
            cost=lot.base_price,
            is_active=True
        )
        db.session.add(reserved_spot)
        db.session.commit()
        flash(f"Spot {vacant_spot.spot_no} booked successfully!", "success")
        return redirect(url_for("user_dashboard"))

    return render_template("book_spot.html", lot=lot, Spot_status=Spot_status)

@app.route("/release_spot/<int:spot_id>", methods=["GET", "POST"])
def release_spot(spot_id):
    user_id = session.get("user_id")
    reserved_spot = Reserve_Parking_Spot.query.filter_by(spot_id=spot_id, user_id=user_id, is_active=True).order_by(Reserve_Parking_Spot.parking_time.desc()).first()
    spot = Parking_Spot.query.get(spot_id)
    lot_id = spot.lot_id
    lot = Parking_Lot.query.get(lot_id)
    price = lot.price
    parking_time = reserved_spot.parking_time

    if request.method == "POST" and reserved_spot and spot:
        reserved_spot.leaving_time=datetime.now()
        reserved_spot.is_active=False
        reserved_spot.status = Spot_status.vacant
        
        spot.status = Spot_status.vacant

        leaving_time = reserved_spot.leaving_time

        time_spent = leaving_time-parking_time
        hours = time_spent.total_seconds()/3600
        reserved_spot.duration = int(hours)

        print("Duration to store:", reserved_spot.duration, type(reserved_spot.duration))
        
        db.session.commit()

        print(reserved_spot.duration)

        if reserved_spot.duration>2:
            cost=reserved_spot.cost + ((reserved_spot.duration-2)*price)
            flash(f"Spot {spot.spot_no} released successfully!", "success")
            return redirect(url_for('cost_calc', cost=cost ))
        else:
            cost=reserved_spot.cost
            flash(f"Spot {spot.spot_no} released successfully!", "success")
            return redirect(url_for('cost_calc', cost=cost))
    return render_template("release_spot.html", spot_id=spot_id, spot = spot)

@app.route('/cost_calc/<float:cost>', methods=["GET", "POST"])
def cost_calc(cost):
    
    if request.method=="POST":
        return redirect(url_for('user_dashboard'))
    return render_template("cost_calc.html", cost=cost)

@app.route("/user_parking_history")
def user_parking_history():
    user_id = session.get("user_id")
    reserved_spots = Reserve_Parking_Spot.query.filter_by(user_id=user_id).order_by(Reserve_Parking_Spot.parking_time.desc()).all() 
    return render_template("user_parking_history.html", reserved_spots=reserved_spots)

@app.route("/edit_lot/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    lot = Parking_Lot.query.get(lot_id)
    if request.method == "POST":
        lot.base_price = float(request.form["base_price"])
        lot.price = float(request.form["price"])
    
        spots_to_delete = [spot for spot in lot.spot if spot.spot_no > lot.max_spots]
            
        # Check if all are vacant
        if any(spot.status != Spot_status.vacant for spot in spots_to_delete):
            flash("Cannot reduce max spots. Some spots beyond the new limit are not vacant.", "danger")
            return redirect(url_for("edit_lot", lot_id=lot_id))

        # Safe to delete
        for spot in spots_to_delete:
            db.session.delete(spot)

        db.session.commit()
        
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("edit_lot.html", lot=lot, Spot_status=Spot_status)

@app.route("/del_lot/<int:lot_id>", methods=["GET", "POST"])
def del_lot(lot_id):
    lot = Parking_Lot.query.get(lot_id)
    if request.method=="POST":
        spots = [spot for spot in lot.spot]

        # Check if all are vacant
        if any(spot.status != Spot_status.vacant for spot in spots):
            flash("Cannot reduce max spots. Some spots beyond the new limit are not vacant.", "danger")
            return redirect(url_for("del_lot", lot_id=lot_id))
        
        for spot in spots:
            db.session.delete(spot)

        db.session.delete(lot)

        db.session.commit()
        flash("Parking lot deleted successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("del_lot.html", lot_id=lot_id, lot=lot, Spot_status=Spot_status)

@app.route("/log_out", methods=["GET", "POST"])
def log_out():
    if request.method=="POST":
        return redirect(url_for( "homepage" ))
    return render_template("log_out.html")

@app.route('/admin_summary_charts')
def admin_summary_charts():
    users = User.query.all()
    usernames = [user.username for user in users if user.username!="admin"]

    spots_per_user = [ Reserve_Parking_Spot.query.filter_by(user_id=user.user_id).count()
    for user in users if user.username != "admin" ]
    fig1, ax1 = plt.subplots()
    ax1.bar(usernames, spots_per_user, color='navy')
    ax1.set_title('Number of Spots Occupied per User')
    ax1.set_xlabel('Usernames')
    ax1.set_ylabel('Spots')
    max_spots_per_user = max(spots_per_user) if spots_per_user else 0
    yticks = np.arange(0, max_spots_per_user+2, 2)  
    ax1.set_yticks(yticks)
    img1 = io.BytesIO()
    fig1.tight_layout()
    fig1.savefig(img1, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()

    lots = Parking_Lot.query.all()
    locations = []
    spots_per_lot = []

    for lot in lots:
        locations.append(lot.location)
        count = Reserve_Parking_Spot.query.filter_by(lot_id=lot.lot_id).count()
        spots_per_lot.append(count)

    fig2, ax2 = plt.subplots()
    ax2.bar(locations, spots_per_lot, color='navy')
    ax2.set_title('Spots Occupied per Lot')
    ax2.set_xlabel('Location')
    ax2.set_ylabel('Spots')
    max_spots_per_lot = max(spots_per_lot) if spots_per_lot else 0
    yticks = np.arange(0, max_spots_per_lot+2, 2)  
    ax2.set_yticks(yticks)
    img2 = io.BytesIO()
    fig2.tight_layout()
    fig2.savefig(img2, format='png')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    return render_template('admin_summary_charts.html', plot_url1=plot_url1, plot_url2=plot_url2)

@app.route('/user_summary_charts')
def user_summary_charts():
    user_id = session.get('user_id')
    lots = Parking_Lot.query.all()

    locations = []
    spots_per_lot = []

    for lot in lots:
        locations.append(lot.location)
        count = Reserve_Parking_Spot.query.filter_by(lot_id=lot.lot_id, user_id = user_id).count()
        spots_per_lot.append(count)

    fig3, ax3 = plt.subplots()
    ax3.bar(locations, spots_per_lot, color='navy')
    ax3.set_title('Spots Occupied per Lot')
    ax3.set_xlabel('Location')
    ax3.set_ylabel('Spots')
    max_spots_per_lot = max(spots_per_lot) if spots_per_lot else 0
    yticks = np.arange(0, max_spots_per_lot+2, 2)  
    ax3.set_yticks(yticks)
    img3 = io.BytesIO()
    fig3.tight_layout()
    fig3.savefig(img3, format='png')
    img3.seek(0)
    plot_url3 = base64.b64encode(img3.getvalue()).decode()
    return render_template('user_summary_charts.html', plot_url3=plot_url3)

if __name__ == '__main__':
    app.run(debug=True)