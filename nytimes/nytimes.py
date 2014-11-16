# Standard Lib
import re, requests, json, urllib2, wikipedia, praw, sys, urllib
from itertools import izip

# Firebase
from firebase import firebase

# Imgur
from imgurpython import ImgurClient

imgurClient_id = '09682e2b1a11cd4'
imgurClient_secret = '917548ca300c5536c0a7953d1564683b28356c15'
imgurClient = ImgurClient(imgurClient_id, imgurClient_secret)

# NLTK
import nltk

# Analyze
from analyze import callTweet

# NYTimes, Beautifulsoup, and Cookies
from nytimesarticle import articleAPI
from bs4 import BeautifulSoup
from cookielib import CookieJar

# Flask
from flask import Flask, jsonify, render_template, url_for

# Scikit-learn
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans
reload(sys)
sys.setdefaultencoding("utf-8")

# Bloomberg
import blpapi
sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("10.8.8.1")
sessionOptions.setServerPort(8194)
session = blpapi.Session(sessionOptions)

# Initialization of Flask
app = Flask(__name__, static_folder='static', static_url_path='/static')
NYTimes_API_KEY = 'ca470e1e91b15a82cc0d4350b08a3c0b:14:70189328'

# Initialization of Firebase
firebase = firebase.FirebaseApplication('https://contxt.firebaseio.com/', None)

# StateNameToCodels
stateNameToCode = dict()
stateNameToCode["Alabama"] = "AL"
stateNameToCode["Alaska"] = "AK"
stateNameToCode["Arizona"] = "AZ"
stateNameToCode["Arkansas"] = "AR"
stateNameToCode["California"] = "CA"
stateNameToCode["Colorado"] = "CO"
stateNameToCode["Connecticut"] = "CT"
stateNameToCode["Delaware"] = "DE"
stateNameToCode["District of Columbia"] = "DC"
stateNameToCode["Florida"] = "FL"
stateNameToCode["Georgia"] = "GA"
stateNameToCode["Hawaii"] = "HI"
stateNameToCode["Idaho"] = "ID"
stateNameToCode["Illinois"] = "IL"
stateNameToCode["Indiana"] = "IN"
stateNameToCode["Iowa"] = "IA"
stateNameToCode["Kansas"] = "KS"
stateNameToCode["Kentucky"] = "KY"
stateNameToCode["Louisiana"] = "LA"
stateNameToCode["Maine"] = "ME"
stateNameToCode["Maryland"] = "MD"
stateNameToCode["Massachusetts"] = "MA"
stateNameToCode["Michigan"] = "MI"
stateNameToCode["Minnesota"] = "MN"
stateNameToCode["Mississippi"] = "MS"
stateNameToCode["Missouri"] = "MO"
stateNameToCode["Montana"] = "MT"
stateNameToCode["Nebraska"] = "NE"
stateNameToCode["Nevada"] = "NV"
stateNameToCode["New Hampshire"] = "NH"
stateNameToCode["New Jersey"] = "NJ"
stateNameToCode["NJ"] = "NJ"
stateNameToCode["New Mexico"] = "NM"
stateNameToCode["New York"] = "NY"
stateNameToCode["North Carolina"] = "NC"
stateNameToCode["North Dakota"] = "ND"
stateNameToCode["Ohio"] = "OH"
stateNameToCode["Oklahoma"] = "OK"
stateNameToCode["Oregon"] = "OR"
stateNameToCode["Pennsylvania"] = "PA"
stateNameToCode["Rhode Island"] = "RI"
stateNameToCode["South Carolina"] = "SC"
stateNameToCode["South Dakota"] = "SD"
stateNameToCode["Tennessee"] = "TN"
stateNameToCode["Texas"] = "TX"
stateNameToCode["Utah"] = "UT"
stateNameToCode["Vermont"] = "VT"
stateNameToCode["Virginia"] = "VA"
stateNameToCode["Washington"] = "WA"
stateNameToCode["West Virginia"] = "WV"
stateNameToCode["Wisconsin"] = "WI"
stateNameToCode["Wyoming"] = "WY"

# Clustering algorithm
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

SECURITY_DATA = blpapi.Name("securityData")
SECURITY = blpapi.Name("security")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
ERROR_INFO = blpapi.Name("errorInfo")

def searchImgur(title):
	allStuffs = imgurClient.gallery_search(title, advanced=None, sort='time', window='all', page=0)
	constructURL = []
	for i in allStuffs:
		constructURL.append(i.link)
	return constructURL

def processMessage(msg):
	if not msg.hasElement(SECURITY_DATA):
		print "Unexpected message:"
		print msg
		return

	currentData = []
	securityDataArray = msg.getElement(SECURITY_DATA)
	fieldDataArray = securityDataArray.getElement(FIELD_DATA)
	for i in fieldDataArray.values():
		first = True
		date = ''
		PX_LAST = ''
		for x in i.elements():
			if first == True:
				date = x.getValueAsString()
				first = False
			else:
				PX_LAST = x.getValueAsString()
		currentData.append({"date": date, "score": PX_LAST})
	return currentData

