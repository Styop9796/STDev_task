### ** Clone the Repository**
```sh
git clone https://github.com/your-username/cinema-booking-app.git
cd cinema-booking-app
```

### **Create virtual enviroment**
```sh
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
```

### **Install dependencies**
Note: I'm using lates version of Django , use older version if you have old python version  
```sh
pip install -r requirements.txt
```

### **Setup Enviroment Variables**
Note: Please have your PostgreSQL database ready with database name and credentials.

Copy .env.example file as .env and fill with credentials.


### **Database Migrations**
```sh

python manage.py makemigrations
python manage.py migrate
```

### **Optional: Backup data from backup.sql file **
I have prepared database to make it easy for you to test

```sh
python manage.py loaddata backup.sql
```

### **Create a Superuser (For Admin Access)**
Admin panel is available at /admin URL.Follow instructions after createsuperuser command

```sh
python manage.py createsuperuser

```

### **Running the Server**
```sh
python manage.py runserver
```

