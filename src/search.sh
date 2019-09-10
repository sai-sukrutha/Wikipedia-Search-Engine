#!/bin/bash
#!/usr/bin/env python
# $bash search.sh <path_to_index> <path_to_inputfile> <path_to_outputfile>
if [[ $# -eq 3 ]]
then
    index_path=$1       #File
    input_path=$2
    output_path=$3
    python3 searching.py $index_path $input_path $output_path
else
    echo "Error:Syntax: bash search.sh <path_to_index> <path_to_inputfile> <path_to_outputfile>"
fi
