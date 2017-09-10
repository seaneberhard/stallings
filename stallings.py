@total_ordering
class Generator(object):
    def __init__(self, name, inv = False):
        self.name = name
        self.inv = inv
        
    def inv(self):
        return Generator(self.name, not self.inv)
    
    def __mul__(self, other):
        return other[self]
        
    def __lt__(self, other):
        return (self.name, self.inv) < (other.name, other.inv)
        
    def __eq__(self, other):
        return (self.name, self.inv) == (other.name, other.inv)
        
    def __hash__(self):
        return hash((self.name, self.inv))
    
    
class Graph(object):
    # make a basic Stallings graph on generators gens on k roots
    def __init__(self):
        self.roots = [Node()]
        self.verts = self.roots[:]
        self.numEdges = 0
        
    def Refresh(self):
        verts = set(self.roots)
        stack = self.roots[:]
        while len(stack) > 0:
            v = stack.pop()
            for g in v.nbrs():
                if not g * v in verts:
                    verts.add(g * v)
                    stack.append(g * v)
        self.verts = list(verts)
        self.numEdges = sum([v.degree() for v in self.verts])/2
                           
    def NumVertices(self):
        return len(self.verts)
                           
    def NumEdges(self):
        return self.numEdges
                           
    def Chi(self):
        return self.NumVertices() - self.NumEdges()
        
    def eta(self, other):
        try:
            eta = {}
            verts = set(self.roots)
            stack = self.roots[:]
            for i in range(len(self.roots)):
                eta[self.roots[i]] = other.roots[i]
            while len(stack) > 0:
                v = stack.pop()
                for g in v.nbrs():
                    if not g * v in verts:
                        verts.add(g * v)
                        stack.append(g * v)
                        eta[g * v] = g * eta[v]
            return eta
        except KeyError:
            return None
        
    def __le__(self, other):
        return not self.eta(other) is None
    
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
        
    @classmethod
    def FromWords(cls, words):
        graph = Graph()
        for word in words:
            node = graph.roots[0]
            for g in word:
                node[g] = Node()
                node = node[g]
            node.merge(graph.roots[0])
        return graph
        
class Node(object):
    def __init__(self):
        self._nbrs = {}
        # union-find fields
        self._up = self
        self._rank = 0
    
    def _find(self):
        if self._up != self:
            self._up = self._up._find()
        return self._up
    
    def merge(self, other):
        # find reps and quit if they are the same
        find1 = self._find()
        find2 = other._find()
        if find1 == find2:
            return
        
        # identify the better root and call it find1
        if find1._rank < find2._rank:
            temp = find1
            find1 = find2
            find2 = temp
        elif find1._rank == find2._rank:
            find1._rank += 1
        find2._up = find1
        
        # absorb neighbours from find2 into find1
        for (g,nbr) in find2._nbrs.items():
            find1[g] = nbr
            
    def gens(self):
        return sorted(self._find()._nbrs.keys.gens())
    
    def degree(self):
        return len(self.gens)
    
    def __getitem__(self, g):
        nbrs = self.nbrs()
        nbrs[g] = nbrs[g]._find()
        return nbrs[g]
    
    def __setitem__(self, g, nbr):
        try:
            self[g].merge(nbr)
        except KeyError:
            self.nbrs()[g] = nbr._find()
            nbr[g.inv()] = self
