import re, requests, json, urllib2, wikipedia, praw
from nytimesarticle import articleAPI
from bs4 import BeautifulSoup
from cookielib import CookieJar
from flask import Flask, jsonify, render_template, url_for
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans

app = Flask(__name__, static_folder='static', static_url_path='/static')
NYTimes_API_KEY = 'ca470e1e91b15a82cc0d4350b08a3c0b:14:70189328'

def cluster_articles(reference_article, articles):
	v = DictVectorizer(sparse=False)
	dataset = []
	related_articles_inds = []
	reference_keys = reference_article["keywords"]
	num_reference_keys = len(reference_keys)
	ref_keywords = {}

	for key in reference_keys:
		ref_keywords[key["value"]] = 1
    dataset.append(ref_keywords)

	for article in articles:
		keywords = {}
		keys = article["keywords"]
		for key in keys:
			keywords[key["value"]] = 1
            
		dataset.append(keywords)
        
	vectorized = v.fit_transform(dataset)  
    # trim irrelevant data points: vectorize w.r.t. reference article keywords, vs all keywords.
	trimmed_vectorized = []
	for i in xrange(0, len(vectorized)):
		trimmed_vectorized.append(vectorized[i][-num_reference_keys:])
        
	num_clusters = 1 + len(articles)
	km = KMeans(n_clusters = num_clusters, init='random', n_init=1, verbose=1)
	km.fit(trimmed_vectorized)
	reference_label = km.labels_[0]
	print km.labels_

	for i in xrange(1, len(km.labels_)):
		if (reference_label == km.labels_[i]):
			related_articles_inds.append(i)

	related_articles_urls = []
	for i in xrange(0, len(related_articles_inds)):
		index = related_articles_inds[i] - 1
		related_articles_urls.append(articles[index]["web_url"])

	return related_articles_urls

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

print cluster_articles(getArticle('http://www.nytimes.com/2014/11/14/world/middleeast/abu-bakr-baghdadi-islamic-state-leader-calls-for-new-fight-against-west.html'), [getArticle('http://www.nytimes.com/2014/11/15/sports/not-all-leagues-ready-to-go-all-in-on-legalized-gambling.html'), getArticle('http://www.nytimes.com/2014/11/15/business/some-retailers-are-promoting-their-decision-to-remain-closed-on-thanksgiving.html?hp&action=click&pgtype=Homepage&module=photo-spot-region&region=top-news&WT.nav=top-news'), getArticle('http://www.nytimes.com/2014/11/14/world/middleeast/abu-bakr-baghdadi-islamic-state-leader-calls-for-new-fight-against-west.html')])

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