from collections import defaultdict
import queue
import math 
import time
import networkx as nx

#**** imports from our codebase *****
import custom_arith 

def ac_eval_non_recurse(graph, graph_nx):
  topological_list= nx.algorithms.dag.topological_sort(graph_nx)
  for key in topological_list:
    obj= graph[key]
    if obj.is_sum():
      result= 0.0
      for child in obj.child_key_list:
        result= result + graph[child].curr_val
      
      obj.curr_val = result

    if obj.is_product():
      result= 1.0
      for child in obj.child_key_list:
        result= result * graph[child].curr_val
      
      obj.curr_val = result

  return graph[topological_list[-1]].curr_val
  
def ac_eval(graph, final_node, elimop= 'SUM', **kwargs):
  
  assert elimop in ['SUM', 'MAX', 'MIN', 'PROD_BECOMES_SUM'], "Elimination operation provided for AC_eval is invalid"
 
  precision= 'FULL'
  if kwargs is not None:
    if 'precision' in kwargs:
      assert kwargs['precision'] in ['FULL', 'CUSTOM']
      if kwargs['precision'] == 'CUSTOM':
        precision= 'CUSTOM'

    if precision == 'CUSTOM':
      assert 'arith_type' in kwargs, "arith_type has to be passed if precision is CUSTOM"
      assert kwargs['arith_type'] in ['FIXED', 'FLOAT']
      arith_type= kwargs['arith_type']

      if arith_type == 'FIXED':
        assert 'int' in kwargs, "number of int bits has to be passed if arith_type is FIXED"
        assert kwargs['int'] < 50 and kwargs['int'] > 0, "number of int bits should be in range (0,50)"
        int_bits= kwargs['int']
        
        assert 'frac' in kwargs, "number of frac bits has to be passed if arith_type is FIXED"
        assert kwargs['frac'] < 50 and kwargs['frac'] > 0, "number of frac bits should be in range (0,50)"
        frac_bits= kwargs['frac']
        
      if arith_type == 'FLOAT':
        assert 'exp' in kwargs, "number of exp bits has to be passed if arith_type is FLOAT"
        assert kwargs['exp'] < 50 and kwargs['exp'] > 0, "number of exp bits should be in range (0,50)"
        exp_bits= kwargs['exp']
        
        assert 'mant' in kwargs, "number of mant bits has to be passed if arith_type is FLOAT"
        assert kwargs['mant'] < 50 and kwargs['mant'] > 0, "number of mant bits should be in range (0,50)"
        mant_bits= kwargs['mant']

  #ac_node_list= list(graph.keys())

  # A dict to keep track of evaluated nodes
  # Key: Ac node number
  # Val: By default: False
  #done_nodes= dict.fromkeys(ac_node_list, False)
  done_nodes = {}

  #done_nodes= defaultdict(lambda: False, done_nodes) # All keys initialized to 0
  
  # Stores the value of the smallest non-zero number in the entire network for this query
  global_min_val = [1.0]
  
  ac_query_val= ac_eval_recurse(final_node, graph, done_nodes, global_min_val, elimop, **kwargs)
  
  if precision== 'CUSTOM':
    if arith_type == 'FIXED':
      ac_query_val= custom_arith.FixedPoint_To_FloatingPoint(ac_query_val, int_bits, frac_bits)  
    elif arith_type == 'FLOAT':
      ac_query_val= custom_arith.custom_flt_to_flt(ac_query_val, exp_bits, mant_bits, denorm= False)  
  
  #print "Smallest val in this query: ", global_min_val[0], 'Exp_bits: ', math.log(abs(math.log(global_min_val[0],2)),2)

  return ac_query_val


