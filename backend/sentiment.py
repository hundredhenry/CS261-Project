from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_pipeline = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")

    def get_sentiment(self, content):
        sentiment = self.sentiment_pipeline(content)