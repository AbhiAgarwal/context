from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans

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
    #trim irrelevant data points: vectorize w.r.t. reference article keywords, vs all keywords.
    trimmed_vectorized = []
    for i in xrange(0, len(vectorized)):
        trimmed_vectorized.append(vectorized[i][-num_reference_keys:])
        
    num_clusters = 50
    km = KMeans(n_clusters = num_clusters, init='random', n_init=1, verbose=1)
    km.fit(trimmed_vectorized)
    reference_label = km.labels_[0]
        
    for i in xrange(0, len(km.labels_)):
       if (reference_label == km.labels_[i]):
           related_articles_inds.append(i)
    
    related_articles_urls = []
    
    for i in xrange(0, len(related_articles_inds)):
       index = related_articles_inds[i]
       related_articles_urls.append(articles[index]["web_url"])
    
    return related_articles_urls