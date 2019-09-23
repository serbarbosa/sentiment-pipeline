# An efficient information reTRIEval data structure
class TrieNode(object):
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.is_special_end = False
        self.polarity = ''
    def __repr__(self):
        return str(self.children)


def insert(root_node, word):
    n = root_node
    set_end = False
    #verifica se deve permitir parada antes
    if word[0][-1] == '*':
        word[0] = word[0][:-1]
        set_end = True

    for character in word[0]:
        
        t = None
        if character not in n.children:
            t = TrieNode()
            n.children[character] = t
        else:
            t = n.children.get(character)
        
        n = t
    n.is_end = True
    n.polarity = word[1]
    n.is_special_end = set_end

def search(root_node, search_string):
    node = root_node
    for character in search_string:
        if node.is_special_end: return True, node.polarity
        
        c = node.children.get(character)
        if not c:
            return False, node.polarity
        node = c
    
    return node.is_end, node.polarity

import pickle
if __name__ == '__main__':

    root = TrieNode()
    data = None

    with open('Sentiment_words/sent_words_polarity.p', 'rb') as f:
        data = pickle.load(f)
        
    for k, v in data.items():
        #print('['+k+', '+v+']' )
        insert(root, [k, v])
    
    print_trie(root)

    print(search(root, 'esgotado'))
