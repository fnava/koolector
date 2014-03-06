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
        if cmd in ["updatedb","download","status","check_books","publishers"]:
            # nasty trick, again better with a command DP???
            getattr(self, cmd)()

    def updatedb(self):
        print "updatedb", "undefined"

    def download(self):
        print "download", "undefined"
        
    def check_books(self):
        """Pass integrity tests on book files contained in downloads folder.
        
        Keyword arguments:
            None
        For each file in the folder, if it is found in database and meets
        integrity constraints is marked in db as downloaded, otherwise 
        it's marked as error in db and the bad file is moved to 'rejected'
        folder.
        Integrity contraints depend upon the book library, e.g.:
            * genesis: compute md5 hash and compare with database md5 field
            * it-ebooks: verify the file has pdf format
        """
        print "check_books", "undefined"

    def status(self):
        print "status", "undefined"
        
    def _shortify(self, title):
        return "".join([c for c in title if re.match(r'\w| ', c)]).replace(' ','_')  
        
    def _save_bookdb(self):
        """Dump _bookdb dictionary to JSON format database"""
        filename=os.path.join(self.homeDir,jsonFile)
        f = open(filename,'w')
        f.write(json.dumps(self._bookdb,sort_keys=True))
        f.close()
    
    def _load_bookdb(self):
        """Load book database into _bookdb dictionary"""
        filename=os.path.join(self.homeDir,jsonFile)
        if os.access(filename, os.F_OK):    
            f = open(filename,'r')
            books_json=f.read()
            self._bookdb=json.loads(books_json)
            f.close()
        else:
            self._bookdb = {}
            
    def _reject_file(self, filename, book=None):
        """File reject actions called from check_books
        
        Common action to all book library types to be performed with all
        rejected files during check_books execution
        """
        books_dir = os.path.join(self.homeDir, self.booksDir)
        rejected_books_dir = os.path.join(self.homeDir, "rejected")
        filepath = os.path.join(books_dir,filename)
        if book is not None:
            book["m"] = bookLibrary.marks["error"]
        if not os.path.isdir(rejected_books_dir):
            os.mkdir(rejected_books_dir)
        os.rename(filepath, os.path.join(rejected_books_dir,filename))