def ac_eval_recurse(curr_node, graph, done_nodes, global_min_val, elimop, **kwargs):
  """ kwargs:
    'precision' = FULL or CUSTOM
    'arith_type' = FIXED or FLOAT
    
    Only valid if 'arith_type' is FIXED:
      'int' = Number of integer bits
      'frac' = Number of fraction bits
    
    Only valid if 'arith_type' is FLOAT:
      'exp' = Number of exponent bits
      'mant' = Number of mantissa bits

    Example:
      kwargs= {'precision': 'CUSTOM', 'arith_type' : 'FIXED', 'int': 8, 'frac': 23}
  """

  #--- Process arguments
  assert elimop in ['SUM', 'MAX', 'MIN', 'PROD_BECOMES_SUM'], "Elimination operation provided for AC_eval is invalid"

  precision= 'FULL'
  if kwargs is not None:
    if 'precision' in kwargs:
      assert kwargs['precision'] in ['FULL', 'CUSTOM']
      if kwargs['precision'] == 'CUSTOM':
        precision= 'CUSTOM'

    if precision == 'CUSTOM':
      assert 'arith_type' in kwargs, "arith_type has to be passed if precision is CUSTOM"
      assert kwargs['arith_type'] in ['FIXED', 'FLOAT']
      arith_type= kwargs['arith_type']

      if arith_type == 'FIXED':
        assert 'int' in kwargs, "number of int bits has to be passed if arith_type is FIXED"
        assert kwargs['int'] < 50 and kwargs['int'] > 0, "number of int bits should be in range (0,50)"
        int_bits= kwargs['int']
        
        assert 'frac' in kwargs, "number of frac bits has to be passed if arith_type is FIXED"
        assert kwargs['frac'] < 50 and kwargs['frac'] > 0, "number of frac bits should be in range (0,50)"
        frac_bits= kwargs['frac']
        
      if arith_type == 'FLOAT':
        assert 'exp' in kwargs, "number of exp bits has to be passed if arith_type is FLOAT"
        assert kwargs['exp'] < 50 and kwargs['exp'] > 0, "number of exp bits should be in range (0,50)"
        exp_bits= kwargs['exp']
        
        assert 'mant' in kwargs, "number of mant bits has to be passed if arith_type is FLOAT"
        assert kwargs['mant'] < 50 and kwargs['mant'] > 0, "number of mant bits should be in range (0,50)"
        mant_bits= kwargs['mant']
      

  #---- Functionality starts here------

  if done_nodes.get(curr_node, False) == True:    
    return graph[curr_node].curr_val
  
  # This is a leaf node
  if graph[curr_node].is_leaf():
    #done_nodes[curr_node]= True
    if precision == 'FULL':
      result = graph[curr_node].curr_val
    elif precision == 'CUSTOM':
      if arith_type == 'FIXED':
        result = custom_arith.FloatingPntToFixedPoint(graph[curr_node].curr_val, int_bits, frac_bits)
      elif arith_type == 'FLOAT':
        result = custom_arith.flt_to_custom_flt(graph[curr_node].curr_val, exp_bits, mant_bits, denorm= False)
        
    return result 

  # If not leaf node and not evaluated yet
  if graph[curr_node].is_product():
    if elimop == 'PROD_BECOMES_SUM':
      result = 0
    else:
      result = 1
  elif graph[curr_node].is_sum():
    if elimop == 'SUM' or 'PROD_BECOMES_SUM':
      result = 0
    elif elimop == 'MIN':
      result = 1000
    elif elimop == 'MAX':
      result = 0

  if precision == 'CUSTOM':
    if arith_type == 'FIXED':
      result = custom_arith.FloatingPntToFixedPoint(result, int_bits, frac_bits)
    elif arith_type == 'FLOAT':
      result = custom_arith.flt_to_custom_flt(result, exp_bits, mant_bits, denorm=False)
      
  for child in graph[curr_node].child_key_list:
    child_val= ac_eval_recurse(child, graph, done_nodes, global_min_val, elimop, **kwargs)

    if graph[curr_node].is_product():
      if precision == 'FULL':
        if elimop == 'PROD_BECOMES_SUM':
          result = result + child_val
        else:
          result = result * child_val

      elif precision == 'CUSTOM':
        if arith_type == 'FIXED':
          result= custom_arith.fix_mul(result, child_val, int_bits, frac_bits)
        elif arith_type == 'FLOAT':
          result= custom_arith.flt_mul(result, child_val, exp_bits, mant_bits, denorm=False)        

    elif graph[curr_node].is_sum():
      if precision == 'FULL':
        if elimop == 'SUM' or 'PROD_BECOMES_SUM':
          result = result + child_val
        elif elimop == 'MIN':
          if child_val < result:
            result = child_val
        elif elimop == 'MAX':
          if child_val > result:
            result = child_val
      
      elif precision == 'CUSTOM':
        if elimop == 'SUM' or 'PROD_BECOMES_SUM':
          if arith_type == 'FIXED':
            result= custom_arith.fix_add(result, child_val, int_bits, frac_bits)
          elif arith_type == 'FLOAT':
            result= custom_arith.flt_add(result, child_val, exp_bits, mant_bits, denorm=False)        
        else:
          assert 0, "Not implemented yet."
  
  if elimop == 'MIN':
    graph[curr_node].min_val= result
    
  done_nodes[curr_node] = True
  graph[curr_node].curr_val= result
  
  # Update gloabl_min_val
  if result < global_min_val[0] and result != 0:
    global_min_val[0] = result
  
  assert result < 2**63

  return result

