
import sys
import argparse
import math

import ac_class
import error_analysis

def run(args):
  ac_obj= ac_class.ac(args)   
  print("Total nodes: ", len(ac_obj.graph))
  if args.format == 'float':
    for mant_bits in range(7,20):
      error_analysis.set_ac_node_bits(ac_obj, mant_bits)
      error= error_analysis.error_eval(ac_obj, 'float', ac_obj.head_node, custom_bitwidth= False)
      c= math.log(error+1)/math.log(1+2**(-mant_bits-1))
      low_error= 1 - (1-2**(-mant_bits-1))**c
      
#      kwargs= {'precision': 'CUSTOM', 'arith_type' : 'FLOAT', 'exp': 9, 'mant': mant_bits}
#      energy= src.energy.energy_est(ac_obj.graph, **kwargs)
      
#      print('for ', mant_bits,' bits mantt the rel. error bound is: ', error, ' for negative c, error could be: ', low_error, ', energy in fJ: ', energy)
      print('for ', mant_bits,' mantissa bits the rel. error bound is: ', error)

  elif args.format == 'fixed':
    # TODO : Error analysis fixed point
    print("Fixed-point error analysis needs an init step which is not implemented in this release. Sorry!")

  # TODO : Automatic HW generation


def main(argv=None):
  parser = argparse.ArgumentParser(description='Auto power estimation script')
  parser.add_argument('name', type=str, choices=['alarm', 'HAR_NaiveBayes26F', 'HAR_TAN26F', 'HAR_TAN' 'UIWADS_NaiveBayes3F_class1' , 'UIWADS_NaiveBayes3F_class2', 'UNIMIB_NB_window10', 'UNIMIB_TAN_window10'] ,help='Enter the name of the network to be analysed')
  parser.add_argument('format', type=str, choices=['fixed','float'], help='Enter the format to be used')
#  parser.add_argument('EXP/INT_bits', type=int, choices=list(range(2,50)), help='bits for EXP or INTEGER part')
#  parser.add_argument('MNT/FRAC_bits', type=int, choices=list(range(2,50)), help='bits for MANTTISA or FRACTION part')

  args = parser.parse_args(argv)
  run(args)

if __name__ == "__main__":
  sys.exit(main())

