
import useful_methods

class global_var():
  """
    Class that stores all the general names
  """
  
  def __init__(self, name):
    self.AC_FILE= './benchmarks/' + name +'.net.ac'

    self.OPERATION_NAME_PRODUCT= 'Product'
    self.OPERATION_NAME_LEAF= 'Leaf'
    self.OPERATION_NAME_SUM= 'Sum'

class ac():
  """
    Class that constains AC data structure
  """
  def __init__(self, args):
    self.name= args.name
    self.graph= {}
    self.graph_nx= None
    self.leaf_list= None
    self.global_var= global_var(self.name)
    
    self.construct_ac()

  def construct_ac(self):
    """
      populates self.graph and self.leaf_list
    """
    import ac_parser

    # To share the constants for  'operation_type'
    sample_node_obj= node(None)

    self.graph, self.leaf_list= ac_parser.parse_ac_file(sample_node_obj, self.global_var)
    self.graph_nx= useful_methods.create_nx_graph_from_node_graph(self.graph)
    self.head_node= useful_methods.check_if_only_one_root(self.graph)

  
class node():
  """
    class that stores properties of each node in AC
  """

  def __init__(self, node_key):
    self.key= node_key

    # Details about outgoing and incoming edges
    # NOTE: Here if A->B , A is child and B is parent. Opposite to conventional terminology
    self.child_key_list= []
    self.parent_key_list= []

    # Type of node
    self.PRODUCT= 0
    self.SUM= 1
    self.LEAF= 2
    self.operation_type= None

    # Important value during evaluation
    self.curr_val=0.0
    self.min_val=0.0
    self.max_val=1.0

    self.bits= None

  def is_leaf(self):
    assert self.operation_type != None
    if self.operation_type == self.LEAF:
      return True
    else:
      return False

  def is_sum(self):
    assert self.operation_type != None
    if self.operation_type == self.SUM:
      return True
    else:
      return False

  def is_product(self):
    assert self.operation_type != None
    if self.operation_type == self.PRODUCT:
      return True
    else:
      return False

  def add_child(self, child_key): # non-intuitively child = predecessor node
    assert isinstance(child_key, int), "child_key should be of int type"    
    self.child_key_list.append(child_key)

  def add_parent(self, parent_key): # non-intuitively parent = successor node
    assert isinstance(parent_key, int), "parent_key should be of int type"    
    self.parent_key_list.append(parent_key)
