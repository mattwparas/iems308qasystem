
import ast
import re
import datetime
from dateutil import parser

import numpy as np
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, query
from nltk import tag, tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
# from typing import List, Tuple
import string
# from string import maketrans
import pandas as pd

from nltk.corpus import stopwords
import os


# load corpus
# articles
articles = pd.read_csv("articles.csv")
list_of_articles = [ast.literal_eval(x) for x in articles['Article'].values]


# Connect to Elasticsearch -- must be running on localhost:9200
elastic = Elasticsearch()
if not elastic.indices.exists(index = "articles"):
    elastic.indices.create(index = "articles")

def build_elastic(day_index, article_index, sentences):
    date = datetime.date(2013, 1, 1) + datetime.timedelta(day_index)
    article_body = " ".join(sentences)
    article_id = "{}.{}".format(day_index, article_index)
    document_info = {
        "body" : article_body,
        "date" : date,
        "month" : date.month,
        "year" : date.year
    }
    
    output_json = {
        "_index" : "articles",
        "_type" : "article",
        "_id" : article_id,
        "_source" : document_info   
    }
    return output_json


db_dump = []
for date_index, date in enumerate(list_of_articles):
    for article_index, article in enumerate(date):
        db_dump.append(build_elastic(date_index, article_index, article))
        
helpers.bulk(elastic, db_dump)


def classify_question(question):  
    question = question.lower()
    # bankrupt -> Type 1
    if "bankrupt" in question:
        return 1
    # What affects GDP -> Type 2
    if "affect" in question and "gdp" in question:
        return 2
    # CEO -> Type 3
    if "ceo" in question:
        return 3
    # followup question -> Type 4?
    return 4


def parse_type_1(question):
    question = question.lower()
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    years = ["2013", "2014"]
    split_question = question.split(' ')
    for index, word in enumerate(months):
        if word in question:
            found_month = (index, word)
    
    for index, word in enumerate(years):
        if word in question:
            found_year = (index, word)
    
    bankrupt = ' '.join(["bankrupt", "bankruptcy"])
    
    # Write all queries
    matching_bankrupt = query.Q("query_string", query = bankrupt)
    matching_month = query.Q("match", month = found_month[0])
    matching_year = query.Q("match", year = int(found_year[1]))
    return matching_bankrupt + matching_month + matching_year


def parse_type_2(question):
    question = question.lower()
    gdp = "GDP"
    affect_list = ["affects", "affect", "effects", "effect"]
    affect_string = ' '.join(affect_list)
    return query.Q("query_string", query = gdp) + query.Q("query_string", query = affect_string)


def parse_type_3(question):
    question = question.split(' ')
    ceo = ["CEO"]
    if "company" in question:
        company = question[question.index("company")+1:]
    else:
        if "of" in question:
            company = question[question.index("of")+1:]
    company = [x.replace('?', '') for x in company]
    output_list = ceo + company
    and_string = ' AND '.join(output_list)
    return query.Q("query_string", query = and_string)

def parse_type_4(question):
    # find words after select keywords
    prepositions = ["is", "from", "with", "about", "above", "by", "for", "in"]
    punctuation = ['?', '.', '!']
    # identify property after prepositions
    found_prepositions = []
    for index, word in enumerate(question.split(' ')):
        if word in prepositions:
            found_prepositions.append(index)
    if found_prepositions:
        last_preposition = found_prepositions.pop()
    if last_preposition:
        selected_property = ' '.join(question.split(' ')[last_preposition + 1:])
        for punct in punctuation:
            if punct in selected_property:
                selected_property = selected_property.replace(punct, '')
    
    search_strings = selected_property + " GDP"
    group1 = ' AND '.join(search_strings.split(' '))
    
    associated_words = "affect affects effect effects fall high low increase decrease rise drop"
    
    return query.Q("query_string", query = group1) + query.Q("query_string", query = associated_words)


stop_words = set(stopwords.words("english"))
def remove_stop_words(big_string):
    return " ".join([x for x in big_string.split(' ') if x.lower not in stop_words])


# search for the top 50 results using elastic search
def search_for_query(es_query):
    search_using_elastic = Search(using = elastic, index = "articles")
    query_search = search_using_elastic.query(es_query)[:50]
    return query_search.execute()


from find_percentages import find_percentages
import find_ceos as fc
from find_companies import find_potential_companies


def parse_type_1_results(results):
    # what company went bankrupt in march of 2013
    found_sentences = []
    for article in results.hits:
        list_of_sentences = tokenize.sent_tokenize(article.body)
        gdp_sentences = [x for x in list_of_sentences if "bankrupt" in x.lower()]
        found_sentences += gdp_sentences
    
    found_companies = find_potential_companies(found_sentences)
    most_common = pd.Series(found_companies).value_counts().index[0]
    
    return most_common

def parse_type_2_results(results):   
    # what factors affect GDP
    articles = [x.body for x in results.hits]
    articles = [remove_stop_words(x) for x in articles]
    tf_vectorizer = TfidfVectorizer(ngram_range = (1, 2))
    tfidf_scores = tf_vectorizer.fit_transform(articles)
    sum_frequencies = np.sum(tfidf_scores, axis = 0)
    # get the top 20 words
    words = np.array(tf_vectorizer.get_feature_names())[np.argsort(sum_frequencies)[:, -50:]]
    no_stop_words = [x for x in words[0] if x not in stop_words]
    return no_stop_words

def parse_type_3_results(results):
    # CEO of what company
    found_sentences = []
    for article in results.hits:
        list_of_sentences = tokenize.sent_tokenize(article.body)
        gdp_sentences = [x for x in list_of_sentences if "ceo" in x.lower()]
        found_sentences += gdp_sentences
    
    potential_ceos = fc.find_ceo_matches(found_sentences)
    most_common = pd.Series(potential_ceos).value_counts().index[0]
    return most_common


def parse_type_4_results(results):
    # what percentage drop is associated with property
    found_sentences = []
    for article in results.hits:
        list_of_sentences = tokenize.sent_tokenize(article.body)
        gdp_sentences = [x for x in list_of_sentences if "gdp" in x.lower()]
        found_sentences += gdp_sentences
    
    found_percents = [find_percentages(x) for x in found_sentences]
    flat_list = [item for sublist in found_percents for item in sublist]
    most_common = pd.Series(flat_list).value_counts().index[0]
    return most_common



def classify_and_parse_question(question):
    classification = classify_question(question)
    if classification == 1:
        query1 = parse_type_1(question)
        results = search_for_query(query1)
        parsed_results = parse_type_1_results(results)
        return parsed_results
    if classification == 2:
        query2 = parse_type_2(question)
        results = search_for_query(query2)
        parsed_results = parse_type_2_results(results)
        return parsed_results
    if classification == 3:
        query3 = parse_type_3(question)
        results = search_for_query(query3)
        parsed_results = parse_type_3_results(results)
        return parsed_results
    if classification == 4:
        query4 = parse_type_4(question)
        results = search_for_query(query4)
        parsed_results = parse_type_4_results(results)
        return parsed_results



os.system('clear')
print("#############################################")
print("##WELCOME TO QA SYSTEM IEMS 308 VERSION 1.0##")
print("-----Source code at github.com/mattwparas----")
print("#############################################")
print("\n")


while(True):
    new_question = input("Enter a question:")
    try:
        print(classify_and_parse_question(new_question))
    except:
        print("No response found. Sorry! ")
    print('\n')













