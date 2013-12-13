#!/usr/bin/env python
import sys
import os

dir = os.path.join(sys.argv[1])
for root,dirs,files in os.walk(dir):
  for file in files:
    if file.endswith('.abs'):
      slash_count = 0;
      with open(os.path.join(root,file)) as f:
        for line in f:
          line = line.strip()
          tokens = line.split(" ")
          if (len(tokens)==0):
            continue
          if (tokens[0]=='Title:'):
            for i in range(1, len(tokens)):
              print tokens[i],
            print ''
          elif (tokens[0]=='\\\\'):
            slash_count += 1
          elif (slash_count==2):
            print line + ' ',
      print '\n'
