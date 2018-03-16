# Code written by Adam Becker
# adam@freelanceastro.com

from __future__ import division
import csv
import igraph
from cPickle import UnpicklingError
import json
# from network_everyone import graph_to_dict

# Hawking's id in the database.
hawking_id = 78459

# Load the graph, if it's there.
# Otherwise, prompt the user to build it.
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
famous_names = [int(name["id"]) for name in famous_reader]
famous_file.close()

# Load our list of highlighted names!
highlighted_file = open("../csv/highlighted_names.tsv", "r")
highlighted_reader = csv.DictReader(highlighted_file, delimiter = "\t")
highlighted_names = [int(name["id"]) for name in highlighted_reader]
highlighted_file.close()

print "Done loading famous and highlighted names!"

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
    Returns the index number given a name.
    ''' 
    return g_dir.vs["name"].index(name)

def ind(id):
    '''
    Returns the index number given an id.
    ''' 
    return g_dir.vs["id"].index(id)

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

# Append an attribute to all vertices of famous people.
# Using 0 and 1 rather than False and True so JavaScript can read this later on.
g_dir.vs["famous"] = 0
for id in famous_names:
    index = g_dir.vs["id"].index(id)
    g_dir.vs[index]["famous"] = 1

# Append an attribute to all vertices of highlighted people.
# Using 0 and 1 rather than False and True so JavaScript can read this later on.
g_dir.vs["highlighted"] = 0
for id in highlighted_names:
    index = g_dir.vs["id"].index(id)
    g_dir.vs[index]["highlighted"] = 1

# Putting Hawking in focus for JavaScript.
g_dir.vs["focus"] = 0
g_dir.vs[ind(hawking_id)]["focus"] = 1

# Figure out who's connected by less than n.
n = 4

famous_set = set(famous_names)

# Get the famous list's three-degree network as a subgraph, and save it.
small_set = set([name for name in famous_set])
for i in famous_set:
    neighbor_set = neighbors(i, depth = n-1)
    small_set |= neighbor_set
    # print "Processing..." + name.decode("utf-8") + "..."

small_list = [ind(i) for i in small_set]
small_network = g_dir.subgraph(small_list)
print len(small_network.vs)

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
        
        # Weeding out bad beginnings of names.
        if node["name"][:7] == '''&nbsp; ''':
            print node["name"].decode("utf-8")
            d["name"] = node["name"][7:]
        elif node["name"][:4] == "Sir ":
            print node["name"].decode("utf-8")
            d["name"] = node["name"][4:]
        elif node["name"][:8] == "Pierre  ":
            print node["name"].decode("utf-8")
            d["name"] = node["name"][:7] + node["name"][8:]
            print d["name"].decode("utf-8")
        else:
            d["name"] = node["name"]
            
        # Weeding out bad endings to names.
        if d["name"][-5:] == ", FRS":
            d["name"] = d["name"][:-5]
            print d["name"]
        if d["name"][-4:] == " FRS":
            d["name"] = d["name"][:-4]
            print d["name"]
        if d["name"][-4:] == " OBE":
            print d["name"]
            d["name"] = d["name"][:-4]
        if d["name"][-5:] == ", OBE":
            print d["name"]
            d["name"] = d["name"][:-5]
        elif d["name"][-5:] == ", PhD":
            print d["name"]
            d["name"] = d["name"][:-5]
        elif d["name"][-7:] == ", Ph.D.":
            print d["name"]
            d["name"] = d["name"][:-7]            
        elif d["name"][-5:] == ", PHD":
            print d["name"]
            d["name"] = d["name"][:-5]
        elif d["name"][-7:] == " &nbsp;":
            print d["name"]
            d["name"] = d["name"][:-7]
        elif d["name"][-6:] == "&nbsp;":
            print d["name"]
            d["name"] = d["name"][:-6]       
        
        d["id"] = node["id"]
        d["famous"] = node["famous"]
        d["highlighted"] = node["highlighted"]
        d["focus"] = node["focus"]
        d["distance"] = node["distance"]
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

small_dict = graph_to_dict(small_network)

f = open("../json/small.json", "w")
json.dump(small_dict, f)
f.close()