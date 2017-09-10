def Generator(object):
  def __init__(self, name):
    self.name = name
    while self.name.endswith("ii"):
      self.name = self.name[:-2]
  
  def inv(self):
    if self.name.endswith("i"):
      return Generator(self.name[:-1])
    return Generator(self.name + "i")
    
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.name == other.name
    return NotImplemented
    
  def __ne__(self, other):
    return not self == other
    
  def __hash__(self):
