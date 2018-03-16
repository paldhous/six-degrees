# coding: utf-8

# Code written by Adam Becker
# adam@freelanceastro.com
# In the unlikely event that this is ever released publicly:
# it's likely that New Scientist owns copyright on this code,
# as much of it was written in 2013 when I was an employee of New Scientist,
# and it was written expressly for a project at New Scientist.
# Thus, much as it pains me, if New Scientist owns copyright, I have to say:
# (c) 2014 Reed Business Information, Inc. All Rights Reserved.
#
# HOWEVER!
# If, by some fluke, I do retain copyright on this code, then the following licensing applies:
# (c) 2014 Adam Becker
# This code is released under the MIT License, the full text of which can be found at:
# http://opensource.org/licenses/MIT

from __future__ import division
import csv
import igraph
from cPickle import UnpicklingError
import json
from multiprocessing import Pool # Multiprocessing FTW.

# Maximum index number.
# NOT the number of nodes!
NODES = 180300 # updated to reflect the files from MGP from the end of January, 2014.

# Hawking's id in the database.
hawking_id = 78459

# Define a necessary function.
def distance(g, name1, name2): 
    '''
    For a given graph g, returns the distance between two people, including those people.
    (So the minimum distance between two distinct people is 2.)
    name1 and name2 can be names or indices.
    '''
    return len(g.get_shortest_paths(name1, name2)[0])

# Load the graph, if it's there.
# Otherwise, build it from scratch.
try:
    g_dir = igraph.Graph.Read("math_genealogy_directed.pickle")
    g = igraph.Graph.Read("math_genealogy_undirected.pickle")
    print "Done loading graph!"
except UnpicklingError:
    # Initialize the graph.
    # We want the index numbers from the database to line up with the indices of the nodes, 
    # which means we need NODES + 1 nodes, since igraph (sensibly) starts counting at zero.
    g_dir = igraph.Graph(NODES+1, directed = True)

    # Load in the edges.
    # edge_file = open("../csv/advises_clean.tsv", "r")
    edge_file = open("../csv/advises.tsv", "r")    
    # edge_reader = csv.reader(edge_file, delimiter="\t") # tab-separated entries
    edge_reader = csv.DictReader(edge_file, delimiter = "\t")
    
    def edge_adder(edge):
        '''
        Given an edge in the form of an advisor/advisee dictionary, 
        converts it into an edge that igraph can read and adds it to the graph.
        We'll be feeding this to the multiprocessing pool.
        '''
        n1 = int(edge["advisor"])
        n2 = int(edge["advisee"])
        return (n1, n2)
    
    edges = map(edge_adder, edge_reader)
    # Turns out that it's *much* faster to add many edges at once than it is to add them one by one.
    g_dir.add_edges(edges)
        
    print "Done adding edges!"

    # Load in the names.
    # name_file = open("../csv/names_clean.tsv", "r")
    name_file = open("../csv/names.tsv", "r")
    name_reader = csv.DictReader(name_file, delimiter = "\t")

    # Put the names into the graph.
    for entry in name_reader:
        node = g_dir.vs[int(entry["academic_id"])]
        firstname = entry["given_name"]
        lastname = entry["family_name"]
        
        if firstname != " " and firstname != "":
            if (firstname[-1:] == " "):
                firstname = firstname[:-1]
            if (firstname[0] == " "):
                firstname = firstname[1:]
        else:
            firstname = False
        
        if lastname != " " and lastname != "":
            if (lastname[-1:] == " "):
                lastname = lastname[:-1]
            if (lastname[0] == " "):
                lastname = lastname[1:]
        else:
            lastname = False
        
        if firstname and lastname:
            node["name"] = firstname + " " + lastname
        elif lastname:
            node["name"] = lastname
        elif firstname:
            node["name"] = firstname
        else:
            node["name"] = ""

    print "Done adding names!"
    
    print "Calculating distance from Stephen Hawking for all nodes..."
    
    # Give every node a property called "id"
    # so we can keep track of people with duplicated names
    g_dir.vs["id"] = [v.index for v in g_dir.vs]
    
    # Get the undirected graph going.
    g = g_dir.as_undirected()
    
    # Figure out the distance to Hawking for every node.
    def hawkdist(id): return distance(g, hawking_id, id) - 1
    # The mapping function must be defined before the pool is created.
    p = Pool(processes = 7)
    # Multiprocessing can't handle lists of igraph vertices, for whatever reason.
    # So we'll give it a list of numbers instead.
    verts = [v.index for v in g.vs]
    distances = p.map(hawkdist, verts)
    g_dir.vs["distance"] = distances

    print "Done calculating distances from Hawking!"

    # # Filter out the people who are wholly disconnected from Hawking
    # connected_ids = [v.index for v in filter(lambda x: x["distance"] != -1, g_dir.vs)]
    # g_dir = g_dir.subgraph(connected_ids)
    
    # print "Done filtering out people disconnected from Hawking!"
    
    g_dir.save("math_genealogy_directed.pickle")
    
    print "Done saving graph!"
    
    g.save("math_genealogy_undirected.pickle")
    
    print "Done saving undirected graph!"

# A useful function.
def ind(id):
    '''
    Returns the index number given an id.
    ''' 
    return g_dir.vs["id"].index(id)

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

# Append an attribute to all vertices of famous people.
# Using 0 and 1 rather than False and True so JavaScript can read this later on.
g_dir.vs["famous"] = 0
for i in famous_names:
    g_dir.vs[ind(i)]["famous"] = 1

# Append an attribute to all vertices of highlighted people.
# Using 0 and 1 rather than False and True so JavaScript can read this later on.
g_dir.vs["highlighted"] = 0
for i in highlighted_names:
    g_dir.vs[ind(i)]["highlighted"] = 1
    
# Putting Hawking in focus for JavaScript.
g_dir.vs["focus"] = 0
g_dir.vs[ind(hawking_id)]["focus"] = 1

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
            # print node["name"].decode("utf-8")
            d["name"] = node["name"][7:]
        elif node["name"][:4] == "Sir ":
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
        if d["name"][-4:] == " FRS":
            d["name"] = d["name"][:-4]
        if d["name"][-4:] == " OBE":
            d["name"] = d["name"][:-4]
        if d["name"][-5:] == ", OBE":
            d["name"] = d["name"][:-5]
        elif d["name"][-5:] == ", PhD":
            d["name"] = d["name"][:-5]
        elif d["name"][-7:] == ", Ph.D.":
            d["name"] = d["name"][:-7]            
        elif d["name"][-5:] == ", PHD":
            d["name"] = d["name"][:-5]
        elif d["name"][-7:] == " &nbsp;":
            d["name"] = d["name"][:-7]
        elif d["name"][-6:] == "&nbsp;":
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

print "Dumping everything into a JSON"
everything_dict = graph_to_dict(g_dir)
f = open("../json/everything.json", "w")
json.dump(everything_dict, f)
f.close()