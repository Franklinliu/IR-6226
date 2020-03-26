CI6226: Information Retrieval

README

This is an assignment of the course Information Retrieval. In this project, we've split it into 2 parts and worked incrementally to make a complete IR system.
The first part consisted of having a system that used an in-memory index using a trie. This system used concepts of TF-IDF to rank the documents and retrieved a fixed set of relevant documents.


#####################################

Steps to run the program:

1. Parse the input directory (HillaryEmails) by running ( should be in the folder)
	python emailparser.py						--> Outputs emaildataset.xml

2. Create the index file by running
	python indexCreator.py ./output/emaildataset.xml ./output/trieIndex.dat ./output/postingList.dat

where 	trieIndex.dat = name of index file to be generated
	postingList.dat = name of the output file to contain the posting list

3. Run the query on the created index by
	python documentRetriever.py ./output/trieIndex.dat
where trieIndex.dat = name of input index file
