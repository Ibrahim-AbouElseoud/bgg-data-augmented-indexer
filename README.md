# bgg-data-augmented-indexer
Index your group's collection into a csv with data collected from BoardGameGeek.com. Input is a csv with your game titles and it will do the rest getting the data

If the game name is not found directly in the website then the script will use the name to search in the BGG website and gets the closest result using jaro_winkler_similarity.

## How to run

1. Have python 3 installed
2. `pip install -r requirements.txt`
3. Have a csv file with columns: Game, Owned by
4. Be in the directory of the script with a cmd and type `python bgg_csv_indexer.py`
5. When prompted for the csv path input the relative path of the file or the absolute path without quotation
6. The output is generated in the same directory of the script under the name boardgames_indexed.csv

## How to run with exe

1. Double click exe 
2. Input the path of the input csv file without double quotes
3. The output is generated in the same directory of the executable under the name boardgames_indexed.csv

Note: if running the exe and it closes before completion, then open a console in the location of the exe and type bgg_csv_indexer.exe and it will run normally until it finishes.

[Download Exe from here](https://github.com/Ibrahim-AbouElseoud/bgg-data-augmented-indexer/releases)

There is a sample input and output csvs in the repository you can take a look to have an idea of the input and output.
