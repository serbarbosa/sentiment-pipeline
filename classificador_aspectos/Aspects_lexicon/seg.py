import pickle

def write_pickle(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

data = None
with open('explicit_aspects.p', 'rb') as f:

    data = pickle.load(f)
cont = 0

d1 = {}
d2 = {}
for k, v in data.items():
    
    if len(k.split(' ')) > 1:
        d2[k] = v
    else:
        d1[k] = v

write_pickle('explicit_aspects1.p', d1)
write_pickle('explicit_aspects2.p', d2)

data = None
with open('implicit_aspects.p', 'rb') as f:
    data = pickle.load(f)

d3 = {}
d4 = {}
for k, v in data.items():
    
    if len(k.split(' ')) > 1:
        d4[k] = v
    else:
        d3[k] = v

write_pickle('implicit_aspects1.p', d3)
write_pickle('implicit_aspects2.p', d4)

