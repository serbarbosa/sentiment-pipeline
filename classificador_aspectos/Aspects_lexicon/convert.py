import pickle

data = None
with open('explicit_aspects.p', 'rb') as f:
    data = pickle.load(f)
d = {}
for i in range(len(data)):
    d[data[i]] = i

with open('explicit_aspects.p', 'wb') as f:
    pickle.dump(d, f)


with open('explicit_aspects.p', 'rb') as f:
    data = pickle.load(f)
    print(data)
