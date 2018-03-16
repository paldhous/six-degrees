# coding=UTF-8

# Code written by Adam Becker
# adam@freelanceastro.com
#
# Last modified 2013-07-29

from __future__ import division
import csv
import igraph
from cPickle import UnpicklingError
from itertools import combinations # HELL YEAH ITERTOOLS!
import json

# Maximum index number.
# NOT the number of nodes!
NODES = 174609

# Load the graph, if it's there.
g_dir = igraph.Graph.Read("math_genealogy_directed.pickle")
g = igraph.Graph.Read("math_genealogy_undirected.pickle")
print "Done loading graph!"

# Load our list of famous names!
famous_file = open("../csv/famous_names.tsv", "r")
famous_reader = csv.DictReader(famous_file, delimiter = "\t")
famous_names = []
for name in famous_reader:
    famous_names.append(name["names"])

print "Done loading famous names!"

# Define a few handy-dandy functions.
def distance(name1, name2): 
    '''
    Returns the distance between two people, including those people.
    (So the minimum distance between two distinct people is 2.)
    '''
    return len(g.get_shortest_paths(name1, name2)[0])


def path(name1, name2):
    '''
    Returns the actual path between two people, names and all.
    '''
    route = g.get_shortest_paths(name1, name2)
    result = []
    for node in route[0]:
        name = g.vs[node]["name"]
        result.append(name.decode("utf-8"))
    return result

def id(name):
    '''
    Returns the id number given a name.
    ''' 
    return g.vs["name"].index(name)


# Append an attribute to all vertices of famous people.
# Using "0 and 1 rather than False and True so JavaScript can read this later on.
g_dir.vs["famous"] = 0
# g.vs["famous"] = 0
for name in famous_names:
    # g.vs[name]["famous"] = 1
    g_dir.vs[id(name)]["famous"] = 1


def neighbors(name, depth = 1):
    '''
    Returns neighbors of the given person, down to the given depth.
    Includes the original person, since that's depth zero.
    '''
    i = 0
    all_neighbors = {name}
    old_neighbors = {name}
    while i < depth:
        new_neighbors = set()
        for person in old_neighbors:
            neighbors = set(g.neighbors(person))
            new_neighbors |= neighbors
        new_neighbors -= all_neighbors          # make sure there are no duplicates, to avoid an infinite loop
        all_neighbors |= new_neighbors          # add them to the list
        old_neighbors = new_neighbors.copy()    # what was once new is old again
        i += 1
    return all_neighbors

kummer_set = {"Ernst Kummer"}

# Get Kummer's two-degree network as a subgraph, and save it.
kummer_total_set = set()
for name in kummer_set:
    neighbor_set = neighbors(name, depth = 2)
    kummer_total_set |= neighbor_set
    print "Processing..." + name.decode("utf-8") + "..."

print len(kummer_total_set)

kummer_total_list = list(kummer_total_set)
kummer_network = g_dir.subgraph(kummer_total_list)
print len(kummer_network.vs)
# hawking_network.save("hawking_network.gml")

# Putting Hawking in focus for JavaScript.
kummer_network.vs["focus"] = 0
filter(lambda n: n["name"] == "Ernst Kummer", kummer_network.vs)[0]["focus"] = 1

def graph_to_dict(g):
    '''
    Does what it says on the tin.
    Turns the graph into a dict with two entries: nodes and links.
    Each of those is a list, and the entries in the lists are themselves dicts.
    The nodes carry name, id, famous, and focus properties.
    '''
    # Create list of nodes-as-dicts.
    nodes = []
    for node in g.vs:
        d = {}
        d["name"] = node["name"]
        d["id"] = node.index
        d["famous"] = node["famous"]
        d["focus"] = node["focus"]
        nodes.append(d)
    print len(nodes)
    
    links = []
    for edge in g.es:
        d = {}
        d["source"] = edge.source
        d["target"] = edge.target
        links.append(d)
    
    result = {"nodes":nodes, "links":links}
    return result

kummer_dict = graph_to_dict(kummer_network)

f = open("kummer.json", "w")
json.dump(kummer_dict, f)
f.close()