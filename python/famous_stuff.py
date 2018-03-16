# Code written by Adam Becker
# adam@freelanceastro.com

from __future__ import division
import csv
import json

famous_file = open("../csv/famous_names.tsv", "r")
famous_reader = csv.DictReader(famous_file, delimiter = "\t")
famous_names = []
for name in famous_reader:
    famous_names.append(name)
famous_file.close()

# famous_dict = {"famous":famous_names}
print "Dumping everything into a JSON"
f = open("../json/famous.json", "w")
# json.dump(famous_dict, f)
json.dump(famous_names, f)
f.close()

highlighted_file = open("../csv/highlighted_names.tsv", "r")
highlighted_reader = csv.DictReader(highlighted_file, delimiter = "\t")
highlighted_names = []
for name in highlighted_reader:
    highlighted_names.append(name)
highlighted_file.close()

print "Dumping everything into a JSON"
f = open("../json/highlighted.json", "w")
json.dump(highlighted_names, f)
f.close()