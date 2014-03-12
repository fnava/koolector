# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:09:20 2014

@author: fnavarro
"""

import os
import stat
import subprocess
import sys
import re
import json
import magic
from booklibrary import bookLibrary
import hashlib
import difflib


def hashfile(afile, blocksize=65536):
    """Return md5 hash for a given file"""
    # taken from http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()

class genesis(bookLibrary):
    
    siteUrl = "http://libgen.org"

    def status(self):
        print "status genesis. still not implemented"        
        
    def updatedb(self):
        libgendb = self._query_libgen()
        self._load_bookdb()
        self._bookdb_compare(libgendb) 
        
    def download(self):
        self._load_bookdb()
        next_item = self._check_next_item()
        if next_item is not None:
            self._download_item(next_item)
        else:
            print "Nothing to download"
                    
    def check_books(self):
        """Browse book directory for books and find matches into database
        
        Book file integrity is checked using criteria function which
        computes md5 sum and compares with value stored in database
        """

        def criteria(filepath, md5):
            """Compare computed md5 with stored in book db"""
            A = md5.strip().upper() 
            B = hashfile(open(filepath, 'rb')).upper()
            if not A == B:
                print "\n".join(difflib.ndiff([A], [B]))
                #print self._bookdb[fileid]["md5"]
                #print md5
            return A == B

        self._load_bookdb()
        books_dir = os.path.join(self.homeDir, self.booksDir)
        rejected_books_dir = os.path.join(self.homeDir, "rejected")
        book_files = [ f for f in os.listdir(books_dir) if os.path.isfile(os.path.join(books_dir,f)) ]
        
        for filename in book_files:
            filepath = os.path.join(books_dir,filename)
            m = re.match(u'^(B[0-9]{7})_',filename)
            if m:
                fileid = m.group(1)
            else:
                print "%s: rejected, no ID found" % filename
                self._reject_file(filename,"badid")
                continue
            if fileid in self._bookdb:
                book = self._bookdb[fileid]
#                print fileid, filepath, self._bookdb[fileid] 
                filesize = os.stat(filepath).st_size
                if filesize == 0:
                    if m in book and \
                        book["m"] != bookLibrary.marks["ignored"] and \
                        book["m"] != bookLibrary.marks["repeated"]:
                            book["m"] = bookLibrary.marks["ignored"]
                    else:
                        print "%s: rejected, size 0" % fileid
                        self._reject_file(filename,"badsize",book)
                else:
                    if not criteria(filepath, self._bookdb[fileid]["md5"]):
                        print "%s: rejected, md5 mismatch" % fileid
                        self._reject_file(filename,"badmd5",book)
                    else:
                        # File exists, and md5 match db claims, so we
                        # marked it as correctly downloaded in db
                        print "%s: ok" % fileid
                        self._bookdb["m"] = bookLibrary.marks["downloaded"]
            else:
                print "%s: rejected, not found in db" % fileid
                self._reject_file(filename,"notindb")
        self._save_bookdb()

    # Helper functions:

    def _filepath(self, book):
        """Returns full path filename for a books file"""
        if "filename" in book:
            return os.path.join(self.homeDir, self.booksDir, book["filename"])
        else:
            return None
            
    def _mirrordb(self):
        """Download libgen db snapshot dump file and rebuild in local mirror."""
        pass
        # Pseudo codigo
        ## Descarga de libgen
        # Descargar dump database
        # Descargar snapshot codigo
        # Borrar mysql db
        # Descomprimir dump (piping?)
        # Importar dump
        # Descomprimir codigo php
        # Copiar config.php                    
        # restart mysql y apache

        ## Otencion listado items
        #+ consulta contra database
        #+ formar diccionario base "books"
        #+ cargar diccionario anterior
        #+ merge de datos:
            # copiar marcas        
            # Compare book databases
            # ??
        # volcar diccionario a JSON

    def _query_libgen(self): 
        """Returns a dictionary with book data retrieved from mysql libgen db"""
        import genesis_sql        
        filter = genesis_sql.queries["everything_2014_bysize"]

        fields = ["id", 
                  "md5",
                  "title",
                  "authors",
                  "datePublished",
                  "publisher",
                  "numberOfPages",
                  "inLanguage",
                  "bookFormat",
                  "isbn",
                  "topic" 
                  ]   

        import MySQLdb
        import json                    #os.remove(filepath)
    
        libgendb = {}
        db = MySQLdb.connect(host="localhost", 
                             user="root",    
                             passwd="root",  
                             db="libgen1",
                             charset='utf8')
        cursor = db.cursor()
        cursor.execute(filter)
        db.commit()
        numrows = int(cursor.rowcount)
        for x in range(0,numrows):
            row = cursor.fetchone()
            libgendb[row[0]]={}
            for i,f in enumerate(fields):
                libgendb[row[0]][f]=row[i]
        return libgendb

    def _bookdb_compare(self, libgendb):        
        """Merge upstream with local database"""
        # NOTE: from http://docs.python.org/2/library/json.html
        #  Keys in key/value pairs of JSON are always of the type str. 
        #  When a dictionary is converted into JSON, all the keys of 
        #  the dictionary are coerced to strings. As a result of this, 
        #  if a dictionary is converted into JSON and then back into
        #  a dictionary, the dictionary may not equal the original one. 
        #  That is, loads(dumps(x)) != x if x has non-string keys.

        tmp_bookdb = {}
        for bidx,libgen_book in libgendb.items():
            sidx = "B%07d" % bidx
            if sidx in self._bookdb:
                local_book = self._bookdb[sidx]
                tmp_bookdb[sidx] = {}
                for fidx, libgen_book_field in libgen_book.items():
                    if fidx in local_book:
                        if local_book[fidx] == libgen_book_field:
                            tmp_bookdb[sidx][fidx] = local_book[fidx]
                        else:
                            print "%s.%s: %s -> %s" % (bidx, fidx, local_book[fidx], libgen_book_field)
                            tmp_bookdb[sidx][fidx] = libgen_book_field
                    else:
                        print "%s.%s: %s" % (bidx, fidx, libgen_book_field)
                        tmp_bookdb[sidx][fidx] = libgen_book_field
                if "m" in self._bookdb[sidx]:
                    tmp_bookdb[sidx]["m"] = self._bookdb[sidx]["m"]
                else:
                    tmp_bookdb[sidx]["m"] = ""
            else:
                print json.dumps(libgen_book,
                                sort_keys=True,
                                indent=4, 
                                separators=(',', ': ')
                                )
                tmp_bookdb[sidx] = libgen_book
                tmp_bookdb[sidx]["m"] = ""
#            short_title = "".join([c for c in tmp_bookdb[sidx]["title"] if re.match(r'\w', c)])
            short_title = self._shortify(tmp_bookdb[sidx]["title"])
            tmp_bookdb[sidx]["filename"] =  "%s_%s.pdf" % (sidx, short_title)
        self._bookdb = tmp_bookdb
        self._save_bookdb()
    
    def _download_item(self, book):
        """Download book file"""
        downloadUrl = "%s/get?md5=%s&open=0" % (self.siteUrl, book["md5"])
        filepath = self._filepath(book)
        for i in range(0,2):
            print i
            if os.access(filepath, os.F_OK):
                md5 = hashfile(open(filepath, 'rb'))
                if book["md5"] != md5:
                    print "lo borraria"                    
                    #os.remove(filepath)
                else:
                    self._bookdb["m"] = bookLibrary.marks["to verify"]
                    return
            cmd_wget = "/usr/bin/wget -nc -O %s %s" % (filepath, downloadUrl)
            print cmd_wget
            subprocess.call(cmd_wget.split(), shell=False)
        sys.stderr.write("Unable to download %s" % filepath)
        
    def _check_next_item(self):
        """Return next book data from download queue"""
        for book_idx,book_data in self._bookdb.items():
            filename = self._filepath(book_data)
            if filename is not None:
                if not os.access(filename, os.F_OK):
                    return book_data
                    #break
        return None
                