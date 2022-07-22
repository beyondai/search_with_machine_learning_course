import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv


# Proprocessing imports                                                                                                     
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string

ps = PorterStemmer()

def transform_queries(product_name):
    product_name = product_name.translate(str.maketrans('', '', string.punctuation)).lower()
    #tokens = word_tokenize(product_name) # slow. turn off during debugging. use spli() instead
    tokens = product_name.split()
    product_name = ' '.join([ps.stem(w) for w in tokens])
    return product_name

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data_1.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
#df['query'] = df['query'].str.lower()
df['query'] = df['query'].apply(transform_queries)
# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
def count_freq(df):
    return df.groupby('category', sort=False).count().rename(columns={"query": "freq"}).sort_values("freq")

MIN_FREQ = 1000
ROOT = 'cat00000'
i = 0

while (True):
    #DEBUG
    '''
    i += 1
    if i%100 == 0:
        print(i)
        print(freq)
    freq = count_freq(df)
    '''
    # avoid the root category
    f0, c0 = freq.iloc[0].freq, freq.iloc[0].name # least frequency and category
    f1, c1 = freq.iloc[1].freq, freq.iloc[1].name # least frequency and category
    (f, c) = (f0, c0) if c0 != ROOT else (f1, c1)
    if f > MIN_FREQ: # all categories >= minimum frequency requirement
        break
    p = parents_df[parents_df["category"] == c].iloc[0].parent #find parent category
    df.loc[df["category"] == c, 'category'] = p # roll it up

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
