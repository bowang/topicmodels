#!/usr/bin/env python

import os
import sys

dir = os.path.join(sys.argv[1])
for root,dirs,files in os.walk(dir):
  for file in files:
    if file.endswith('.txt'):
      with open(os.path.join(root,file)) as ifs:
      	ofs = open(file, 'w')
        for line in ifs:
          ofs.write(line + '\n')
        ofs.close()
