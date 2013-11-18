#!/usr/bin/env python
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import time

for year in range(1992, 2003):
	for month in range(1, 12):
		id = str((year%100) * 100 + month)
		print id
		site = requests.get('http://arxiv.org/list/cond-mat/' + id + '?show=3000')
		soup = BeautifulSoup(site.text.encode('ISO-8859-1'))
		f = open(id + '.txt', 'w')
		divs = soup.findAll('div', 'list-title')
		for div in divs:
		    f.write(div.contents[2].encode('utf-8'))
		f.close()
