VisionStock
Smart warehouse inventory monitoring with computer vision
VisionStock watches warehouse shelves through a camera or a recorded video, detects and counts the products it sees, saves the counts in a database and shows them on a live web dashboard. When a product falls below its minimum stock, it records a low-stock event and alerts every open dashboard.



Tech stack
Area	Technology
Language	Python, JavaScript, SQL
Computer vision	OpenCV, YOLO (Ultralytics), ByteTrack
Backend	FastAPI, SQLAlchemy, Pydantic, JWT (PyJWT), bcrypt
Database	MySQL or SQLite
Real time	WebSocket, optional Apache Kafka
Frontend	HTML, CSS, Bootstrap 5, JavaScript, Chart.js
Tools	Git, GitHub


How it works
Camera / video
    -> OpenCV reads and resizes a frame           (vision/camera.py)
    -> YOLO detects objects, ByteTrack gives IDs  (vision/detection.py)
    -> count unique IDs inside each shelf region  (vision/counting.py, shelf_monitor.py)
    -> every few seconds: save quantities, create events
                                                   (services/inventory_service.py)
    -> WebSocket message to the open dashboards   (services/websocket_service.py)
    -> dashboard reloads its numbers and shows alerts
The same loop also draws the boxes on each frame and streams the picture to the Live Camera page.

Example: Shelf C has a camera region and the camera sees 5 snack packets. The minimum stock for snack packets is 8. The tracker gives 5 unique IDs, so inventory is saved as 5. That is below 8, so a Low stock event is created and every open dashboard shows an alert.

Getting started
1. Requirements
- Python 3.10 or newer
- MySQL 8, or nothing extra if you use SQLite
- Internet on the first run, because the pages load Bootstrap and Chart.js from a CDN and YOLO downloads its model file
2. Install
git clone https://github.com/YOUR_USERNAME/VisionStock.git
cd VisionStock

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / Mac

pip install -r backend/requirements.txt
Ultralytics installs PyTorch, so this download is large. Everything except the Live Camera page also works without it.
3. Configure the database
Copy .env.example to .env, then pick one option.

SQLite (quickest, nothing to install):
DATABASE_URL=sqlite:///visionstock.db
MySQL:

Create the database and sample data by running database/schema.sql in MySQL Workbench (or mysql -u root -p < database/schema.sql). You can also just create an empty database named visionstock, because the app creates the tables itself.

Put your password in .env:
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/visionstock
If the password has special characters, write them as codes: @ is %40, # is %23, / is %2F, : is %3A.
4. Create the first Admin
python -m backend.create_admin
Enter a name, an email and a password (hidden while you type). If the email already belongs to a Staff user, the command offers to make that user an Admin.
5. Start the server
python -m uvicorn backend.main:app --reload
On Windows you can also double-click start_server.bat.

Open http://127.0.0.1:8000 and log in. The interactive API documentation is at http://127.0.0.1:8000/docs.
6. Try real detection
- Put a video (.mp4) in the videos/ folder, or use the webcam.
- Shelves page: edit a shelf and set its camera region (X, Y, Width, Height as a percent of the picture, for example 0, 0, 100, 100 for the whole frame).
- Products page: set the YOLO class name of a product, which is the label the model gives (for example bottle or person).
- Live Camera page: choose the source and click Start. The first start takes a minute while the model loads.
The model file yolov8n.pt (about 6 MB) is downloaded on the first start. If your network blocks the download, save the file in the project folder yourself.
Accounts and roles
Role	How to get it	Permissions
Staff	Register on the website (register.html)	View, add and edit
Admin	Only with python -m backend.create_admin	Everything, including delete



Database
Five tables (see database/schema.sql):
Table	Purpose
users	Name, email, password hash, role
products	Name, category, minimum stock, YOLO class name
shelves	Name, location, status, occupancy, camera region
inventory	Latest detected quantity of a product on a shelf
detection_events	History of stock updates and low-stock alerts


Future improvements
- Draw shelf regions directly on the video
- Train a custom model for specific products
- Several cameras
- Password reset and login rate limiting
- Barcode and QR code scanning
- Automatic restocking suggestions

