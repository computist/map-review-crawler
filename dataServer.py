from __future__ import print_function
from flask import Flask, request
from celery import Celery
from OpenSSL import SSL
import time
import sqlite3
import sys
import re
from selenium import webdriver

SUMMARY_CLASS = ".ml-panes-entity-summary-information"
REVIEW_CLASS = ".ml-reviews-page-user-review-text"
REVIEW_BUTTON_CLASS = ".ml-panes-entity-link"
REVIEW_COUNT_CLASS = ".ml-reviews-page-title-bar-text"
REVIEW_PANEL_CLASS = ".ml-reviews-page-white-background"

# connect to db
conn = sqlite3.connect("restaurant.db")
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurant';")
if c.fetchone() is None:
    # create table if not exist
    c.execute("CREATE TABLE restaurant (cid varchar primary key, name varchar, summary varchar)")
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review';")
if c.fetchone() is None:
    # create table if not exist
    c.execute("CREATE TABLE review (cid varchar, review varchar)")
conn.commit()

# set up task queue
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route("/")
def main():
    cids = request.args.get("cids")
    if cids is None:
        cids = ""
    for cid in cids.split(","):
        scrape.apply_async(args=[cid])
    return cids

@celery.task
def scrape(cid):
    try:
        print(cid)
        url = "https://maps.google.com/?cid=" + cid
        driver = webdriver.PhantomJS()
        driver.get(url)
        html = driver.page_source
        arr = html.split("search?q=")
        if len(arr) > 1:
            seg = arr[1]
            name = seg[:seg.index(",")] # name not found then raise exception and skip
            arr = driver.find_elements_by_css_selector(SUMMARY_CLASS)
            if len(arr) > 0:
                summary = arr[0].get_attribute('innerHTML')
                driver.find_element_by_css_selector(REVIEW_BUTTON_CLASS).click()
                time.sleep(3)
                numReview = int(driver.find_element_by_css_selector(REVIEW_COUNT_CLASS).get_attribute('innerHTML').split(" ")[0])

                c.execute("INSERT INTO restaurant(cid,name,summary) VALUES(?, ?, ?)", (cid, name, summary)) 
                # throw exception and skip if not unique
                conn.commit()
                
                while True:
                    driver.execute_script("e = document.querySelector(' " + REVIEW_PANEL_CLASS + "'); e.scrollTop = e.scrollHeight;")
                    time.sleep(0.5)
                    reviews = driver.find_elements_by_css_selector(REVIEW_CLASS)
                    if len(reviews)/2 >= numReview: # duplicate twice
                        break;
                
                if len(reviews) > 0:
                    for i in range(0, len(reviews), 2):
                        c.execute("INSERT INTO review(cid,review) VALUES(?, ?)", (cid, reviews[i].get_attribute('innerHTML')))
                    conn.commit()
                    print("Stored %d reviews for %s." % (len(reviews)/2, name))
    except Exception as e:
        print(e)
    finally:
        driver.close()
    
if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    app.run(host='127.0.0.1',port='5000', ssl_context=context)