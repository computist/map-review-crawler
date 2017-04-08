# Google Map Review Crawler

## Steps to install and run

### 1. install dependency
pip install Flask
pip install -U "celery[redis]"
sudo apt-get install redis-server
sudo apt-get install nodejs-legacy
sudo apt install npm
sudo npm -g install phantomjs-prebuilt
sudo pip install -U selenium

### 2. create and install self-signed certificate
cert.pem
key.pem
use the name above for your certificate and put it in the same folder

### 3. run data server
python dataServer.py

### 4. run redis
redis-server

### 5. run background data processing job
celery worker -A dataServer.celery --loglevel=info --concurrency=1
suggest to use lower concurrency to avoid blocking by google
sqlite has limited support for concurrency, if concurrency > 1, db file may corrupt in the middle.
use other db to increase concurrency

### 6. open browser (chrome or firefox), goto google map (full mode, not lite mode)
run code listen.js in browserconsole
after you copy paste the js and run in console, you can close the console.

### 7. search restaurant, it will auto store data
move map around, the map will auto search the new area and the script will capture new results