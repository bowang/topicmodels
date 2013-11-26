#!/usr/bin/env python
import sys
import os
import re
import pprint
from collections import OrderedDict
from stemming.porter2 import stem

least_term_freq = 2
least_phrase_freq = 2

pp = pprint.PrettyPrinter()

def main():
  stopwords = set()
  with open(sys.argv[2]) as f:
    for line in f:
      stopwords.add(line.strip())

  docs = {}
  docid = 1
  docs[docid] = {}
  vocab = {}
  phrases = {}

  with open(sys.argv[1]) as f:
    for line in f:
      # empty line denotes the start of a new doc
      if line in ['\n', '\r\n']:
        docid += 1
        docs[docid] = {}
        if docid % 100 == 0:
          print 'docid = ' + str(docid)
        continue
      segments = re.split('[,;.:?!()]+', line)
      # skip doc hash tag
      if len(segments) == 1 and segments[0].find(' ') == -1:
        continue
      for segment in segments:
        segment = segment.strip().lstrip().lower()
        started = False
        prev = ""
        for token in segment.split():
          # remove latex format tokens
          if  len(re.findall(r'[${}\\]+', token)) > 0 or \
              token in stopwords or \
              token.isdigit():
            started = False
            continue
          # generate word groups
          elif started == False:
            started = True
            prev = token
          else:
            phrase = prev + ' ' + token
            prev = token
            if phrase not in phrases:
              phrases[phrase] = 1
              docs[docid][phrase] = 1
            else:
              if phrase not in docs[docid]:
                phrases[phrase] += 1
                docs[docid][phrase] = 1
              else:
                docs[docid][phrase] += 1
          # generate words
          token = stem(token)
          if token not in vocab:
            vocab[token] = 1
            docs[docid][token] = 1
          else:
            if token not in docs[docid]:
              vocab[token] += 1
              docs[docid][token] = 1
            else:
              docs[docid][token] += 1

  vocab_eff = OrderedDict(sorted(filter(lambda (k, v): v >= least_term_freq, vocab.items())))
  phrases_eff = OrderedDict(sorted(filter(lambda (k, v): v >= least_phrase_freq, phrases.items())))
  num_vocab_eff = len(vocab_eff)
  num_phrases_eff = len(phrases_eff)

  print 'effective vocabulary ({}): '.format(num_vocab_eff)
  print vocab_eff
  print ''
  print 'effective phrases ({}): '.format(num_phrases_eff)
  print phrases_eff
  print ''

  # generate term:freq matrix
  tffile = open('termfreq.txt', 'w')
  for docid in range(1, len(docs) + 1):
    tflist = ''
    tfnum = 0
    for term in docs[docid]:
      if term in vocab_eff:
        tflist += ' ' + str(vocab_eff.keys().index(term)) + ':' + str(docs[docid][term])
        tfnum += 1
      elif term in phrases_eff:
        tflist += ' ' + str(phrases_eff.keys().index(term) + num_vocab_eff) + ':' + str(docs[docid][term])
        tfnum += 1
    tffile.write(str(tfnum) + tflist + '\n')
  tffile.close()

  # generate dictionary
  dicfile = open('dictionary.txt', 'w')
  for term in vocab_eff:
    dicfile.write(term + '\n')
  for term in phrases_eff:
    dicfile.write(term + '\n')
  dicfile.close()

  # generate docmap
  dmfile = open('docmap.txt', 'w')
  for docid in range(1, len(docs) + 1):
    dmfile.write('doc' + str(docid) + '\n');
  dmfile.close()
if  __name__ =='__main__':main()
