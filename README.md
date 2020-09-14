# ProbLP
Relative error bounds for custom floating-point arithmetic in Probabilisitic circuits.

Verified with Python3.7

Usage:
python main.py <circuit name> float
  Example: python main.py HAR_TAN26F float

NOTE: The abosolute error bounds for the fixed-pt arith. is also implemented but needs an additional step to initialize the leaf nodes, which is not implemented yet.

Dataset sources:
HAR: https://archive.ics.uci.edu/ml/datasets/human+activity+recognition+using+smartphones
UIWADS: https://archive.ics.uci.edu/ml/datasets/Activity+Recognition+from+Single+Chest-Mounted+Accelerometer
UNIMIB: http://www.sal.disco.unimib.it/technologies/unimib-shar/

Repository for the paper "ProbLP: A framework for low-precision probabilistic inference". Please cite this paper https://doi.org/10.1145/3316781.3317885 
