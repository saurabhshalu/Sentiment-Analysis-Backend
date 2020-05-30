import preprocessor as p
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()
def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))
p.set_options(p.OPT.URL)
x='#awesome #dead #hello'
y=x.replace('#','')
print(p.clean(y))
sentiment_analyzer_scores(y)