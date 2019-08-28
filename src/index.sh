#!/bin/bash
#!/usr/bin/env python3
# $bash index.sh <path_to_data> <path_to_index>
if [[ $# -eq 2 ]]
then
    data_path=$1       #File
    index_path=$2      #Folder
    #echo $data_path
    #echo $index_path
    python3 indexer.py $data_path $index_path
else
    echo "Error:Syntax: bash index.sh <path_to_data> <path_to_index>"
fi
