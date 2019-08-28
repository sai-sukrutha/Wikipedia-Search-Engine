# Mini-Wikipedia-Search-Engine
A Search Engine using minimized wikipedia data dump 

Commands to run
bash index.sh <path_to_data> <folder_to_create_index>
bash search.sh <path_index_file> <queries_input> <queries_output>

Example:
bash index.sh ../data/data.xml ./index/
bash search.sh ./index/my_index.pkl ../queries/sample_queryfile ../queries/sample_output
