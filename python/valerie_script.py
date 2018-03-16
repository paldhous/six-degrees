# Code written by Adam Becker
# adam@freelanceastro.com
#

from __future__ import division
import csv
import igraph
from cPickle import UnpicklingError

try:
    g_dir = igraph.Graph.Read("math_genealogy_directed.pickle")
    g = igraph.Graph.Read("math_genealogy_undirected.pickle")
    print "Done loading graph!"
except UnpicklingError:
    # Load the whole graph.
    print "Whoops! Looks like you need to build the total graph. Run network_everyone.py, then try running this again."


# Load our list of famous names!
famous_file = open("../csv/famous_names.tsv", "r")
famous_reader = csv.DictReader(famous_file, delimiter = "\t")
famous_names = []
for name in famous_reader:
    famous_names.append(name["firstname"] + " " + name["lastname"])
print "Done loading famous names!"

# Define a few handy-dandy functions.

def dir_distance(name1, name2): 
    '''
    Returns the DIRECTED distance between two people, including those people.
    (So the minimum distance between two distinct people is 2.)
    '''
    return len(g_dir.get_shortest_paths(name1, name2)[0])

def isAdvisorOf(name1, name2):
    '''
    A NON-SYMMETRIC FUNCTION.
    Tells you ONLY whether person 1 is the advisor of person 2.
    This function TELLS YOU NOTHING ABOUT THE REVERSE!
    '''
    return dir_distance(name1, name2) == 2

def node_path(name1, name2):
    '''
    Returns the actual path between two people, names and all.
    '''
    route = g.get_shortest_paths(name1, name2)
    # result = []
    # for node in route[0]:
    #     name = g.vs[node]["name"]
    #     result.append(name)
    # return result
    return route[0]

def named(node):
    '''Returns the name of a node.'''
    return g.vs[node]["name"].decode("utf-8")

def pretty_print_path(name1, name2):
    '''
    Returns the actual path between two people, names and all.
    Also returns the directions of the edges, i.e. whether it's a student-of or advisor-of relationship.
    '''
    nodes = node_path(name1, name2)
    bools = [isAdvisorOf(pair[0], pair[1]) for pair in zip(nodes[:-1], nodes[1:])]
    s = ''
    for n, b in zip(nodes[:-1], bools):
        s += named(n)
        if b:
            s += '''\n was the advisor of \n'''
        else:
            s += '''\n was the student of \n'''
    s += named(nodes[-1])
    return s


# Generate the lists Valerie wants!
for name in famous_names:
    if name == "Stephen Hawking":
        pass
    else:
        connection = pretty_print_path("Stephen Hawking", name)
        print connection
        print '''\n'''

