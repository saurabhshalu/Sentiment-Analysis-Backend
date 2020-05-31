from django.http import HttpResponse
from .models import Searchres
from .models import Detailed
import json
import tweepy
from datetime import timedelta
from tweepy import OAuthHandler
from datetime import datetime
import preprocessor as p
import GetOldTweets3 as got
from wordcloud import WordCloud
import urllib
import matplotlib.pyplot as plt
import io
import base64
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()
import os

def word_cloud(text):
    try:
        wc = WordCloud(width=1600, height=800,random_state=1, max_words=100,colormap="Paired", background_color='black',)
        wc = wc.generate(text)
        plt.figure(figsize=(10,5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        image = io.BytesIO()
        plt.savefig(image, format='png')
        image.seek(0)  # rewind the data
        string = base64.b64encode(image.read())

        image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
        return image_64
    except:
        pass

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    if score['compound']<=-0.01:
        return -1
    if score['compound']>=0.01:
        return 1
    else:
        return 0

def clean_tweet(tweet):
    p.set_options(p.OPT.URL)
    x=p.clean(tweet)
    return x.replace('#', '')
def to_dictsim(x):
    l1=[]
    l2=[]
    try:
        l2.append(x.postweet1)
    except:
        pass
    try:
        l1.append(x.negtweet1)
    except:
        pass
    try:
        l2.append(x.postweet2)
    except:
        pass
    try:
        l1.append(x.negtweet2)
    except:
        pass
    y = {"hashtag": x.hashtag, 'positive':x.positive,'negative':x.negative,'negtweet':l1,'postweet':l2,'tweetcount':x.tweetcount,"time":x.time1,"poswc":x.poswc,"negwc":x.negwc}
    return y
#resobj = Searchres(hashtag='',time=0,positive=0,negative=0,postweet=[],negtweet=[],tweetcount=0)
#detres = Detailed(hashtag='',poslist = [],neglist = [],postweet = [],negtweet = [],tweetcountl=0,dorm=0,countofdorm=0,label=[])
#test for github
def monthret(x):
    if x==1:
        return 'jan'
    if x==2:
        return 'Feb'
    if x==3:
        return 'Mar'
    if x==4:
        return 'Apr'
    if x==5:
        return 'May'
    if x==6:
        return 'june'
    if x==7:
        return 'july'
    if x==8:
        return 'Aug'
    if x==9:
        return 'Sept'
    if x==10:
        return 'Oct'
    if x==11:
        return 'Nov'
    if x==12:
        return 'Dec'

def to_integer(dt_time):
    return 1000000*dt_time.year + 10000*dt_time.month + 100*dt_time.day +  4*dt_time.hour +int(dt_time.minute/15)

class TwitterClient(object):

    def __init__(self):

        consumer_key = os.environ.get('consumer_key')
        consumer_secret = os.environ.get('consumer_secret')
        access_token = os.environ.get('access_token')
        access_token_secret = os.environ.get('access_token_secret')

        try:

            self.auth = OAuthHandler(consumer_key, consumer_secret)

            self.auth.set_access_token(access_token, access_token_secret)

            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")


    def simfetching_tweets(self, query,type=0, count=100):
        msgs = []
        i=1
        if type == 0 :
            try:
                for tweet in tweepy.Cursor(self.api.search, lang='en', count=100, q=query).items(count):
                    i = i + 1
                    msgs.append(tweet)
            except:
                pass
            return msgs

    def simget_tweets(self, query,type=0, count=100):

        tweets = []
        try:

            fetched_tweets=self.simfetching_tweets(query,type,count)
            for tweet in fetched_tweets:

                parsed_tweet = {}
                parsed_tweet['status'] = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                y = clean_tweet(tweet.text)
                parsed_tweet['text'] = y
                parsed_tweet['sentiment'] = sentiment_analyzer_scores(y)
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
    def detfetching_tweets(self, query ,until,since ,type=0, count=100):
        msgs = []
        i=1
        if type == 0 :
            try:
                for tweet in tweepy.Cursor(self.api.search,until =until,since =since, lang='en', count=100, q=query).items(count):
                    i = i + 1
                    msgs.append(tweet)
            except:
                pass
            return msgs

    def detget_tweets(self, query,until,since ,type=0, count=100):
        tweets = []
        try:
            fetched_tweets = self.detfetching_tweets(query,until,since, type, count)
            for tweet in fetched_tweets:

                parsed_tweet = {}
                parsed_tweet['status'] = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                y = clean_tweet(tweet.text)
                parsed_tweet['text'] = y
                parsed_tweet['sentiment'] = sentiment_analyzer_scores(y)
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def simpleanalysis(request):

    api = TwitterClient()
    if request.method == 'GET':
        hashtag1 = request.GET['hashtag']
        tweetcounting = 100
        try:
            tweetcounting = int(request.GET['tcount'])
        except:
            pass
        j = -1
        searchress = Searchres.objects.all().order_by('-time1')
        for i in range(0, searchress.count()):
            if searchress[i].hashtag == hashtag1:
                j = i
                time1 = int(to_integer(datetime.now()))
                diff = time1 - searchress[j].time1
                if diff >= 1:
                    j = -1
                break
        if j >= 0:
            resobj1 = searchress[j]
            return to_dictsim(resobj1)

        else:
            hashtag2 = '#' + hashtag1
            resobj = Searchres(hashtag='', time1=0, positive=0, negative=0, tweetcount=0)
            resobj.hashtag = hashtag1
            tweets = api.simget_tweets(query=hashtag2 ,type=0, count=tweetcounting)
            resobj.positive=0
            resobj.negetive=0
            if len(tweets) > 0:
                ptweets=[]
                ptext=''
                for tweet in tweets:
                    if tweet['sentiment'] == 1:
                        ptweets.append(tweet)
                        ptext = ptext + " " + tweet['text']
                ntweets = []
                ntext = ''
                for tweet in tweets:
                    if tweet['sentiment'] == -1:
                        ntweets.append(tweet)
                        ntext = ntext + " " + tweet['text']
                #ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 1]
                resobj.positive = 100 * len(ptweets) / len(tweets)
                #ntweets = [tweet for tweet in tweets if tweet['sentiment'] == -1]
                resobj.negative = 100 * len(ntweets) / len(tweets)
                resobj.poswc = word_cloud(ptext)
                resobj.negwc = word_cloud(ntext)
                try:
                    resobj.postweet1 = ptweets[len(ptweets)-1]['status']
                except:
                    pass
                try:
                    resobj.negtweet1 = ntweets[len(ntweets) - 1]['status']
                except:
                    pass
                try:
                    resobj.postweet2 = ptweets[len(ptweets) - 2]['status']
                except:
                    pass
                try:
                    resobj.negtweet2 = ntweets[len(ntweets) - 2]['status']
                except:
                    pass
            resobj.time1 = to_integer(datetime.now())
            resobj.tweetcount = len(tweets)
            resobj.save()
            return to_dictsim(resobj)
def detailedanalysis(request):
    api = TwitterClient()
    if request.method == 'GET':
        hashtag1 = request.GET['hashtag']
        hashtag2 = '#' + hashtag1
        dorm = int(request.GET['dorm'])
        countofdorm = 6
        try:
            countofdorm = int(request.GET['countofdorm'])
        except:
            pass
        tweetcounting = 100
        try:
            tweetcounting = int(request.GET['tcount'])
        except:
            pass
        resobj = Detailed(hashtag=hashtag1, time1=to_integer(datetime.now()), tweetcount=tweetcounting, dorm=dorm,countofdorm=countofdorm,positive=0,negative=0)
        tcountp=0
        tcountn=0
        ttcount=0
        label = []
        count = []
        poslist = []
        neglist = []
        postweet = []
        negtweet= []
        ntext = ''
        ptext = ''
        if dorm == 0:
            x = datetime.today()
            for key in range(countofdorm):
                edate = x - timedelta(days=key)
                sdate = x - timedelta(days=key+1)
                tweets = api.detget_tweets(query=hashtag2, type=0,until=edate.strftime('%Y-%m-%d'),since=sdate.strftime('%Y-%m-%d') ,count=tweetcounting)
                positive = 0
                negative = 0
                pz=0
                if len(tweets) > 0:
                    ptweets=[]
                    for tweet in tweets:
                        if tweet['sentiment'] == 1:
                            ptweets.append(tweet)
                            ptext = ptext + " " + tweet['text']
                    ntweets = []
                    for tweet in tweets:
                        if tweet['sentiment'] == -1:
                            ntweets.append(tweet)
                            ntext = ntext + " " + tweet['text']
                    px=len(ptweets)
                    py=len(tweets)
                    positive = 100 * px/py
                    ttcount += py
                    tcountp += px
                    pz=len(ntweets)
                    negative = 100 * pz/py
                label.append(str(edate.strftime('%d'))+"/"+ str(monthret(int(edate.strftime('%m')))))
                count.append(len(tweets))
                poslist.append(positive)
                neglist.append(negative)
                tcountn+=pz
                if key == 0:
                    try:
                        postweet.append(ptweets[len(ptweets) - 1]['status'])
                    except:
                        pass
                    try:
                        negtweet.append(ntweets[len(ntweets) - 1]['status'])
                    except:
                        pass
                    try:
                        postweet.append(ptweets[len(ptweets) - 2]['status'])
                    except:
                        pass
                    try:
                        negtweet.append(ntweets[len(ntweets) - 2]['status'])
                    except:
                        pass


        elif dorm==1:
            x = datetime.now().month
            y1 = datetime.now().year
            for key in range(countofdorm):
                month1=x-key
                year1 = y1
                if month1 <= 0 :
                    year1 = y1 - 1
                    month1 += 12
                dates1 = str(year1) + '-' + str(month1) + '-'
                tweetCriteria = got.manager.TweetCriteria().setQuerySearch(hashtag2) \
                    .setSince(dates1 + "01") \
                    .setUntil(dates1 + "28") \
                    .setMaxTweets(tweetcounting)
                try:
                    tweetgot = got.manager.TweetManager.getTweets(tweetCriteria)
                    tweets = []
                    for tweet in tweetgot:

                        parsed_tweet = {}
                        parsed_tweet['status'] = f'https://twitter.com/{tweet.username}/status/{tweet.id}'
                        y = clean_tweet(tweet.text)
                        parsed_tweet['text'] = y
                        parsed_tweet['sentiment'] = sentiment_analyzer_scores(y)
                        if tweet.retweets > 0:
                            if parsed_tweet not in tweets:
                                tweets.append(parsed_tweet)
                        else:
                            tweets.append(parsed_tweet)
                    positive = 0
                    negative = 0
                    if len(tweets) > 0:
                        ptweets = []
                        for tweet in tweets:
                            if tweet['sentiment'] == 1:
                                ptweets.append(tweet)
                                ptext = ptext + " " + tweet['text']
                        ntweets = []
                        for tweet in tweets:
                            if tweet['sentiment'] == -1:
                                ntweets.append(tweet)
                                ntext = ntext + " " + tweet['text']
                        positive = 100 * len(ptweets) / len(tweets)
                        negative = 100 * len(ntweets) / len(tweets)
                    label.append(str(monthret(month1)) + "/" + str(year1))
                    count.append(len(tweets))
                    poslist.append(positive)
                    neglist.append(negative)
                    ttcount += len(tweets)
                    tcountp += len(ptweets)
                    tcountn += len(ntweets)
                    if key == 0:
                        try:
                            postweet.append(ptweets[len(ptweets) - 1]['status'])
                        except:
                            pass
                        try:
                            negtweet.append(ntweets[len(ntweets) - 1]['status'])
                        except:
                            pass
                        try:
                            postweet.append(ptweets[len(ptweets) - 2]['status'])
                        except:
                            pass
                        try:
                            negtweet.append(ntweets[len(ntweets) - 2]['status'])
                        except:
                            pass
                except:
                    pass
        if ttcount > 0:
            resobj.positive = 100 * tcountp / ttcount
            resobj.negative = 100 * tcountn / ttcount
            resobj.poswc = word_cloud(ptext)
            resobj.negwc = word_cloud(ntext)
            resobj.save()
            return {"hashtag": hashtag1, 'positive': resobj.positive, 'negative': resobj.negative,
            'tweetcount': ttcount, "time": resobj.time1, "label": label, "count": count, "poslist": poslist,
            "neglist": neglist, 'postweet': postweet, "negtweet": negtweet, "ptweet": tcountp, "ntweet": tcountn,"poswc":resobj.poswc,"negwc":resobj.negwc}

def index(request):
    res=''
    if request.method == 'GET':
        reqtype = 0
        try:reqtype = int(request.GET['type'])
        except:pass
        if reqtype==1:
            res = detailedanalysis(request)
        else:
            res = simpleanalysis(request)
    response = HttpResponse(json.dumps(res))
    response['Access-Control-Allow-Origin'] = 'https://sentiapp.netlify.app/'
    response['Access-Control-Allow-Methods'] = 'GET'
    return response