def bloombergSentimentLocation(security1):
    # Start a Session
    if not session.start():
        print "Failed to start session."
        return
    try:
        # Open service to get historical data from
        if not session.openService("//blp/refdata"):
            print "Failed to open //blp/refdata"
            return
        # Obtain previously opened service
        refDataService = session.getService("//blp/refdata")

        # Create and fill the request for the historical data
        request = refDataService.createRequest("HistoricalDataRequest")
        request.getElement("securities").appendValue(security1)
        request.getElement("fields").appendValue("PX_LAST")
        request.getElement("fields").appendValue("OPEN")
        request.set("periodicityAdjustment", "ACTUAL")
        request.set("periodicitySelection", "DAILY")
        request.set("startDate", "20140301")
        request.set("endDate", "20141114")
        request.set("maxDataPoints", 100)

        # Send the request
        cid = session.sendRequest(request)

        allMessages = []
        # Process received events
        while(True):
            # We provide timeout to give the chance for Ctrl+C handling:
            ev = session.nextEvent(500)
            for msg in ev:
            	current_data = processMessage(msg)
            	if current_data is not None:
					allMessages.append(processMessage(msg))
            if ev.eventType() == blpapi.Event.RESPONSE:
                # Response completly received, so we could exit
                return allMessages
    finally:
        # Stop the session
        session.stop()

# AlchemyAPI
def twitterSentimentAnalysis(title):
	result = firebase.get('/twitter', None)
	completedData = []
	twitterExists = False
	if result is not None:
		for i in result:
			if result[i]['title']['main']:
				twitterExists = True
				completedData = result[i]
	if twitterExists == False:
		toAdd = {}
		toAdd['title'] = {}
		toAdd['title']['main'] = 'main'
		toAdd['title']['title'] = title
		results = callTweet(urllib.pathname2url(title), 500)
		completedData = results
		toAdd['results'] = results
		firebase.post('/twitter', toAdd)
	constructedData = []
	for i in completedData['results']:
		score = i['sentiment']['doc']['score']
		created_at = i['created_at']
		constructedData.append({ 'score': score, 'date': created_at })
	return constructedData

# GetArticle from the URL, and return JSON
def getArticle(url):
	# Beautiful Soup scraping for Article
	s = requests.Session()
	mainPage = s.get(url)
	mainPagesoup = BeautifulSoup(mainPage.text)
	title = mainPagesoup.find("h1")
	p = mainPagesoup.find_all("p")
	img = mainPagesoup.find_all("img")
	title = title.getText()

	# Use API to get keywords, etc.
	result = firebase.get('/nytimes', None)
	NYTimesExist = False
	if result is not None:
		for i in result:
			if result[i]['title']['main']:
				twitterExists = True
				completedData = result[i]

	api = articleAPI(NYTimes_API_KEY)
	articles = api.search(q = ("\"" + title + "\""), hl = True)
	currentArticle = articles['response']['docs'][0]

	# Article text Engine
	nltkText = ''
	allText = ''
	for eachSelection in p:
		nltkText += (eachSelection.getText() + ' ')
		allText += (eachSelection.getText() + '<br><br>')

	allImages = []
	for eachImage in img:
		allImages.append(eachImage['src'])
	currentArticle['allText'] = allText	
	currentArticle['nltk'] = nltkText
	currentArticle['img'] = allImages
	currentArticle['twitter'] = twitterSentimentAnalysis(title)

	# Definition Engine
	imagesRuleThemAll = []
	currentState = ''
	for eachKeyword in range(0, len(currentArticle['keywords'])):
		if currentArticle['keywords'][eachKeyword]['name'] == "glocations":
			for x in stateNameToCode.keys():
				if x in currentArticle['keywords'][eachKeyword]['value']:
					currentState = x
		currentWord = currentArticle['keywords'][eachKeyword]['value']
		currentDefinition = wikipedia.summary(currentWord, sentences=1)
		currentArticle['keywords'][eachKeyword]['definition'] = currentDefinition


	currentArticle['stateBelongingTo'] = currentState
	if currentState != "":
		bloomberg = bloombergSentimentLocation('SMLYUS' + currentState + ' Index')
		currentArticle['bloombergData'] = bloomberg
	else:
		currentArticle['bloombergData'] = []

	currentLengthX = len(currentArticle['keywords'])/2
	currentArticle['bestRankedKeyword'] = currentArticle['keywords'][currentLengthX]['value']
	imagesRuleThemAll.append(searchImgur(currentArticle['keywords'][currentLengthX]['value']))
	for i in allImages:
		imagesRuleThemAll[0].append(i)
	currentArticle['allimages'] = imagesRuleThemAll
	currentArticle['allimages'][0] = currentArticle['allimages'][0][::-1]
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