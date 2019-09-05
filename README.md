# Mini-Wikipedia-Search-Engine
A Search Engine using minimized wikipedia data dump 

Commands to run

bash index.sh <path_to_data> <folder_to_create_index>

bash search.sh <path_index_folder> <queries_input_file> <queries_output_file>


Example:

bash index.sh ../data/data.xml ../index/

bash search.sh ../index/ ../queries/sample_queryfile ../queries/sample_output.txt
