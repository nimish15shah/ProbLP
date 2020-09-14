import inspect
import networkx as nx
import itertools

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    black   = '\u001b[30m'
    red     = '\u001b[31m'
    green   = '\u001b[32m'
    yellow  = '\u001b[33m'
    blue    = '\u001b[34m'
    magenta = '\u001b[35m'
    cyan    = '\u001b[36m'
    white   = '\u001b[37m'

    bblack  = '\u001b[30;1m'
    bred    = '\u001b[31;1m'
    bgreen  = '\u001b[32;1m'
    byellow = '\u001b[33;1m'
    bblue   = '\u001b[34;1m'
    bmagenta= '\u001b[35;1m'
    bcyan   = '\u001b[36;1m'
    bwhite  = '\u001b[37;1m'


    reset= '\u001b[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

        self.black   ='' 
        self.red     ='' 
        self.green   ='' 
        self.yellow  ='' 
        self.blue    ='' 
        self.magenta ='' 
        self.cyan    ='' 
        self.white   ='' 
        
        self.bblack   ='' 
        self.bred     ='' 
        self.bgreen   ='' 
        self.byellow  ='' 
        self.bblue    ='' 
        self.bmagenta ='' 
        self.bcyan    ='' 
        self.bwhite   ='' 
        

    def color(self, name= 'reset'):
      if name == 'red':
        return self.red 
      
      if name == 'black':
        return self.black

      if name == 'green':
        return self.green 

      if name == 'yellow':
        return self.yellow

      if name == 'blue':
        return self.blue 
      
      if name == 'magenta':
        return self.magenta 

      if name == 'cyan':
        return self.cyan

      if name == 'white':
        return self.white

      if name == 'bred':
        return self.bred 
      
      if name == 'bblack':
        return self.bblack

      if name == 'bgreen':
        return self.bgreen 

      if name == 'byellow':
        return self.byellow

      if name == 'bblue':
        return self.bblue 
      
      if name == 'bmagenta':
        return self.bmagenta 

      if name == 'bcyan':
        return self.bcyan

      if name == 'bwhite':
        return self.bwhite
  

      if name == 'reset':
        return self.reset

      return self.reset

def indices(a, func):
  """ Returns list of indices where func evals to True 
  @param a: list to be checked
  @param func: Test to be performed
  
  @example: indices(a, lambda x: x==1) returns all the indices of the list that contains value 1
  """ 
  return [i for (i, val) in enumerate(a) if func(val)]

def printlog(msg, color='reset'):
  callerframerecord = inspect.stack()[1]    # 0 represents this line
                                            # 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  filename= info.filename
  filename= filename.split('/')[-1]
  print(filename, ':', end=' ')                      # __FILE__     -> Test.py
  #print info.function, '::',                      # __FUNCTION__ -> Main
  print(info.lineno, ':', end=' ')                       # __LINE__     -> 13
  
  color_obj= bcolors()
  print(color_obj.color(color), end=' ')
  print(msg, end=' ')
  print(color_obj.color('reset'))

def printcol(msg, color= 'reset'):
  color_obj= bcolors()
  print(color_obj.color(color), end=' ')
  print(msg, end=' ')
  print(color_obj.color('reset'))
  

def create_nx_graph_from_node_graph(graph):
  """
    Creates an equivalent of self.graph (the default AC graph) in a networkx format.
  """

  G= nx.DiGraph()
  for node,obj in list(graph.items()):
    for parent in obj.parent_key_list:
      G.add_edge(node, parent)
  
  return G  

def check_if_only_one_root(graph):
  head_ls= [node for node, obj in list(graph.items()) if len(obj.parent_key_list) == 0]
  assert len(head_ls) == 1, [head_ls]

  return head_ls[0]

def clog2(num):
  assert num > 0
  return len(bin(num-1)) - 2

def format_hex(num, L):
  format_str= '{:0' + str(L//4) + 'x}'
  return format_str.format(num)

def get_leaves(graph_nx):
  return [n for n in graph_nx.nodes() if len(list(graph_nx.predecessors(n))) == 0]

def get_non_leaves(graph_nx):
  return [n for n in graph_nx.nodes() if len(list(graph_nx.predecessors(n))) != 0]

def compute_reverse_lvl(graph_nx):
  """ All leaves are at zero
  """
  topological_list= nx.algorithms.dag.topological_sort(graph_nx)
  
  map_v_to_reverse_lvl= {}

  for node in topological_list:
    curr_lvl= 0

    for p in graph_nx.predecessors(node):
      if curr_lvl <= map_v_to_reverse_lvl[p]:
        curr_lvl = map_v_to_reverse_lvl[p] + 1
    
    map_v_to_reverse_lvl[node]= curr_lvl

  return map_v_to_reverse_lvl

def relabel_nodes_with_contiguous_numbers(graph_nx, start= 0):
  """
    Creates a shallow copy
  """
  mapping= {n : (idx + start) for idx, n in enumerate(list(graph_nx.nodes()))}

  return nx.relabel.relabel_nodes(graph_nx, mapping, copy= True), mapping
  
def relabel_nodes_with_contiguous_numbers_leaves(graph_nx, start= 0):
  """
    Creates a shallow copy
    leaves from start, start+len(leaves)
    compute from start+len(leaves) + 1, ...
  """
  id_iter= itertools.count(start)

  leaves= get_leaves(graph_nx)
  mapping= {n : next(id_iter) for n in leaves}

  non_leaves= get_non_leaves(graph_nx)
  for n in non_leaves:
    mapping[n]= next(id_iter)

  return nx.relabel.relabel_nodes(graph_nx, mapping, copy= True), mapping
  
def ls_to_str(ls):
  ls= str(ls)
  ls= ls[1:-1]
  return ls

