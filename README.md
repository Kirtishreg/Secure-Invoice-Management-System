The Invoice Management System is a Python-based application that leverages state-of-the-art encryption and security protocols to protect sensitive financial data. Key features include:

Secure invoice creation and management
Item addition to invoices
Secure payment processing
Two-factor authentication (2FA) for user login
Real-time alerts for invoice creation and payments
Encrypted data storage
The Secure Invoice Management System was designed using the Model-View-Controller (MVC) architecture, a well-established design pattern that promotes the separation of concerns. This structure allows the system to be modular, easy to maintain, and scalable. The MVC pattern divides the application into three distinct components: Model, View, and Controller.

Model: The Model represents the data layer of the application and is responsible for interacting with the database. In the Secure Invoice Management System, we use SQL Alchemy, an Object-Relational Mapping (ORM) library, to define the database models. These models represent the core entities in the system, including User, Invoice, Business, and Transaction Log. SQL Alchemy allows us to define relationships between models, such as one-to-many relationships between users and invoices, and between businesses and users.
View: The View is responsible for presenting data to the user. In this system, the view is implemented using HTML templates stored in the templates/ directory. These templates are rendered dynamically using the Jinja2 template engine, which is built into Flask. The views display various forms for creating invoices, viewing invoices, and processing payments, among other things.
Controller: The Controller is responsible for handling user input, processing requests, and updating the view accordingly. In this system, the controller is implemented as Flask routes in the app.py and routes.py files. The routes define the business logic of the application, such as handling the creation of invoices, displaying invoice lists, and approving or paying invoices.
Setup the application
set FLASK_APP=app.py

flask db init flask db migrate -m "" flask db upgrade

Run the Application
flask run
