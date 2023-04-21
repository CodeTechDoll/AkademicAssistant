import numpy as np
from torch import softmax
from transformers import pipeline
from transformers import AutoTokenizer, AutoConfig
from transformers import AutoModelForSequenceClassification

from config import config

TOKENIZER = config.get("DEFAULT", "tokenizer")
SENTIMENT_MODEL = config.get("DEFAULT", "sentiment_model")


def tokenize(text):
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
    return tokenizer.tokenize(text)


def prepare_model(model_name, model_type, tokenizer):
    model = model_type.from_pretrained(model_name)
    #model.save_pretrained(model_name)
    model.resize_token_embeddings(len(tokenizer))
    return model


def generate_sentiment(model_name, tokenizer, text):
    nlp = pipeline("sentiment-analysis", model=model_name, tokenizer=tokenizer)
    result = nlp(text)
    return result[0]["label"]


# Example usage of the functions
text = "This is a sample text. It is used to test the functions in the ai_pipeline.py file."


tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
config = AutoConfig.from_pretrained(SENTIMENT_MODEL)
model = prepare_model(SENTIMENT_MODEL, AutoModelForSequenceClassification, tokenizer=tokenizer)
encoded_input = tokenizer(text, return_tensors='pt')
output = model(**encoded_input)
scores = output[0][0].detach().numpy()
scores = softmax(scores)

ranking = np.argsort(scores)
ranking = ranking[::-1]
for i in range(scores.shape[0]):
    l = config.id2label[ranking[i]]
    s = scores[ranking[i]]
    print(f"{i+1}) {l} {np.round(float(s), 4)}")