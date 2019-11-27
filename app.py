# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 21:56:42 2019

@author: ZEESHAN
"""

from flask import render_template, url_for, flash, redirect, request, Flask
#from flask_login import login_user, current_user, logout_user, login_required
from os import listdir
from os.path import isdir
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import os
import stripe
from jinja2 import Template

stripe_keys = {
  'secret_key': 'sk_test_kM99QDFhfnOgWyrNIgMe0MvZ00BeqrtFZa',
  'publish_key':'pk_test_snsvSTrxjwY9oA9Gmrt5Vn6P00UkJlLMSd'
}

stripe.api_key = stripe_keys['secret_key']


def read_article(items):
    linedata=items
    ll=''
    for line in linedata:
      ll=ll+" "+line.strip()
    article=ll.split(". ")
    sentences = []

    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # Vector creation for sentence 1
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # Vector creation for sentence 2
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(items, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text & split it
    sentences =  read_article(items)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
    print("Indexes of top ranked_sentence order are ", ranked_sentence)

    if(top_n<len(ranked_sentence)):
      for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))
    else:
      for i in range(len(ranked_sentence)):
        summarize_text.append(" ".join(ranked_sentence[i][1]))
    # Step 5 - output the summarize text
    print("Summarize Text: \n", ". ".join(summarize_text))
    return(summarize_text)

app=Flask(__name__)


@app.route('/')
def index():
    print("test",stripe_keys['publish_key'])
    return render_template('index.html',p_key=stripe_keys['publish_key'])

@app.route('/home')
def home():
    print("test",stripe_keys['publish_key'])
    return render_template('index.html',p_key=stripe_keys['publish_key'])


@app.route('/payment', methods=['POST'])
def payment():
    
    amount = 100
    print(request.form['stripeToken'])
    stripe.Charge.create(     
    amount=amount,
    currency='usd',
    card=request.form['stripeToken'],
    description='Essay Shrinkr Thanks'
    )

    return render_template('thankyou.html')

@app.route('/submit',methods=['POST'])
def submit():
    itemList = request.form['tarea']
    items = itemList.split("\n")
    outs=generate_summary(items, 10)
    oo=''
    for l in outs:
        oo=oo+l
    print("Zee",oo)
    return render_template('index.html',output=oo,inp=itemList,p_key=stripe_keys['publish_key'])
    # split the text to get each line in a list
    #text2 = text.split('\n')

    #Lister=request.form['tarea']
    #items=Lister.split("\n")
    #print(text2)

    #Generate Summary
    #generate_summary( text2, 10)
    
    #return render_template(index.html,output="What's up zeesh")

if __name__=='__main__':
    app.run()