def copy_curr_to_max(analysis_obj):
  for key, obj in list(analysis_obj.graph.items()):
    obj.max_val= obj.curr_val

def error_propogate_recurse(analysis_obj, curr_node, done_nodes, arith_type, verb):
  """
  Usage from graph_analysis.py:
    For float:
    #print "Min query val: ", src.ac_eval.ac_eval(self.graph, self.head_node, 'MIN')
    #error= src.ac_eval.error_propogate_recurse(self, self.head_node, dict.fromkeys(self.ac_node_list, False), 'float', bits)
    #error= error -1
    For fixed:
    print  "No evidence AC eval: ", src.ac_eval.ac_eval(self.graph, self.head_node)
    src.ac_eval.copy_curr_to_max(self)
    error= src.ac_eval.error_propogate_recurse(self, self.head_node, dict.fromkeys(self.ac_node_list, False), 'fixed')
  """
  assert arith_type in ['float', 'fixed'], "Invalid arith_type passed tp error propogate"
  
  graph= analysis_obj.graph
  if done_nodes.get(curr_node, False) == True: 
    if arith_type == 'float':
      return graph[curr_node].rel_error_val
    elif arith_type == 'fixed':
      return graph[curr_node].abs_error_val


  # This is a leaf node
  if graph[curr_node].is_leaf():
    done_nodes[curr_node]= True
    
    if arith_type == 'float':
      """ Following functionality not in this release
      if graph[curr_node].leaf_type== graph[curr_node].LEAF_TYPE_WEIGHT:
        graph[curr_node].rel_error_val= (1 + 2**-(graph[curr_node].bits+1))
      elif graph[curr_node].leaf_type== graph[curr_node].LEAF_TYPE_INDICATOR:
        graph[curr_node].rel_error_val= 1 
      else:
        print("Unsupported leaf type")
        exit(1)
      """
      graph[curr_node].rel_error_val= (1 + 2**-(graph[curr_node].bits+1))
      return graph[curr_node].rel_error_val
    
    elif arith_type == 'fixed':
      """ Following functionality not in this release
      if graph[curr_node].leaf_type== graph[curr_node].LEAF_TYPE_WEIGHT:
        graph[curr_node].abs_error_val = 2**-(graph[curr_node].bits+1)
      elif graph[curr_node].leaf_type== graph[curr_node].LEAF_TYPE_INDICATOR:
        graph[curr_node].abs_error_val = 0
      else:
        print("Unsupported leaf type")
        exit(1)
      """
      graph[curr_node].abs_error_val = 2**-(graph[curr_node].bits+1)
      return graph[curr_node].abs_error_val
  

  # If not leaf node and not evaluated yet, compute the error
  
  if arith_type == 'float': 
    if graph[curr_node].is_product():
      result = 1.0
    elif graph[curr_node].is_sum():
      result = 0.0
    
    child_err_list=[]
    child_min_list=[]
    child_max_list=[]
    for child in graph[curr_node].child_key_list:
      child_val= error_propogate_recurse(analysis_obj, child, done_nodes, arith_type, verb)
      child_err_list.append(child_val)
      child_min_list.append(graph[child].min_val)
      child_max_list.append(graph[child].max_val)

      if graph[curr_node].is_product():
        result = result * child_val
      
      if graph[curr_node].is_sum():
        if child_val > result:
          result= child_val

    result= result * (1+ 2**-(graph[curr_node].bits+1))
    
    done_nodes[curr_node] = True
    graph[curr_node].rel_error_val= result 
    
    return result

  elif arith_type == 'fixed':
    result = 0.0
    
    child_err_list=[]
    child_min_list=[]
    child_max_list=[]
    child_bit_list=[]
    child_key_list=[]
    for child in graph[curr_node].child_key_list:
      child_val= error_propogate_recurse(analysis_obj, child, done_nodes, arith_type, verb)
      child_err_list.append(child_val)
      child_min_list.append(graph[child].min_val)
      child_max_list.append(graph[child].max_val)
      child_bit_list.append(graph[child].bits)
      child_key_list.append(child)

    # Error propogated from children
    # Following code assumes 2 children, i.e., AC is binarized
    if graph[curr_node].is_product():
      result= child_max_list[0]*child_err_list[1] + child_max_list[1]*child_err_list[0] + child_err_list[0]*child_err_list[1]
    if graph[curr_node].is_sum():
      result= child_err_list[0] + child_err_list[1]
    
    # Error added due to curr operation (Only in product)
    if graph[curr_node].is_product():
      result= result + 2**-(graph[curr_node].bits+1)
    if graph[curr_node].is_sum():
      if graph[curr_node].bits < child_bit_list[0] or graph[curr_node].bits < child_bit_list[1]:
        result= result + 2**-(graph[curr_node].bits+1)
  
    done_nodes[curr_node] = True
    graph[curr_node].abs_error_val= result 
    
    return result

