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
from network_everyone import graph_to_dict

# Maximum index number.
# NOT the number of nodes!
NODES = 174609

# Load the reduced graph, if it's there.
# Otherwise, build it from the whole graph.
try:
    g_dir = igraph.Graph.Read("hawking_genealogy_directed.pickle")
    g = igraph.Graph.Read("hawking_genealogy_undirected.pickle")
    print "Done loading graph!"
except UnpicklingError:
    # Load the whole graph.
    g_dir = igraph.Graph.Read("math_genealogy_directed.pickle")
    g = igraph.Graph.Read("math_genealogy_undirected.pickle")
    print "Done loading whole graph!"
    
    # # Initialize the graph.
    # # We want the index numbers from the database to line up with the indices of the nodes, 
    # # which means we need NODES + 1 nodes, since igraph (sensibly) starts counting at zero.
    # g_dir = igraph.Graph(NODES+1, directed = True)
    # 
    # # Load in the edges.
    # edge_file = open("../csv/advises_clean.tsv", "r")
    # # edge_reader = csv.reader(edge_file, delimiter="\t") # tab-separated entries
    # edge_reader = csv.DictReader(edge_file, delimiter = "\t")
    # 
    # def edge_adder(edge):
    #     '''
    #     Given an edge in the form of an advisor/advisee dictionary, 
    #     converts it into an edge that igraph can read and adds it to the graph.
    #     We'll be feeding this to the multiprocessing pool.
    #     '''
    #     n1 = int(edge["advisor"])
    #     n2 = int(edge["advisee"])
    #     return (n1, n2)
    # 
    # edges = map(edge_adder, edge_reader)
    # # Turns out that it's *much* faster to add many edges at once than it is to add them one by one.
    # g_dir.add_edges(edges)
    #     
    # print "Done adding edges!"
    # 
    # # Load in the names.
    # name_file = open("../csv/names_clean.tsv", "r")
    # name_reader = csv.DictReader(name_file, delimiter = "\t")
    # 
    # # Put the names into the graph.
    # for entry in name_reader:
    #     node = g_dir.vs[int(entry["academic_id"])]
    #     node["name"] = entry["given_name"] + " " + entry["family_name"]

    print "Done adding names!"
    
    g_dir.save("hawking_genealogy_directed.pickle")
    
    print "Done saving graph!"
    
    g = g_dir.as_undirected()
    g.save("hawking_genealogy_undirected.pickle")
    
    print "Done saving undirected graph!"

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

# Figure out who's connected by less than n.
n = 4

famous_set = set(famous_names)
hawking_set = {"Stephen Hawking"}
done = False
i = 0
while not done:
    new_set = set()
    for name in famous_set - hawking_set:
        for target in hawking_set:
            d = distance(name, target)
            if d <= n:
                new_set.add(name)
    if len(new_set - hawking_set) == 0:
        done = True
    else:
        # print i
        # i += 1
        # print new_set
        print "Processing..."
        hawking_set |= new_set

print "Within Hawking's three-degree network:"
hawking_list = u""
for name in hawking_set:
    hawking_list += name.decode("utf-8")
    hawking_list += ", "
print hawking_list[:-2]

debroglie_set = {"Louis de Broglie"}
done = False
i = 0
while not done:
    new_set = set()
    for name in famous_set - debroglie_set:
        for target in debroglie_set:
            d = distance(name, target)
            if d <= n:
                new_set.add(name)
    if len(new_set - debroglie_set) == 0:
        done = True
    else:
        # print i
        # i += 1
        # print new_set
        print "Processing..."
        debroglie_set |= new_set

print "Within de Broglie's three-degree network:"
debroglie_list = u""
for name in debroglie_set:
    debroglie_list += name.decode("utf-8")
    debroglie_list += ", "
print debroglie_list[:-2]

everyone_else = famous_set - hawking_set - debroglie_set
close_connections = []
for pair in combinations(everyone_else, 2):
    d = distance(pair[0], pair[1])
    if d <= n and d > 1:
        close_connections.append(pair)

print close_connections

print "Everyone else:"
not_hawking_list = u""
for name in everyone_else:
    not_hawking_list += name.decode("utf-8")
    not_hawking_list += ", "
print not_hawking_list[:-2]

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

# Get Hawking's three-degree network as a subgraph, and save it.
hawking_total_set = set([id(name) for name in hawking_set])
for name in hawking_set:
    neighbor_set = neighbors(name, depth = 3)
    hawking_total_set |= neighbor_set
    print "Processing..." + name.decode("utf-8") + "..."

print len(hawking_total_set)

hawking_total_list = list(hawking_total_set)
hawking_network = g_dir.subgraph(hawking_total_list)
print len(hawking_network.vs)
# hawking_network.save("hawking_network.gml")

# Putting Hawking in focus for JavaScript.
hawking_network.vs["focus"] = 0
filter(lambda n: n["name"] == "Stephen Hawking", hawking_network.vs)[0]["focus"] = 1

# def graph_to_dict(g):
#     '''
#     Does what it says on the tin.
#     Turns the graph into a dict with two entries: nodes and links.
#     Each of those is a list, and the entries in the lists are themselves dicts.
#     The nodes carry name, id, famous, and focus properties.
#     '''
#     # Create list of nodes-as-dicts.
#     nodes = []
#     for node in g.vs:
#         d = {}
#         d["name"] = node["name"]
#         d["id"] = node.index
#         d["famous"] = node["famous"]
#         d["focus"] = node["focus"]
#         nodes.append(d)
#     print len(nodes)
#     
#     links = []
#     for edge in g.es:
#         d = {}
#         d["source"] = edge.source
#         d["target"] = edge.target
#         links.append(d)
#     
#     result = {"nodes":nodes, "links":links}
#     return result

hawking_dict = graph_to_dict(hawking_network)

f = open("hawking.json", "w")
json.dump(hawking_dict, f)
f.close()