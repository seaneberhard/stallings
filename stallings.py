@total_ordering
class Generator(object):
    def __init__(self, name, inv = False):
        self.name = name
        self.inv = inv
        
    def inv(self):
        return Generator(self.name, not self.inv)
    
    def __mul__(self, other):
        return other.nbrs[self]
        
    def __lt__(self, other):
        return (self.name, self.inv) < (other.name, other.inv)
        
    def __eq__(self, other):
        return (self.name, self.inv) == (other.name, other.inv)
        
    def __hash__(self):
        return hash((self.name, self.inv))
    
    
class Graph(object):
    # make a basic Stallings graph on generators gens on k roots
    def __init__(self, gens = [], k = 1):
        self.gens = sorted(list(set(gens + [g.inv() for g in gens])))
        self.roots = [Node() for i in range(k)]
        self.numVerts = k
        self.numEdges = 0
                           
    def NumVertices(self):
        return self.numVerts
                           
    def NumEdges(self):
        return self.numEdges
                           
    def Chi(self):
        return self.NumVertices() - self.NumEdges()
    
    # do Stallings foldings where needed, and just generally tidy up
    def Fold(self):
        
    def eta(self, other):
        
    def __le__(self, other):
        return self.eta(other)
    
    def __eq__(self, other):
        return self <= other and other <= self
    
    def __add__(self, other):
        comb = Graph(self.gens + other.gens, len(self.roots) + len(other.roots))
        for i in range(len(self.roots)):
            comb.roots[i].merge(self.roots[i])
        for i in range(len(other.roots)):
            comb.roots[len(self.roots) + i].merge(other.roots[i])
        comb.Fold()
        return comb
    
    def copy(self):
        copy = Graph(self.gens, len(self.roots))
        
    
    def __mul__(self, k):
        return sum([self.copy() for i in range(k)])
    
    @classmethod
    def FromWord(cls, word):
        graph = Graph(word)
        node = graph.roots[0]
        for g in word:
            node.nbrs[g] = Node()
            node = node.nbrs[g]
        node.merge(graph.roots[0])
        graph.Fold()
        return graph
        
    def FromWords(cls, words):
        graph = sum([Graph.FromWord(w) for w in words])
        root = Node()
        for r in graph.roots:
            root.merge(r)
        graph.roots = [root]
        graph.Fold()
        return graph
        
class Node(object):
    def __init__(self):
        self.nbrs = {}
        self.dup = set([self]) # nodes waiting to be folded into this one
    
    def degree(self):
        return len(self.nbrs)
    
    def merge(self, other):
        self.dup += other.dup
        other.dup = self.dup
