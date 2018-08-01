#!/bin/env python3
'''
Document:
	if error at here:
		model=api.load("glove-twitter-25")
	copy my ~/gensim-data/ to your ~
'''
word_list_path="/mnt/share/ky/Aesthetic-Painting/word_list.txt"
match_count=3
result_pattern='[%.6f,%.6f]'

print('launch gensim')
import gensim.downloader as api
print('load model: '+"glove-twitter-25")
model=api.load("glove-twitter-25") #if error here, copy my ~/gensim-data/ to your ~
word_dict={}
word_list=[]
print('load words: '+word_list_path)
with open(word_list_path) as fin:
	for line in fin.readlines():
		word,x,y=line.split()
		x,y=float(x),float(y)
		word_dict[word]=(x,y)
		try:
			model.word_vec(word)
			word_list+=[word]
		except KeyError:
			pass
			#print('drop word: '+word)

def do_match(word):
	if word in word_dict:
		return result_pattern%word_dict[word]
	
	try:
		word_dist=model.distances(word,word_list)
	except KeyError:
		return result_pattern%(0,0)
	
	assert len(word_dist)==len(word_list)
	neighbors=[]
	for i in range(len(word_dist)):
		index=len(neighbors)
		while index>0 and word_dist[i]<neighbors[index-1][1]:
			index-=1
		if index<match_count:
			neighbors.insert(index,(word_list[i],word_dist[i]))
		if len(neighbors)>=match_count:
			del neighbors[match_count:]
	x,y=0.0,0.0
	for word,dist in neighbors:
		wx,wy=word_dict[word]
		x,y=x+wx,y+wy
	x,y=x/len(neighbors),y/len(neighbors)
	return result_pattern%(x,y)
