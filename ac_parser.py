
import ac_class

def parse_ac_file(node_obj, global_var):
  op_list= read_ac_file(global_var)
  op_list= binarize_op_list(op_list, global_var)

  ac= create_graph_from_op_list(node_obj, op_list, global_var)
  
  leaf_list= [node for node, obj in list(ac.items()) if obj.is_leaf()]
  
  return ac, leaf_list

def add_node(graph, node_key, child_key_list, op_type):
    # Add the node and update it's child list
    node_obj= ac_class.node(node_key)
    for item in child_key_list:
      node_obj.add_child(item)
    node_obj.operation_type= op_type
    
    graph[node_obj.key]= node_obj
    
    # Update parent list of the child
    for item in child_key_list:
      graph[item].add_parent(node_key)


def create_graph_from_op_list(node_obj, op_list, global_var):
  graph= {}
  for item in op_list:
    node_key= item[0]
    
    op_type= 0
    if (item[1] == global_var.OPERATION_NAME_PRODUCT):
      child_key_list= item[2:]
      op_type= node_obj.PRODUCT
    elif (item[1] == global_var.OPERATION_NAME_SUM):
      child_key_list= item[2:]
      op_type= node_obj.SUM
    elif (item[1] == global_var.OPERATION_NAME_LEAF):
      child_key_list= []
      op_type= node_obj.LEAF
    else:
      print("Error in op_type while creating graph from op_list")
      exit(1)

    add_node(graph, node_key, child_key_list, op_type)
    
    # Mark the leaf node as computed
    if graph[node_key].is_leaf():
      graph[node_key].computed= 1

  return graph

def binarize_op_list(op_list, global_var):
  """
    As hardware operators generally have 2 inputs, convert non-binary graph to binary graph
  """
  total_offset= 0
  #new_op_list= op_list[:]
  new_op_list_1= []

  # This dict maps new key in the new binarized op_list to original key of the non-binary op_list
  map_BinaryOpListKey_To_OriginalKey= {}
  
  offset_list= []

  for idx, arg in enumerate(op_list):
    # Offset all numbers in arg
    arg_w_offset= []
    for opcode_idx, opcode in enumerate(arg):
      if opcode_idx == 0:
        arg_w_offset.append(opcode + total_offset)
      if opcode_idx == 1: # operator
        arg_w_offset.append(opcode)   
      if opcode_idx > 1:
        # Add offset to rest of the numbers only if this is not a leaf node
        if not arg[1] == global_var.OPERATION_NAME_LEAF:
          assert len(offset_list) > opcode, [len(offset_list),opcode, idx, arg]
          arg_w_offset.append(opcode + offset_list[opcode])
        else:
          arg_w_offset.append(opcode)

    # check if operator has more than 2 inputs
    if (len(arg) > 4):
      new_idx= idx + total_offset
      
      # remove the big instr from the list
      #del new_op_list[new_idx]
      
      # Break up the big instruction in smaller instructions
      oper_name = arg_w_offset[1]
      n_input= len(arg_w_offset) - 2
      input_list = arg_w_offset[2:]
      curr_instr_idx= new_idx
      new_instr_list= []
      while (n_input > 1):
        n_remain_input = n_input
        output_list= [] # The list that contains all the outputs of this level, to be used as inputs for the next level
        while (n_remain_input > 1):
          output_list.append(curr_instr_idx)
          
          new_instr= []
          new_instr.append(curr_instr_idx)
          new_instr.append(oper_name) # Operation name
          new_instr.append(input_list[0])
          new_instr.append(input_list[1])

          #new_op_list.insert(curr_instr_idx, new_instr)
          new_op_list_1.append(new_instr)
          
          map_BinaryOpListKey_To_OriginalKey[curr_instr_idx] = idx

          curr_instr_idx = curr_instr_idx + 1 
          input_list = input_list[2:] # remove inputs consumed in curr instruction
          n_remain_input = n_remain_input-2
        
        n_input= n_input/2 + (n_input & 1)
        output_list = output_list + input_list # Add the last unpaired element of input list to the output list
        input_list= output_list[:] # Copy all elements of output_list to input_list for next iteration
      
      t0= time.time()
      # Add offset to all the integers in the list
      offset= curr_instr_idx - new_idx - 1
      #new_op_list= _add_offset_to_op_list(new_op_list, curr_instr_idx, new_idx, offset)
      total_offset = total_offset + offset
      
      # Record the offset in the offset list
      offset_list.append(total_offset)
      
      t1= time.time()
      #print 2,t1-t0
    
    else: # Code will enter this else when the instruction has less than 2 inputs and do not need to be expanded in a binary tree 
      offset_list.append(total_offset) # No offset to be added for this instruction, as it is not expanded in a binary tree structure
      new_op_list_1.append(arg_w_offset)
      map_BinaryOpListKey_To_OriginalKey[arg_w_offset[0]] = arg[0]
  
  return new_op_list_1 


def read_ac_file(global_var):
  """
    Parses .ac format, retruns op_list
  """
  
  fp= open(global_var.AC_FILE, 'r')
  ac= fp.readlines()

  # Remove first line of type "nnf 23 26 7"
  if 'nnf' in ac[0]:
    ac = ac[1:]

  # Determine which type of AC file it is
  # Type 1: One with A,O and L 
  # Type 2: One with *,+ and l
  ac_type_1= 0
  ac_type_2= 1
  if ac[0].split(' ')[0] == 'L':
    ac_type= ac_type_1 
  elif ac[0].split(' ')[0] == 'l':
    ac_type= ac_type_2
  else:
    print("Unknown format of net.ac file")
    exit(1)

  if ac_type == ac_type_1: # one with A,O and L
    # remove '\n' from the end of each line and split with space
    ac= [i[:-1].split(' ') for i in ac]
    
    # Remove first element in A and two elements in O
    for arg in ac:
      if (arg[0] == 'A'):
        del arg[1]
      if (arg[0] == 'O'):
        del arg[2]
        del arg [1]
    
    new_ac=[]
    for op_idx, operation in enumerate(ac):
      new_op= []
      for idx,arg in enumerate(operation):
        # Replace 'A', 'O' and 'L' with terms in op_list
        if arg == 'L':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_LEAF)
        elif arg == 'A':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_PRODUCT)
        elif arg == 'O':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_SUM)

        # Change numbers from str to int
        if idx > 0:
          new_op.append(int(arg))
    
  
      new_ac.append(new_op)
    
    return new_ac
  
  elif ac_type == ac_type_2: # one with +,* and l
    new_ac = [] 
    for op_idx, operation in enumerate(ac):
      # remove '\n' from the end of each line and split with space
      operation_spl= operation[:-1].split(' ')
      
      # Remove first element in * and + line
      if ('*' in operation_spl) or ('+' in operation_spl):
        del operation_spl[1]
      
      new_op=[]
      for idx,arg in enumerate(operation_spl):
        if arg == 'l':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_LEAF)
        elif arg == '*':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_PRODUCT)
        elif arg == '+':
          new_op.append(op_idx)
          new_op.append(global_var.OPERATION_NAME_SUM)
        
        # Change numbers from str to int
        if idx > 0:
          new_op.append(int(arg))

      new_ac.append(new_op)
    
    return new_ac
