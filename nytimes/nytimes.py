import re, requests, json, urllib2, wikipedia
from nytimesarticle import articleAPI
from bs4 import BeautifulSoup
from cookielib import CookieJar
from flask import Flask, jsonify, render_template, url_for

app = Flask(__name__, static_folder='static', static_url_path='/static')
NYTimes_API_KEY = 'ca470e1e91b15a82cc0d4350b08a3c0b:14:70189328'

def getArticle(url):
	# Beautiful Soup scraping for Article
	s = requests.Session()
	mainPage = s.get(url)
	mainPagesoup = BeautifulSoup(mainPage.text)
	title = mainPagesoup.find("h1")
	p = mainPagesoup.find_all("p")
	img = mainPagesoup.find_all("img")

	# Use API to get keywords, etc.
	api = articleAPI(NYTimes_API_KEY)
	articles = api.search(q = ("\"" + title.getText() + "\""), hl = True)
	currentArticle = articles['response']['docs'][0]

	# Article text Engine
	allText = ''
	for eachSelection in p:
		allText += (eachSelection.getText() + '<br><br>')
	allImages = []
	for eachImage in img:
		allImages.append(eachImage['src'])
	currentArticle['allText'] = allText
	currentArticle['img'] = allImages

	# Definition Engine
	for eachKeyword in range(0, len(currentArticle['keywords'])):
		currentWord = currentArticle['keywords'][eachKeyword]['value']
		currentDefinition = wikipedia.summary(currentWord, sentences=1)
		currentArticle['keywords'][eachKeyword]['definition'] = currentDefinition

	return currentArticle

# Primary route
@app.route("/")
def primaryURL():
	return "Enter a URL"

# API route
@app.route("/api/<path:url>")
def apiRoute(url):
	return jsonify(getArticle(url))

# Default user route
@app.route("/<path:url>")
def urlRoute(url):
	return render_template('home.html', article=getArticle(url))

if __name__ == "__main__":
	app.run()