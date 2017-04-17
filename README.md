# Google Map Review Crawler

## Steps to install and run

### 1. install dependency
```
pip install Flask
pip install -U "celery[redis]"
sudo apt-get install redis-server
sudo apt-get install nodejs-legacy
sudo apt install npm
sudo npm -g install phantomjs-prebuilt
sudo pip install -U selenium
```

### 2. create and install self-signed certificate
cert.pem
key.pem
Use the filename above for your certificate and put it in the same folder.

### 3. run data server
```
python dataServer.py
```

### 4. run redis
```
redis-server
```

### 5. run background data processing job
```
celery worker -A dataServer.celery --loglevel=info --concurrency=1
```
Suggest to use lower concurrency value to avoid blocking by google.
Sqlite has limited support for concurrency. 
If concurrency > 1, db file may corrupt in the middle.
If you want higher concurrency, use other db instead.

### 6. open browser (chrome or firefox), goto https://localhost:5000/
It will prompt you that the page is not safe. 
Click on continue to page without warning. The browser will not warn you again for the current session.

### 7. goto google map (full mode, not lite mode)
Run code listen.js in browser console.
After you copy paste the js and hit ENTER, you can close the console.
The script will monitor event in the background.

### 8. search restaurant, it will auto store data
Move the map around, and the map will auto search the new area and the script will capture new results.