from functools import total_ordering

inf = float("inf")

@total_ordering
class Generator(object):
    def __init__(self, name, inverted = False):
        self.name = name
        self.inverted = inverted

    def __str__(self):
        return self.name + ("^-1" if self.inverted else "")
        
    def inv(self):
        return Generator(self.name, not self.inverted)

    def __lt__(self, other):
        return (self.name, self.inverted) < (other.name, other.inverted)

    def __eq__(self, other):
        return (self.name, self.inverted) == (other.name, other.inverted)
        
    def __hash__(self):
        return hash((self.name, self.inverted))

class Word(list):
    def __str__(self):
        return "*".join([str(g) for g in self])

    def __mul__(self, v):
        if isinstance(v, self.__class__):
            w = Word(self + v)
            w.red()
            return w
        for g in self[::-1]:
            v = g * v
        return v

    def inv(self):
        return Word([g.inv() for g in self[::-1]])

    def red(self):
        i = 0
        while i + 1 < len(self):
            if self[i] == self[i+1].inv():
                self[i:i+2] = []
                i = max(i-1,0)
            else:
                i += 1

    def __pow__(self, n):
        w = Word(list(self) * abs(n))
        if n < 0:
            w = w.inv()
        w.red()
        return w

class Graph(object):
    # make a basic singleton Stallings graph with 1 root
    def __init__(self):
        self.roots = [Node()]
        self._verts = []
        self._hash = 0
        self.rehash()
        self._desc = None
        self._pi = None
        
    def rehash(self):
        count = 0
        labels = {}
        self.roots = [r.find() for r in self.roots]
        stack = []
        self._verts = []
        for r in self.roots:
            if not r in labels:
                labels[r] = count
                count += 1
                stack.append(r)
                self._verts.append(r)
        while len(stack) > 0:
            v = stack.pop()
            for g in v.gens():
                if not g * v in labels:
                    labels[g * v] = count
                    count += 1
                    stack.append(g * v)
                    self._verts.append(g * v)
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
                if not self.roots[i] in eta:
                    eta[self.roots[i]] = other.roots[i]
                elif not eta[self.roots[i]] == other.roots[i]:
                    return None
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
        
    def __ne__(self, other):
        return not self == other
    
    def __add__(self, other):
        comb = Graph()
        comb.roots = self.copy().roots + other.copy().roots
        comb.rehash()
        return comb

    def __mul__(self, k):
        if k < 1:
            return NotImplemented
        if k == 1:
            return self
        return self * (k-1) + self
    
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
    def fromWord(cls, word):
        return cls.fromWords([word])

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
        if self._desc is None:
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
            alg = {g : True for g in graphs}
            for l in links:
                if l[0].chi() - l[1].chi() == 1:
                    alg[l[1]] = False
            self._desc = (graphs, links, alg)
        return self._desc

    def pi(self):
        if self._pi is None:
            desc = self.descendents()
            self._pi = max([-inf] + [d.chi() for d in desc[0] if self != d and desc[2][d]])
        return self._pi
        
    def crit(self):
        desc = self.descendents()
        return [d for d in desc[0] if d != self and desc[2][d] and d.chi() == self.pi()]

    def toCsv(self, filename):
        count = 0
        labels = {}
        edges = []
        for r in self.roots:
            if r not in labels:
                count += 1
                labels[r] = count
        stack = labels.keys()
        while len(stack) > 0:
            v = stack.pop()
            for g in v.gens():
                if not g * v in labels:
                    count += 1
                    labels[g * v] = count
                    stack.append(g * v)
                if not g.inverted:
                    edges.append((str(labels[v]), str(labels[g * v]), str(g)))
        with open(filename, "w") as f:
            f.writelines([",".join(e) + "\n" for e in edges])

    def descendentsToCsv(self, filename, chi = ""):
        desc = self.descendents()
        count = 0
        labels = {}
        for g in desc[0]:
            count += 1
            labels[g] = count
        edges = []
        for e in desc[1]:
            edges.append([str(labels[e[0]]), str(labels[e[1]])])
        with open(filename, "w") as f:
            f.writelines([",".join(e) + "\n" for e in edges])
        if chi != "":
            with open(chi, "w") as f:
                f.writelines([",".join([str(labels[g]), str(g.chi())]) + "\n" for g in desc[0]])

    def csvs(self):
        self.toCsv("g.csv")
        self.descendentsToCsv("gd.csv", "gdchi.csv")

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



### standard variables
x = Word([Generator("x")])
y = Word([Generator("y")])
z = Word([Generator("z")])