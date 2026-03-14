# Vehicle Parking App

A web-based **Vehicle Parking Management System** built using **Flask, SQLite, HTML, CSS, and Jinja2**.
The application allows an **Admin** to manage parking lots and **Users** to reserve and release parking spots efficiently.

---

# Description

The **Vehicle Parking App** consists of **one admin and multiple users**.

### Admin Capabilities

* Create parking lots with multiple parking spots
* Edit parking lot pricing
* Delete parking lots (only if none of the spots are occupied)
* View parking history of all users
* View analytics charts summarizing parking usage

### User Capabilities

* Register and log in to the system
* Book a parking spot in any available parking lot
* Release a booked parking spot
* View parking history
* View summary charts of their parking activity

This application provides a **simple and efficient system for managing parking spaces and bookings**.

---

# Technologies Used

## Backend

**Flask** – Python web framework used to build the backend.

### Flask Libraries Used

* **Flask** – Handles HTTP requests
* **render_template** – Renders HTML pages using Jinja2
* **request** – Handles form data (GET/POST)
* **flash** – Displays alert messages
* **url_for** – Dynamically generates URLs
* **redirect** – Redirects users between routes
* **session** – Maintains session data

### Extension Used

**Flask-SQLAlchemy**

* ORM used to interact with the SQLite database.

---

## Frontend

* **HTML** – Structure of web pages
* **CSS** – Styling of the application
* **Jinja2** – Template engine used for dynamic HTML rendering

---

## Database

**SQLite**

* Lightweight relational database
* Stores application data in structured tables

---

# Database Schema Design

The database contains four main tables:

| Table                 | Primary Key | Description                                |
| --------------------- | ----------- | ------------------------------------------ |
| users                 | user_id     | Stores user information                    |
| parking_lots          | lot_id      | Stores parking lot details                 |
| parking_spots         | spot_id     | Stores individual parking spot information |
| reserve_parking_spots | reserve_id  | Stores parking reservation details         |

### Relationships

* **lot_id** → Foreign key in `parking_spots`
* **user_id, lot_id, spot_id** → Foreign keys in `reserve_parking_spots`

This relational schema maintains proper **mapping between users, parking lots, and reservations**.

---

# API Design

| Endpoint                      | Purpose                           |
| ----------------------------- | --------------------------------- |
| `/register`                   | Register a new user               |
| `/user_login`                 | Login for users                   |
| `/admin_login`                | Login for admin                   |
| `/create_lot`                 | Create a parking lot              |
| `/edit_lot`                   | Edit parking lot details          |
| `/del_lot`                    | Delete a parking lot              |
| `/book_spot/<int:lot_id>`     | Book a parking spot               |
| `/release_spot/<int:spot_id>` | Release a parking spot            |
| `/user_parking_history`       | View user's parking history       |
| `/admin_parking_history`      | View parking history of all users |
| `/admin_summary_charts`       | View summary charts for admin     |
| `/user_summary_charts`        | View summary charts for users     |

---

# Project Architecture

The project is organized inside the **MAD1** folder.

```
MAD1
│
├── templates/
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── login.html
│   ├── register.html
│   └── other HTML templates
│
├── static/
│   └── style.css
│
├── instance/
│   └── parking.db
│
├── app.py
│
├── models.db
│
├── __pycache__/
│
└── myenv/
```

### Folder Description

**templates/**

* Contains all HTML pages used in the application.

**static/**

* Contains CSS and other static assets.
* `style.css` is used for styling the webpages.

**instance/**

* Stores the SQLite database `parking.db`.

**app.py**

* Main Flask backend application file containing all routes and logic.

**models.db**

* Defines the database schema and models.

****pycache****

* Automatically stores compiled Python files.

**myenv**

* Contains dependencies for the Python virtual environment.

---


# 🎥 Project Demo

Demo Video:
https://drive.google.com/file/d/1VOXgykbMlDKVLGOCNrryYAZ0PBlhnuGV/view?usp=sharing
