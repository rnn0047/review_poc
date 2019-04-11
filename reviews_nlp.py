#
# author: ram.nagpure@gmail.com
# purpose: Using YELP data carry out NLP on user reviews to identify why a good restaurant is good
# tests: TBD

import requests
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

def getYelpBusinessData(url, params, key):
    """
    url:    str; endpoint to yelp api (https://api.yelp.com/v3/businesses/search)
    params: dict; with keys like 'term', 'limit', 'radius', 'location', etc. to identify properties of requested data
    key:    str; clients access key (obtain from YELP)

    rtype:  dict containing response data if successful else throw exception
    """
    if url == None or len(url) < 5 or params == None or len(params) < 2 or key == None or len(key) < 10:
        errMsg ="Input parameters cannot be empty or Null\n\t passed URL:{}\n\t passed params:{}\n\t passed key:{}".format(
                    url, params, key)
        raise Exception(errMsg)

    headers = {'Authorization': 'bearer {}'.format(key)}
    response = requests.get(url= url, params = params, headers = headers)
    data = response.json()
    if (data.get('error', None)):
        raise Exeption("Errored in calling YELP: {}".format(data.get('error')))

    return data

def getYelpUserReviews( buid, key, url=None):
    """
    buid:   str; yelp business id
    key:    str; clients access key (obtain from YELP)
    url:    str; endpoint to yelp review api (https://api.yelp.com/v3/businesses/{buid}/reviews)

    rtype:  dict of dicts containing review data if successful else throw exception
    Note - Only 3 recent reviews are returned per business
    """

    if buid == None or len(buid) < 10 or  key == None or len(key) < 10:
        errMsg ="Input parameters cannot be empty or Null\n\t passed buid:{}\n\t passed key:{}".format(buid, key)
        raise Exception(errMsg)
    if url == None:
        url = 'https://api.yelp.com/v3/businesses/{}/reviews'.format(buid)
    headers = {'Authorization': 'bearer {}'.format(key)}
    response = requests.get(url= url, headers = headers)

    data = response.json()
    if (data.get('error', None)):
        raise Exeption("Errored in calling YELP reviews: {}".format(data.get('error')))

    uReviews = [{'id': buid,
                 'name': review.get('user').get('name'),
                 'userID':review.get('user').get('id'),
                 'userRating':review.get('rating'),
                 'userComment':review.get('text')} for review in data['reviews']]
    return uReviews


def transformTBData(tb_obj):
    """
    utility function to transform TextBlob object into meaningful information

    type: tb_obj -  TextBlob object
    rtype: tuple(float, float, str, str) - polarity, subjectivity, keyword, sentence with the keyword
    """

    assmt = tb_obj.sentiment_assessments
    sense = assmt.polarity #score [-1.0, 1.0] i.e. from very negative to very positive
    sub = assmt.subjectivity #score [0.0, 1.0] i.e. 0.0 is very objective and 1.0 very subjective
    k_t = assmt.assessments
    keyword = None
    sentence= None

    k_t.sort(key=lambda x:x[1]) #sort on polarity
    for i in range(len(k_t)):
        if len(k_t[i]) > 1 and k_t[i][1] >= sense:
            keyword = str(' '.join(k_t[i][0]))
            break

    #find sentence with the keyword
    for sent in tb_obj.sentences:
        if keyword and keyword.replace(" !","") in sent.lower(): #need to remove special char like '!' in search
            sentence = str(sent)
            break

    return (sense, sub, keyword, sentence )