def error_eval(self, arith_type, node, custom_bitwidth= False, verb= False):
  """ In case of error_eval for uniform bit width, set bit_width of each node using set_ac_node_bits method before calling this method
  Usage from graph_analysis.py:
    src.ac_eval.error_eval(self, 'fixed', self.head_node, custom_bitwidth= False)
    OR
    src.ac_eval.set_ac_node_bits(self, bits= 21)
    src.ac_eval.error_eval(self, 'fixed', self.head_node, custom_bitwidth= True)
  """
  assert arith_type in ['float', 'fixed'], "Invalid arith_type passed tp error propogate"
  #assert bits > 0 and bits < 54, "bits should be greater than 0 and less than 54 (max limit due to double-precision float limit)"
  
  if custom_bitwidth:
    assert 0, "Funcitonality not implemented in this release. It allows using custom bitwidth for different nodes."

  if arith_type == 'float':
    #ac_eval(self.graph, node, 'MIN')
    error= error_propogate_recurse(self, node, dict.fromkeys(list(self.graph.keys()), False), 'float', verb)
    error= error -1
  
  elif arith_type =='fixed': 
    #print "AC val with given evidence:", 
    ac_eval(self.graph, node)
    copy_curr_to_max(self)
    error= error_propogate_recurse(self, node, dict.fromkeys(list(self.graph.keys()), False), 'fixed', verb)
  
  return error

def set_ac_node_bits(analysis_obj, bits):
  assert bits > 0 and bits < 54, "bits should be greater than 0 and less than 54 (max limit due to double-precision float limit)"
  for key, obj in list(analysis_obj.graph.items()):
    obj.bits= bits
  

