#!/usr/bin/env python
import sys
import os
import re

separator = ';'
print 'Article_ID' + separator + 'Title' + separator + 'Abstract'
dir = os.path.join(sys.argv[1])
for root,dirs,files in os.walk(dir):
  for file in files:
    if file.endswith('.abs'):
      slash_count = 0;
      with open(os.path.join(root,file)) as f:
        print file.strip('.abs') + separator,
        for line in f:
          line = line.strip()
          line = re.sub('[,;.\'\"]', ' ', line)
          tokens = line.split(' ')
          if (len(tokens)==0):
            continue
          if (tokens[0]=='Title:'):
            for i in range(1, len(tokens)):
              print tokens[i],
          elif (tokens[0]=='\\\\'):
            slash_count += 1
            if (slash_count==2):
              print separator,
          elif (slash_count==2):
            print line + ' ',
        print ''
