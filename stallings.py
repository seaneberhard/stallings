class Generator(object):
    def __init__(self, name, inverted = False):
        self.name = name
        self.inverted = inverted
        
    def inv(self):
        return Generator(self.name, not self.inverted)

    def __lt__(self, other):
        return (self.name, self.inverted) < (other.name, other.inverted)

    def __eq__(self, other):
        return (self.name, self.inverted) == (other.name, other.inverted)
        
    def __hash__(self):
        return hash((self.name, self.inverted))
    
    
class Graph(object):
    # make a basic singleton Stallings graph with 1 root
    def __init__(self):
        self.roots = [Node()]
        self._verts = 0
        self._hash = 0
        self.rehash()
        
    def rehash(self):
        count = 0
        labels = {}
        self.roots = [r.find() for r in self.roots]
        for r in self.roots:
            if not r in labels:
                labels[r] = count
                count += 1
        stack = labels.keys()
        while len(stack) > 0:
            v = stack.pop()
            for g in v.gens():
                if not g * v in labels:
                    labels[g * v] = count
                    count += 1
                    stack.append(g * v)
        self._verts = labels.keys()
        self._numEdges = sum([v.degree() for v in self._verts]) / 2
        self._hash = hash((tuple([labels[r] for r in self.roots]),
            tuple([(g, labels[v], labels[g*v]) for v in self._verts for g in v.gens()])))

    def __hash__(self):
        return self._hash
      
    def numVertices(self):
        return len(self._verts)
                           
    def numEdges(self):
        return self._numEdges
                           
    def chi(self):
        return self.numVertices() - self.numEdges()
        
    def eta(self, other):
        try:
            eta = {}
            verts = set(self.roots)
            stack = self.roots[:]
            for i in range(len(self.roots)):
                eta[self.roots[i]] = other.roots[i]
            while len(stack) > 0:
                v = stack.pop()
                for g in v.gens():
                    if not g * v in verts:
                        verts.add(g * v)
                        stack.append(g * v)
                        eta[g * v] = g * eta[v]
                    elif not eta[g * v] == g * eta[v]:
                        return None
            return eta
        except KeyError:
            return None

    def __le__(self, other):
        return not self.eta(other) is None

    def __eq__(self, other):
        return self <= other and other <= self 
    
    def __add__(self, other):
        comb = Graph()
        comb.roots = self.copy().roots + other.copy().roots
        comb.rehash()
        return comb

    def __mul__(self, k):
        return sum([self] * k)
    
    def copy(self):
        eta = {}
        for r in self.roots:
            if r not in eta:
                eta[r] = Node()
        stack = eta.keys()[:]
        while len(stack) > 0:
            v = stack.pop()
            for g in v.gens():
                if not g * v in eta:
                    eta[g * v] = Node()
                    stack.append(g * v)
                eta[v][g] = eta[g * v]
        graph = Graph()
        graph.roots = [eta[r] for r in self.roots]
        graph.rehash()
        return graph
        
    @classmethod
    def fromWords(cls, words):
        graph = Graph()
        for word in words:
            node = graph.roots[0]
            for g in word:
                node[g] = Node()
                node = node[g]
            node.merge(graph.roots[0])
        graph.rehash()
        return graph

    def children(self):
        kids = []
        for i in range(self.numVertices()):
            for j in range(i+1, self.numVertices()):
                graph = self.copy()
                eta = self.eta(graph)
                u = eta[self._verts[i]]
                v = eta[self._verts[j]]
                u.merge(v)
                graph.rehash()
                if not graph in kids:
                    kids.append(graph)
        return kids

    def descendents(self):
        graphs = [self]
        links = []
        stack = [self]
        while len(stack) > 0:
            g = stack.pop()
            kids = g.children()
            for kid in kids:
                links.append((g, kid))
                if not kid in graphs:
                    graphs.append(kid)
                    stack.append(kid)
        psAlg = {g : True for g in graphs}
        for l in links:
            if l[0].chi() - l[1].chi() == 1:
                psAlg[l[1]] = False
        return (graphs, psAlg)

    def prim

class Node(object):
    def __init__(self):
        self._nbrs = {}
        # union-find fields
        self._up = self
        self._rank = 0
    
    def find(self):
        if self._up != self:
            self._up = self._up.find()
        return self._up

    def merge(self, other):
        # find reps and quit if they are the same
        find1 = self.find()
        find2 = other.find()
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
        find2._nbrs = None
            
    def gens(self):
        return sorted(self.find()._nbrs.keys())
    
    def degree(self):
        return len(self.gens())
    
    def __getitem__(self, g):
        nbrs = self.find()._nbrs
        nbrs[g] = nbrs[g].find()
        return nbrs[g]
    
    def __setitem__(self, g, nbr):
        if g in self.gens():
            self[g].merge(nbr)
        else:
            self.find()._nbrs[g] = nbr.find()
            nbr[g.inv()] = self

    def __rmul__(self, other): 
        return self[other]