# coding: utf-8

# Code written by Adam Becker
# adam@freelanceastro.com

from __future__ import division
import csv
import igraph
from cPickle import UnpicklingError

# Maximum index number.
# NOT the number of nodes!
NODES = 174609

# Load the graph.
g_dir = igraph.Graph.Read("math_genealogy_directed.pickle")
g = igraph.Graph.Read("math_genealogy_undirected.pickle")
print "Done loading graph!"

# Load our list of famous names!
famous_file = open("../csv/famous_names_raw.tsv", "r")
famous_reader = csv.DictReader(famous_file, delimiter = "\t")
# famous_names = []
# for name in famous_reader:
#     famous_names.append(name["firstname"] + " " + name["lastname"])
famous_names = [name for name in famous_reader]
famous_file.close()

# Load our list of highlighted names!
highlighted_file = open("../csv/highlighted_names_raw.tsv", "r")
highlighted_reader = csv.DictReader(highlighted_file, delimiter = "\t")
# highlighted_names = []
# for name in highlighted_reader:
#     highlighted_names.append(name["firstname"] + " " + name["lastname"])
highlighted_names = [name for name in highlighted_reader]
highlighted_file.close()

print "Done loading famous and highlighted names!"

def id(name):
    '''
    Returns the id number given a name.
    ''' 
    return g.vs["name"].index(name)

def lastid(name):
    '''
    Returns the id number given a name.
    ''' 
    return g.vs["name"][::-1].index(name)

def duplicates(name):
    node1 = g.vs[id(name)]
    node2 = g.vs[::-1][lastid(name)]
    return node1.index != node2.index

print highlighted_names
print famous_names

# Finding the indices of famous people.
for person in famous_names: 
    name = person["firstname"] + " " + person["lastname"]
    vertex = g.vs[id(name)]
    if duplicates(name):
        print name
    person["id"] = vertex.index

# Finding the indices of highlighted people.
for person in highlighted_names:
    name = person["firstname"] + " " + person["lastname"]
    vertex = g.vs[id(name)]
    if duplicates(name):
        print name
    person["id"] = vertex.index

# Putting in the notable people with duplicates (other people with the same name) in the network
duplicated_highlights = []
duplicated_highlights.append({"firstname": "Kenneth", "lastname":"Wilson", "id":22937})
duplicated_highlights.append({"firstname": "David", "lastname":"Gross", "id":80901})
duplicated_highlights.append({"firstname": "John", "lastname":"Conway", "id":18849})

f = open("../csv/highlighted_names.tsv", "w")
w = csv.DictWriter(f, ["firstname", "lastname", "id"], delimiter = "\t")
w.writeheader()
w.writerows(highlighted_names)
w.writerows(duplicated_highlights)
f.close()

f = open("../csv/famous_names.tsv", "w")
w = csv.DictWriter(f, ["firstname", "lastname", "blurb", "picture_file", "id"], delimiter = "\t")
w.writeheader()
w.writerows(famous_names)
f.close()