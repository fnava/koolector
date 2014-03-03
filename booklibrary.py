# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:07:21 2014

@author: fnavarro
"""

import json
import os
import re


jsonFile = "books.json"

class bookLibrary:

    booksDir = "books"
    # Marks in bookdb items to track items downloading status
    marks = {"downloaded":"d",  # item downloaded and verified correctly
             "to verify":"v",   # item downloaded pending to be verified
             "error":"e" ,       # md5 hash mismatch (filesize > 0)
             "ignored":"i",     # item to be ignored in next downloads
             "repeated":"r",    # identified as repeated item
             }
             
    def __init__(self, homeDir):
        self.homeDir=homeDir
        
    def command(self, cmd):
        if cmd in ["updatedb","download","status","publishers"]:
            # nasty trick, again better with a command DP???
            getattr(self, cmd)()

    def updatedb(self):
        print "updatedb", "undefined"

    def download(self):
        print "download", "undefined"

    def status(self):
        print "status", "undefined"
        
    def _shortify(self, title):
        return "".join([c for c in title if re.match(r'\w| ', c)]).replace(' ','_')  
        
    def _save_bookdb(self):
        filename=os.path.join(self.homeDir,jsonFile)
        f = open(filename,'w')
        f.write(json.dumps(self._bookdb,sort_keys=True))
        f.close()
    
    def _load_bookdb(self):
        filename=os.path.join(self.homeDir,jsonFile)
        if os.access(filename, os.F_OK):    
            f = open(filename,'r')
            books_json=f.read()
            self._bookdb=json.loads(books_json)
            f.close()
        else:
            self._bookdb = {}
