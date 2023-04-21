import numpy as np
from torch import softmax
from transformers import pipeline
from transformers import AutoTokenizer, AutoConfig
from transformers import AutoModelForSequenceClassification
from sentiment_analysis import SENTIMENT_MODEL, TOKENIZER
from sentiment_analysis import generate_sentiment, prepare_model
from parser import load_from_datafile


data, data_hash = load_from_datafile()
text = data[0]

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