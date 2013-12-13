#!/usr/bin/env python

import os
import sys
import re
from collections import Counter

dir = os.path.join(sys.argv[1])
for root,dirs,files in os.walk(dir):
  for file in files:
    if file.endswith('.txt'):
      with open(os.path.join(root,file)) as f:
        for line in f:
          line = line.strip()
          line = re.sub('[,;.\'\"]', ' ', line)
          print Counter(line.split()).most_common()
