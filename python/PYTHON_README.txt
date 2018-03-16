When updating files, first update and clean the TSV files, as indicated in TSV_README.txt, then:
1. Trash the pickle files.
2. Run network_everyone.py (this will take a while, about 10-15 minutes on a MacBook Pro in 2014.)

##### UNNECESSARY UNLESS SOMETHING WEIRD IS GOING ON (e.g. a reindexing of old nodes) #######

3. Run famous_indices.py
4. Run famous_stuff.py


# NECESSARY ###
5. Run network_small.py