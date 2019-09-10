#!/bin/bash
#!/usr/bin/env python
# $bash search.sh <path_to_index> <path_to_inputfile> <path_to_outputfile>
if [[ $# -eq 1 ]]
then
    index_path=$1       #Folder
    python3 searching.py $index_path
else
    echo "Error:Syntax: bash search.sh <path_to_index>"
fi