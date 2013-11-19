#!/usr/bin/env python

import os
import sys

dir = os.path.join(sys.argv[1])
outdir = sys.argv[1] + '/tmg-format/'
if (os.path.exists(outdir)==False):
  os.mkdir(outdir)
for file in os.listdir(dir):
  if file.endswith('.txt'):
    with open(file) as ifs:
      ofsname = outdir + file
      ofs = open(ofsname, 'w')
      for line in ifs:
        ofs.write(line + '\n')
      ofs.close()
