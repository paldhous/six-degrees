When updating these files, you must clean the name (vertex) and advises (edge) files:
1. Remove the last two lines, which are a listing of how many lines there are and a blank line, from both files.
2. Go in and find Pierre Curie in the names file, then remove the extra space at the end of his first name. I tried to do this with a script, but to no avail for some reason which is not terribly important. (May not even be necessary after all, the script might work.)
Once you've done that:
3. Open the names file, read the maximum index number off the last entry, and throw that into network_everyone.py as the variable NODES.
4. Go run the Python files, as indicated in PYTHON_README.TXT

(Yes, this could be done programmatically, but we had to get it out the door fast, and now it's not worth bothering with.)