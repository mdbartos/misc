misc
====

Miscellaneous scripts and utilities.

----------


db_mash
----

db_mash is a simple utility that can import/export, and combine tabular datastructures. It can read csv, txt, dbf and xls files, and output the combined tables to a database (currently hdf5, pickle, or sqlite structures are supported). To use the script, start by instantiating the class. Only one parameter is required--the name of the database that you want to create. For example:

b = mash_db('phx')

The class 'mash_db' has ten functions:

+ import_csv: imports all csv and txt files from the current directory to pandas dataframes. Dataframes are stored in dictionary 'self.d'. Each dataframe is keyed by its file name (minus the extension).

+ import_xl: imports all .xls files from the current directory to pandas dataframes. Assumes that the .xls file is formatted as a simple table with headers in the first row.

+ import_dbf:imports all dbf files from the current directory to pandas dataframes. Dataframes are stored in dictionary 'self.d'.

+ enforce_types: this function ensures thatfor all tables in 'self.d', columns have only one type. This allows the dataframes to be exported to sqlite databases or hdf stores (and speeds up operations in general).  Warning: I haven't added support for datetime types yet.

+ make_specs: creates a dictionary 'self.spec_d' that holds the (sql-compatible) type for each field. The dictionary is used to create the database connection string.

+ build_tablestr: creates connection strings for each table using the keys and values in 'self.spec_d'. Connections strings are written to 'self.tablestr_d'.

+ make_conn: exports all dataframes from 'self.d' to an sqlite database (enforce_types, make_specs, and build_tablestr need to be run first). For the phoenix assessor database, make_conn took around 12-15 minutes on my machine.

+ make_db: combines the previous six steps into one function, allowing sqlite databases to be built in one step.*

+ save_pickle: writes the contents of 'self.d' to a pickle (binary file), which can be loaded at a later time. Can store basically anything, but it's big and slow to write.

+ save_hdf: writes the contents of 'self.d' to an hdf5 file, which can be loaded at a later time. Less flexible than pickle, but much better performance (fast read/write times, small size, etc.).

+ clear_mem: clears memory by initializing 'self.d', 'self.spec_d' and 'self.tablestr_d'.


Note that dataframes can be accessed directly using the 'self.d' dictionary. So let's assume that you already imported the 'parcels' table from the assessor database using the import_csv function.

If you want to access the dataframe 'parcels' from the assessor database, simply call it like you would a dictionary key. Using the instance 'b' of the mash_sqlite class shown above:


b.d['parcels']

^^(should return the pandas dataframe corresponding to the parcels table)

Thus, if you need to concatenate two dataframes together (as with the LA database), you can do it very easily using pandas:

b.d['dataframe'] = pandas.concat([b.d['dataframe1'],b.d['dataframe2'],b.d['dataframe3']], ignore_index=True)

^^ will append together all rows from dataframe1, dataframe2 and dataframe3 and save the concatenated table as a new dataframe in 'self.d'.

To build an sqlite database from scratch (assuming the required tables are in the current directory), you can simply type the following lines:

b = mash_db('phx')
b.make_db() 
