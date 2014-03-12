# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 11:54:48 2014

@author: fnavarro
"""

import json
import os
import argparse
from booklibraryfactory import bookLibraryFactory

libraries = bookLibraryFactory.libraries

basedir = "/home/taux"

def main():

    site = "itebooks"
    
    if site in libraries.keys():
        # Here the strategy instantiation that will be in use for commands later
        # Wouldnt this be better using some kind of factory DP???
        #library = libraries[args.site](os.path.join(basedir,args.site))
        library = bookLibraryFactory().createLibrary(
                    site, 
                    os.path.join(basedir,site))
    else:
        sys.stderr.write("%s site unknown" % args.site)

    library._load_bookdb()
    for idx,book in library._bookdb.items():
        #print idx,book
        short_filename = book["short-title"]
        title = book["title"]
        old_filename = "%s_%s.PDF" % (idx[3:], short_filename)
        new_filename = "%s_%s.pdf" % (idx, library._shortify(title))
        old_filepath = os.path.join(library.homeDir, library.booksDir, old_filename)
        new_filepath = os.path.join(library.homeDir, library.booksDir, new_filename)        
        #print old_filepath 
        #print new_filepath 
        #print                   
        if os.access(old_filepath, os.F_OK):
            os.rename(old_filepath, new_filepath)
            #print old_filepath 
            #print new_filepath 
            
if __name__ == "__main__":
    main()