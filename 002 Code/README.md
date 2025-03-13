# Source Code
# 주의사항
- ### 다른 Open Source SW를 사용하는 경우 저작권을 명시해야 함
- ### 인턴쉽의 경우 해당 기업의 기밀이 담김 데이터는 제외할 것
  #### ※ 기업 기밀 데이터가 Github에 공개되었을 시의 책임은 공개한 학생에게 있음 

# UCSI_Subject_Team1

## 🚀 Project Execution Result  

![Project Execution Result](https://github.com/user-attachments/assets/6384ef0f-aad1-488f-b7fd-c60d31204f9f)

# 🚀🚀Super Easy Server Setup Guide !!

If you're using Windows, it's recommended to use Git Bash.  

### 📂 0. Set the Folder Location to "back"  
Use the `cd` command to navigate to the `back` folder.

### 💻 1. Create a Virtual Environment  
Run the following command in `cmd` to create a virtual environment:  
```sh
python -m venv venv
```

### ▶️ 2. Activate the Virtual Environment
Mac/Linux
``` sh
source venv/bin/activate
```
window
``` cmd
venv\Scripts\activate
```
Run the appropriate command in `cmd` to activate the virtual environment.

### 📦 3. Install Required Packages
```
pip install -r requirements.txt
```

### 🐋 4. Run Docker
First, ensure Docker is running. Then, execute the following command in `cmd`:
```
docker-compose up -d
```
This will use the `docker-compose.yml` file to automatically configure Docker and create a PostgreSQL database.

### 📁 5. Place the .env File
Place the shared `.env` file inside the `back` folder.
The `.env` file contains sensitive information that should not be uploaded to Git.

### 🚀 6. Start the Server
Run the following commands to start the server:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
This setup process only needs to be done once after cloning the Git repository.


after next run server... 🤔

### etc. 🔄 After Initial Setup: Running the Server
Once the initial setup is complete, you can start the server using:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Note: Make sure Docker is running before starting the server.

### etc2. 🛠️ Accessing the Database Inside Docker
To run DML commands (`SELECT`, `UPDATE`, `DELETE`, `INSERT`, etc.) inside the Dockerized database, use:
```
docker exec -it back-db-1 psql -U postgres -d project_db
```
And that's it! Your server should be up and running! 🚀




