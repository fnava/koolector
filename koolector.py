# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 10:24:48 2014

@author: fnavarro
"""

import os
import argparse
from booklibraryfactory import bookLibraryFactory

# Will use strategy DP to decouple details from library collector
# details, will be handled by the strategy class "class"
#libraries = {
#    "itebooks":itebooks,
#    "genesis":genesis
#    }
libraries = bookLibraryFactory.libraries

basedir = "/home/taux"

def main():

    descr_msg = "ebooks web scraper and collector from:\n"  
    help_msg = ""
    for key,st in libraries.items():
        descr_msg += "   %s:\t%s \n" % (key, st.siteUrl)
        help_msg += "%s | " % key

    parser = argparse.ArgumentParser(description=descr_msg, 
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('site', help=help_msg[:-3])
    parser.add_argument('command', help="updatedb | download | status")                    
    
    args = parser.parse_args()
    
    if args.site in libraries.keys():
        # Here the strategy instantiation that will be in use for commands later
        # Wouldnt this be better using some kind of factory DP???
        #library = libraries[args.site](os.path.join(basedir,args.site))
        library = bookLibraryFactory().createLibrary(
                    args.site, 
                    os.path.join(basedir,args.site))
        library.command(args.command)
    else:
        sys.stderr.write("%s site unknown" % args.site)
    
    #if args.command in ["updatedb","download","status","publishers"]:
        # nasty trick, again better with a factory DP???
    #    getattr(library, args.command)()
    #else:
    #    sys.stderr.write("%s command unknown" % args.command)
        
if __name__ == "__main__":
    main()