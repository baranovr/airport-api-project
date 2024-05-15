# Airport API Project

This project was created to implement an airport management system.
The project was made using **Django REST Framework** and **Docker**.

The project presents eight models:
- `Crew`
- `Route`
- `Airplane`
- `AirplaneType`
- `Flight`
- `Airport`
- `Ticket`
- `Order`

Basically, models are connected using a `ForeignKey`, only the `Crew` and `Flight` model have a `ManyToMany` relationship.
It is important to note that the `Order` model has a user field, which is **built-in Django** model.
A separate app (`user/`) has been implemented for the user.

**Here you can you see the database structure:**

![db structure](https://media.mate.academy/airport_diagram_ce181e403f.png)

<br>
<h2>✈️ Airport API Project</h2>

To get started with the project you need to do the following👇:

> Clone the repository
```bash
$ git clone https://github.com/baranovr/airport-api-project.git
```

<br />

> Install modules via `VENV`  
### 👉 Set Up for `Unix`, `MacOS`
```bash
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

### 👉 Set Up for `Windows`
```bash
$ virtualenv env
$ souce venv\Scripts\activate
$ pip install -r requirements.txt
```

<br />

> Set your environment variables
```bash
$ set DB_HOST=<your DB hostname>
$ set DB_NAME=<your DB name>
$ set DB_USER=<your DB username>
$ set DB_PASSWORD=<your DB user passoword>
$ set SECRET_KEY=<your secret key>
```

<br />

> Set Up Database

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

<br>

## 📑 Project general features 
📍JWT authenticated

📍Admin panel /admin/

📍Documentation is located at /api/doc/swagger/

📍Managing orders and tickets

📍Counting free and occupied seats

📍Creating airplanes

📍Adding flights

📍Filtering crews and flights

<br>

<hr>

<h2>🐋 Airport API Project and Docker</h2>
For convenient development and transfer of the project to other users, Docker was introduced here.
The image has been uploaded to Docker Hub:

> Link: https://hub.docker.com/repository/docker/baranovr/airport_api_project-airport/general

How to use (Docker should be installed)👇:

```bash
docker-compose build
docker-compose up
```

<hr>

## 👤 Create Super User

By default, the application redirects guest users for authentication. 
To access private pages, you will need to create a `superuser`, this can be done by running the special command and follow further instructions:

```bash
$ python manage.py createsuperuser
```

<br />
<hr>

## To get a viewing token, go to the following endpoints👇:

### 📋 Registration:

> .../api/user/register/

### 🎫 Get token:

> .../api/user/token/

 ### ✅ Verify token:

> .../api/user/token/verify/

### 🔄 Refresh token:

> .../api/user/token/refresh/

<br>
<hr>


## 📂 Code-base structure
```angular2html
< PROJECT ROOT >
   |
   |-- airport/  
   |    |-- management/
   |    |    |-- commands/
   |    |        |-- wait_for_db.py
   |    |
   |    |-- tests/
   |    |    |-- test_airport_api.py        # All test files
   |    |
   |    |-- admin.py                        # Registration models in admin page 
   |    |-- apps.py
   |    |-- models.py                       # All airport models
   |    |-- permissions.py                  # File to implement general variable
   |    |-- serializers.py                  # All project models
   |    |
   |    |-- urls.py                         # Paths for pages
   |    |-- views.py                        # All project views
   |
   |-- airport_api_project/
   |    |-- asgi.py
   |    |-- settings.py                     # Defines Global Settings
   |    |-- urls.py
   |    |-- wsgi.py
   |    
   |-- media/                               # Folder for media
   |    |-- uploads/                        
   |        |-- airplanes/                  
   |
   |-- user/                                
   |    |-- admin.py                        # Registration user in admin page
   |    |-- apps.py                         
   |    |-- models.py                       # Folder with user model
   |    |-- serializers.py                  # User serializers
   |    |-- urls.py                         # Urls to get/verify/refresh token
   |    |-- views.py                        # User view
   |
   |-- .gitignore                           # File with ignored file types to git
   |-- docker-compose.yaml                  # Docker images managing file
   |-- Dockerfile                           # Docker implementation file
   |-- .env                                 # Inject Configuration via Environment
   |-- manage.py                            # Start the app - Django default start script
   |-- requirements.txt                     # Development modules
   |
   |-- ************************************************************************
```