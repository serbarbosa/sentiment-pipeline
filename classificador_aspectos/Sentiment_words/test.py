import pickle

data = None

with open('sent_words_polarity.p', 'rb') as f:
    data = pickle.load(f)


for entry in data.keys():

    print(entry)


