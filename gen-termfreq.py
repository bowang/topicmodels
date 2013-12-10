#!/usr/bin/env python
import sys
import os
import re
import inflect
import operator
from collections import OrderedDict
from stemming.porter2 import stem

min_term_freq = 5
min_phrase_freq = 5
min_term_length = 3
max_phrase_length = 5
print_top = 30

enable_term = True
enable_phrase = True

p = inflect.engine()
stopwords = set()
commonverbs = set()
docs = {}
vocab = {}
phrases = {}

def addPhrase (phrase, docid):
  # weight = len(phrase.split())
  weight = 1
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
  if len(sys.argv) < 3:
    print '{} [abstracts.txt] [stopwords.txt] (commonverbs.txt)'.format(sys.argv[0])
    return 1

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
        if docid % 100 == 0:
          print >> sys.stderr, 'docid = ' + str(docid)
        docs[docid] = {}
        continue
      segments = re.split('[,;.:?!()]+', line)
      # skip doc hash tag
      if len(segments) == 1 and segments[0].find(' ') == -1:
        continue
      for segment in segments:
        segment = segment.replace('--', '-').rstrip().lstrip().lower()
        seqlen = 0
        prevs = [0] * max_phrase_length
        tokens = segment.split()
        tokens_copy = tokens
        for token in tokens_copy:
          if len(token) > min_term_length:
            new_tokens = token.split('-')
            if len(new_tokens) > 1:
              flag = True
              for new_token in new_tokens:
                if len(new_token) < min_term_length:
                  flag = False
                  break
              if flag:
                tokens.remove(token)
                tokens.extend(new_tokens)

        for token in tokens:
          # remove leading and trailing non alphanumeric characters
          token = token.lstrip('\"\'`~!-+*_').rstrip('\"\'`!~-+*_')

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

          # convert to singular form
          if all(c.isalpha() for c in token):
            singular = p.singular_noun(token)
            if singular != False:
              token = singular.lower()

          # generate word groups
          if enable_phrase:
            if seqlen < max_phrase_length - 1:
              prevs[seqlen] = token
              seqlen += 1
            else:
              prevs[seqlen] = token
              shiftArray(prevs)
            phrase = token
            for i in range(seqlen - 2, -1, -1):
              phrase = prevs[i] + ' ' + phrase
              addPhrase(phrase, docid)

          # generate words
          if enable_term:
            token = stem(token)
            addTerm (token, docid)

  num_vocab_eff = 0
  num_phrases_eff = 0

  if enable_term:
    vocab_eff = OrderedDict(sorted(filter(lambda (k, v): v >= min_term_freq, vocab.items())))
    vocab_eff_keys = vocab_eff.keys()
    num_vocab_eff = len(vocab_eff)
    print 'effective vocabulary ({}): '.format(num_vocab_eff)
    print vocab_eff
    print ''

  if enable_phrase:
    # dedup sub phrases
    phrases_eff = dict(filter(lambda (k, v): v >= min_phrase_freq, phrases.items()))
    phrases_eff_keys = phrases_eff.keys()
    f = open('dedup.txt', 'w')
    dedup = set()
    for phrase in phrases_eff_keys:
      for anotherPhrase in phrases_eff_keys:
        if (phrase != anotherPhrase) and (phrase in anotherPhrase):
          if (phrases_eff[phrase] <= phrases_eff[anotherPhrase]):
            f.write('\"{}\" in \"{}\" ({}/{})\n'.format(phrase, anotherPhrase, phrases_eff[phrase], phrases_eff[anotherPhrase]))
            dedup.add(phrase)
    f.close()
    phrases_eff = OrderedDict(sorted(filter(lambda (k, v): k not in dedup, phrases_eff.items())))
    phrases_eff_keys = phrases_eff.keys()
    num_phrases_eff = len(phrases_eff)
    print 'effective phrases ({}): '.format(num_phrases_eff)
    print phrases_eff
    print ''

  # print top terms/phrases
  if enable_term:
    vocab_eff_rvs = sorted(vocab_eff.iteritems(), key=operator.itemgetter(1), reverse=True)
    print 'top {} out of {} terms'.format(print_top, num_vocab_eff)
    for i in range(1, print_top + 1):
      print vocab_eff_rvs[i]

  if enable_phrase:
    phrases_eff_rvs = sorted(phrases_eff.iteritems(), key=operator.itemgetter(1), reverse=True)
    print '\ntop {} out of {} phrases'.format(print_top, num_phrases_eff)
    for i in range(1, print_top + 1):
      print phrases_eff_rvs[i]

  # generate term:freq matrix
  tffile = open('termfreq.txt', 'w')
  for docid in range(1, len(docs) + (len(docs[len(docs)]) > 0)):
    tflist = ''
    tfnum = 0
    for term in docs[docid]:
      if enable_term:
        if term in vocab_eff:
          tflist += ' ' + str(vocab_eff_keys.index(term)) + ':' + str(docs[docid][term])
          tfnum += 1
      if enable_phrase:
        if term in phrases_eff:
          tflist += ' ' + str(phrases_eff_keys.index(term) + num_vocab_eff) + ':' + str(docs[docid][term])
          tfnum += 1
    if tfnum > 0:
      tffile.write(str(tfnum) + tflist + '\n')
  tffile.close()

  # generate dictionary
  dicfile = open('dictionary.txt', 'w')
  if enable_term:
    for term in vocab_eff:
      dicfile.write('\"' + term + '\"\n')
  if enable_phrase:
    for term in phrases_eff:
      dicfile.write('\"' + term + '\"\n')
  dicfile.close()

  # generate docmap
  dmfile = open('docmap.txt', 'w')
  for docid in range(1, len(docs) + (len(docs[len(docs)]) > 0)):
    dmfile.write('doc' + str(docid) + '\n');
  dmfile.close()

if  __name__ =='__main__':main()
