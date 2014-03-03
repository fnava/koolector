# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:09:20 2014

@author: fnavarro
"""

import os
import subprocess
import sys
import re
import json
import magic
from booklibrary import bookLibrary
import hashlib

# taken from http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
def hashfile(afile, blocksize=65536):
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()

class genesis(bookLibrary):
    
    siteUrl = "http://libgen.org"
    
    def updatedb(self):
        # Pseudo codigo
        ## Descarga de libgen
        # Descargar dump database
        # Descargar snapshot codigo
        # Borrar mysql db
        # Descomprimir dump (piping?)
        # Importar dump
        # Descomprimir codigo php
        # Copiar config.php                    #os.remove(filepath)
        # restart mysql y apache

        ## Otencion listado items
        #+ consulta contra database
        #+ formar diccionario base "books"
        #+ cargar diccionario anterior
        #+ merge de datos:
            # copiar marcas        # Compare book databases
            # ??
        # volcar diccionario a JSON

        # query to libgen local mirrored mysql database   
        libgendb = self._query_libgen()
        self._load_bookdb()
        # rebuild local book database after libgendb data
        self._bookdb_compare(libgendb) 
        # check downloaded books integrity against local db
        self._check_books()
        
    def _check_books(self):
        books_dir = os.path.join(self.homeDir, self.booksDir)
        book_files = [ f for f in os.listdir(books_dir) if os.path.isfile(os.path.join(books_dir,f)) ]
        
        for f in book_files:
            filepath = os.path.join(books_dir,f)
            m = re.match(u'^([0-9]{7})_',f)      
            if m:
                fileid = str(int(m.group(1)))
#                print fileid, filepath, self._bookdb[fileid] 
                filesize = os.stat(filepath).st_size
                if filesize == 0:
                    if self._bookdb["m"] != bookLibrary.marks["ignored"] and \
                        self._bookdb["m"] != bookLibrary.marks["repeated"]:
                            self._bookdb["m"] = bookLibrary.marks["ignored"]
                else:
                    md5 = hashfile(open(filepath, 'rb'))
                    print self._bookdb[fileid]["md5"]
                    print md5
                    if self._bookdb[fileid]["md5"] != md5:
                        print "Warn: MD5 mismatch for:"
                        print filepath
                        self._bookdb["m"] = bookLibrary.marks["error"]
                        #os.remove(filepath)
                    else:
                        self._bookdb["m"] = bookLibrary.marks["downloaded"]
            else:
                print "Warn: Unable to find bookd ID for:"
                print filepath

    def _query_libgen(self): 
        filter = """
SELECT 
    updated.id, 
    updated.md5,
    updated.Title,
    updated.Author,
    updated.Year,       /* Filtered, only 2012-2013 */
    updated.Publisher,
    updated.Pages,
    updated.Language,   /* Filtered, only "English" */
    updated.Extension,  /* Filtered, only "pdf" */
    updated.Identifier, /* Usually ISBN13.ISBN10 */
    topics.topic_descr  /* Format topic\\subtopic */
FROM updated, topics 
WHERE 
    updated.Extension='pdf'
    AND updated.Filename!="" 
    AND updated.Generic="" 
    AND updated.Visible=""
    AND updated.Language="English"
    AND updated.Year in ("2014","2013")
    AND (
        topics.topic_descr like "Computers%"
        OR topics.topic_descr like "Techn%"
        OR topics.topic_descr like "Math%"
        OR topics.topic_descr like "Scien%"
        )
    AND updated.topic=topics.topic_id         # id
        # md5
        # ISBN
        # Año
        # Titulo 
        # Publisher
        # num paginas? - filtrado, por generalidad
        # Language? - filtrado, por generalidad
        # Format? - filtrado, por generalidad
    AND topics.lang='en' 
/* que sentido tiene el group by aquí?
GROUP BY 
    updated.Year,topics.topic_descr 
*/
ORDER BY 
    updated.Year DESC
"""
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

        # NOTE: from http://docs.python.org/2/library/json.html
        #  Keys in key/value pairs of JSON are always of the type str. 
        #  When a dictionary is converted into JSON, all the keys of 
        #  the dictionary are coerced to strings. As a result of this, 
        #  if a dictionary is converted into JSON and then back into
        #  a dictionary, the dictionary may not equal the original one. 
        #  That is, loads(dumps(x)) != x if x has non-string keys.

        new_bookdb = {}
        for idx,libgen_book in libgendb.items():
            sidx = str(idx)
            if sidx in self._bookdb:
                local_book = self._bookdb[sidx]
                new_bookdb[sidx] = {}
                for idx2, libgen_book_field in libgen_book.items():
                    if idx2 in local_book:
                        if local_book[idx2] == libgen_book_field:
                            new_bookdb[sidx][idx2] = local_book[idx2]
                        else:
                            print "new field value for book id %s in libgen" % sidx
                            print "  field: %s" % idx2
                            print "  old value: %s" % local_book[idx2] 
                            print "  new value: %s" % libgen_book_field 
                            new_bookdb[sidx][idx2] = libgen_book_field
                    else:
                        print "new field %s for book id %s in libgen" % (idx2, sidx)
                        print "  value: %s" % libgen_book_field 
                        new_bookdb[sidx][idx2] = libgen_book_field
                if "m" in self._bookdb[sidx]:
                    new_bookdb[sidx]["m"] = self._bookdb[sidx]["m"]
                else:
                    new_bookdb[sidx]["m"] = ""
            else:
                print "new book found in libgen"
                print json.dumps(libgen_book,
                                sort_keys=True,
                                indent=4, 
                                separators=(',', ': ')
                                )
                new_bookdb[sidx] = libgen_book
                new_bookdb[sidx]["m"] = ""
#            short_title = "".join([c for c in new_bookdb[sidx]["title"] if re.match(r'\w', c)])
            short_title = self._shortify(new_bookdb[sidx]["title"])
            new_bookdb[sidx]["filename"] =  "%07d_%s.pdf" % (idx, short_title)
        self._bookdb = new_bookdb
        self._save_bookdb()
    
    def _filepath(self, book):
        return os.path.join(self.homeDir, self.booksDir, book["filename"])
    
    def _download_item(self, book):
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
                    self._bookdb["m"] = marks["to verify"]
                    return
            cmd_wget = "/usr/bin/wget -nc -O %s %s" % (filepath, downloadUrl)
            print cmd_wget
            subprocess.call(cmd_wget.split(), shell=False)
        sys.stderr.write("Unable to download %s" % filepath)
        
    def _check_next_item(self):
        bidx = 1
        blen = len(self._bookdb)
        for book_idx,book_data in self._bookdb.items():
            if not os.access(self._filepath(book_data), os.F_OK):
                return book_data
                break
                
    def download(self):
        self._load_bookdb()
        next_item = self._check_next_item()
        if next_item is not None:
            self._download_item(next_item)
        else:
            print "Nothing to download"
                    
    def status(self):
        print "status genesis. still not implemented"