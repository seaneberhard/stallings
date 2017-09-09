@total_ordering
class Generator(object):
    def __init__(self, name, inv = False):
        self.name = name
        self.inv = False
        
    def inv(self):
        return Generator(self.name, !self.inv)
        
    def __lt__(self, other):
        return (self.name, self.inv) < (other.name, other.inv)
        
    def __eq__(self, other):
        return (self.name, self.inv) == (other.name, other.inv)
        
    def __hash__(self):
        return hash((self.name, self.inv))
        
    
