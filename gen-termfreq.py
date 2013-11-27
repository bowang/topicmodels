#!/usr/bin/env python
import sys
import os
import re
import inflect
import operator
from collections import OrderedDict
from stemming.porter2 import stem

min_term_freq = 5
min_phrase_freq = 3
min_term_length = 3
max_phrase_length = 5
print_limit = 100000

p = inflect.engine()
stopwords = set()
commonverbs = set()
docs = {}
vocab = {}
phrases = {}

def addPhrase (phrase, docid):
  weight = len(phrase.split())
  if phrase not in phrases:
    phrases[phrase] = 1
    docs[docid][phrase] = weight
  else:
    if phrase not in docs[docid]:
      phrases[phrase] += 1
      docs[docid][phrase] = weight
    else:
      docs[docid][phrase] += weight

def addTerm (term, docid):
  if term not in vocab:
    vocab[term] = 1
    docs[docid][term] = 1
  else:
    if term not in docs[docid]:
      vocab[term] += 1
      docs[docid][term] = 1
    else:
      docs[docid][term] += 1

def shiftArray (arr):
  for i in range(0, len(arr) - 1):
    arr[i] = arr[i + 1]

def main():
  with open(sys.argv[2]) as f:
    for line in f:
      stopwords.add(line.strip())

  if len(sys.argv) >= 4:
    with open(sys.argv[3]) as f:
      for line in f:
        commonverbs.add(line.strip())

  docid = 1
  docs[docid] = {}

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
        seqlen = 0
        prevs = [0] * max_phrase_length
        for token in segment.split():
          # remove leading and trailing non alphanumeric characters
          token = token.replace('--', '-').lstrip('\"\'`~!-+*_').rstrip('\"\'`!~-+*_')
          # remove latex format tokens
          # remove stop words
          # remove common verbs
          # remove tokens containing no letters
          # remove tokens shorter than least term length
          if len(re.findall(r'[${}+\[\]\\]+', token)) > 0 or \
             token in stopwords or \
             stem(token) in commonverbs or \
             not any(c.isalpha() for c in token) or \
             len(token) < min_term_length:
            seqlen = 0
            continue
          else:
            # convert to singular form
            if all(c.isalpha() for c in token):
              singular = p.singular_noun(token)
              if singular != False:
                token = singular.lower()
            # generate word groups
            if seqlen < max_phrase_length - 1:
              prevs[seqlen] = token
              seqlen += 1
            else:
              shiftArray(prevs)
              prevs[seqlen] = token
            phrase = token
            for i in range(seqlen - 2, -1, -1):
              phrase = str(prevs[i]) + ' ' + phrase
              addPhrase(phrase, docid)
          # generate words
          token = stem(token)
          addTerm (token, docid)

  vocab_eff = OrderedDict(sorted(filter(lambda (k, v): v >= min_term_freq, vocab.items())))
  phrases_eff = OrderedDict(sorted(filter(lambda (k, v): v >= min_phrase_freq, phrases.items())))
  vocab_eff_keys = vocab_eff.keys()
  phrases_eff_keys = phrases_eff.keys()
  num_vocab_eff = len(vocab_eff)
  num_phrases_eff = len(phrases_eff)

  print 'effective vocabulary ({}): '.format(num_vocab_eff)
  if num_vocab_eff < print_limit:
    print vocab_eff
    print ''
  print 'effective phrases ({}): '.format(num_phrases_eff)
  if num_phrases_eff < print_limit:
    print phrases_eff
    print ''

  # print top terms/phrases
  vocab_eff_rvs = sorted(vocab_eff.iteritems(), key=operator.itemgetter(1), reverse=True)
  phrases_eff_rvs = sorted(phrases_eff.iteritems(), key=operator.itemgetter(1), reverse=True)
  print 'top 10 out of {} terms'.format(num_vocab_eff)
  for i in range(1,11):
    print vocab_eff_rvs[i]
  print '\ntop 10 out of {} phrases'.format(num_phrases_eff)
  for i in range(1,11):
    print phrases_eff_rvs[i]

  # generate term:freq matrix
  tffile = open('termfreq.txt', 'w')
  for docid in range(1, len(docs) + (len(docs[len(docs)]) > 0)):
    tflist = ''
    tfnum = 0
    for term in docs[docid]:
      if term in vocab_eff:
        tflist += ' ' + str(vocab_eff_keys.index(term)) + ':' + str(docs[docid][term])
        tfnum += 1
      elif term in phrases_eff:
        tflist += ' ' + str(phrases_eff_keys.index(term) + num_vocab_eff) + ':' + str(docs[docid][term])
        tfnum += 1
    tffile.write(str(tfnum) + tflist + '\n')
  tffile.close()

  # generate dictionary
  dicfile = open('dictionary.txt', 'w')
  for term in vocab_eff:
    dicfile.write('\"' + term + '\"\n')
  for term in phrases_eff:
    dicfile.write('\"' + term + '\"\n')
  dicfile.close()

  # generate docmap
  dmfile = open('docmap.txt', 'w')
  for docid in range(1, len(docs) + (len(docs[len(docs)]) > 0)):
    dmfile.write('doc' + str(docid) + '\n');
  dmfile.close()
if  __name__ =='__main__':main()
