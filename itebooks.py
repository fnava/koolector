# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 10:26:40 2014

@author: fnavarro
"""

# Mejoras:
#  detectar numero de publishers
#  estadisticas: 
#   libros por descargar, 
#   libros descargados el ultimo mes
#  marcar y saltar archivo que no pueda descargar
#  historico de evolucion base de datos: #libros

from urllib2 import urlopen
from urllib2 import URLError
import urlparse
from bs4 import BeautifulSoup
import json
import re
import os
import sys
import stat
import time
import magic

from booklibrary import bookLibrary

def get_page(url):
    """Return parsed html page downloaded from a given URL"""
    max_trials = 5
    for i in range(max_trials):
        print i, url
        time.sleep(1)
        try:
            html = urlopen(url).read()
            soup = BeautifulSoup(html)
            success = True
            break
        except URLError as err:
            print err.reason
    if i == max_trials and not success: 
        return None
    for tag in soup.findAll('a', href=True):
            tag['href'] = urlparse.urljoin(url, tag['href'])
    return soup

class itebooks(bookLibrary):
    
    siteUrl = "http://it-ebooks.info"
        
    def status(self):
        self._load_bookdb()
        publishers = {}
        for b_idx,b in self._bookdb.items():
            p = b['publisher']
            if p in publishers:
                publishers[p] += 1
            else:
                publishers[p] = 1
        print "Books in database: %d" % len(self._bookdb)
        #for p,v in publishers.items():
        for p in sorted(publishers, key=publishers.get, reverse=True):
            c = publishers[p]
            print "  (%4.2f %%) %s: %d books" % (100.0*float(c)/float(len(self._bookdb)),p,c ) 
        items = self._new_items()
        if len(items) == 0:
            print "No new books missing. Nothing to download"
        else:
            print "New %d books missing. Next files to be downloaded:" % len(items)
        for i in items:
            print "   %s" % i[0]        
 
    def updatedb(self):
        self._get_publishers()
        #self._publishers = {1: u'The Pragmatic Programmers'}
        #self._publishers = {13: u'McGraw-Hill'}
        #self._publishers = {16: u'Springer'}
        # Download book listings:
        self._get_items()
        # Donwload books details from their pages:
        self._get_items_details()
        self._save_bookdb()

    def download(self):
        self._load_bookdb()
        next_item = self._check_next_item()
        if next_item is not None:
            (filename, refererUrl, downloadUrl) = next_item 
            self._download_item(filename, refererUrl, downloadUrl)
        else:
            print "Nothing to download"

    def check_books(self):
        
        def criteria(filepath):
            """Check mime filetype, has to be PDF"""
            filetype = mime.from_file(filepath)
            return filetype != "application/pdf"
        
        self._load_bookdb()
        books_dir = os.path.join(self.homeDir, self.booksDir)
        rejected_books_dir = os.path.join(self.homeDir, "rejected")
        book_files = [ f for f in os.listdir(books_dir) if os.path.isfile(os.path.join(books_dir,f)) ]
        mime = magic.Magic(mime=True) 
        
        for filename in book_files:
            filepath = os.path.join(books_dir,filename)
            m = re.match(u'^([0-9]{5})_',filename)
            if m:
                fileid_str = m.group(1)
                fileid = str(int(fileid_str))
            else:
                print "%s: rejected, no ID found" % filename
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
                        print "%s: rejected, size 0" % fileid_str
                        self._reject_file(filename,book)
                else:
                    if not criteria(filepath):
                        print "%s: rejected, filetype mismatch" % fileid_str
                        self._reject_file(filename,book)
                    else:
                        # File exists, and md5 match db claims, so we
                        # marked it as correctly downloaded in db
                        print "%s: ok" % fileid_str
                        self._bookdb["m"] = bookLibrary.marks["downloaded"]
            else:
                print "%s: rejected, not found in db" % fileid_str
                self._reject_file(filename)
        self._save_bookdb()
            
    def list_publishers(self):
        self._get_publishers()
        print self._publishers
        #print publishers

    # Helper functions:

    def _get_publishers(self):
        """Download publishers info from it-ebooks site into _publishers dict""" 
        self._publishers = {}
        idx = 1
        while idx > 0:
            soup = get_page("%s/publisher/%s/" % (self.siteUrl, idx) )
            h1 = soup.find_all("h1")
            if len(h1) > 0:
                self._publishers[idx] = h1[0].string
                idx += 1
            else:
                break
    
    def _get_items(self):
        """Get books basic info from it-ebooks site into _bookdb dict"""
        book_count = 0
        book_total = 0
        self._bookdb = {}
        for pubk,publisher in self._publishers.items():
            print "Downloading book list for publisher: %s" % publisher
            endloop = 1
            page = 1
            while endloop > 0:
    #            print " page: %s" % page
                soup = get_page("%s/publisher/%d/page/%d/" % (self.siteUrl, pubk, page))
                aes = soup.find_all("a")
                endloop = 0
                for a in aes:
                    title = a['title']
                    if title == "Next page":
                        endloop += 2
                    elif title == "Prev page":
                        endloop += -1
    #                print title, endloop
                    if len(a.find_all('img')) > 0:
                        itebooks_idx = int(re.search('.*/book/(\d+)/$', a['href']).groups()[0])
                        book_idx = "A%07d" % itebooks_idx
                        url_icon = a.contents[0]['src']
                        short_title = re.search('/images/ebooks/.+/(.*).jpg$', url_icon).groups()[0]
                        self._bookdb[book_idx] = {
                                           "url-itbooks":a['href'],
                                            "url-icon":url_icon,
                                            "title":title,
                                            "short-title":short_title,
                                            "publisher":publisher
                                            }
                        book_count += 1
                page += 1
            print"  %d books" % book_count
            book_total += book_count
        print "Total books found: %d" % book_total            
    
    def _get_items_details(self):
        """Get books detailed info from it-ebooks site and add to _bookdb dict"""
        bidx = 1
        blen = len(self._bookdb)
        for book_idx,book_data in self._bookdb.items():
            soup = get_page(book_data["url-itbooks"])
            a = soup.find('td', text="Download:").find_all_next('a')[0]
            book_data["url-download"] = a['href']
            #b = soup.find('b', itemprop='author')
            #book_data["author"] = b.string
            b = soup.find('b', itemprop='isbn')
            book_data["isbn"] = b.string
            b = soup.find('b', itemprop='datePublished')
            book_data["datePublished"] = b.string
            b = soup.find('b', itemprop='numberOfPages')
            book_data["numberOfPages"] = b.string
            b = soup.find('b', itemprop='inLanguage')
            book_data["inLanguage"] = b.string
            b = soup.find('b', itemprop='bookFormat')
            book_data["bookFormat"] = b.string
            print "%s (%d/%d) %s" % (book_idx, bidx, blen, book_data)
            print "%s (%d/%d)" % (book_idx, bidx, blen)
            bidx += 1
    
    def _download_item(self, filename, refererUrl, downloadUrl):
        """Donwload book file using the temporary URL from book page"""
        filepath = os.path.join(self.homeDir, self.booksDir, filename)
        cmd_wget = "wget -nc -O %s --referer %s %s" % (filepath, refererUrl, downloadUrl) 
        filetype = ""
        for i in range(0,10):
            if os.access(filepath, os.F_OK): 
                filetype = mime.from_file(filepath)
                if filetype == "application/pdf":
                    return
                else:
                    os.remove(filepath)
            os.system(cmd_wget)
            #print cmd_wget             
            mime = magic.Magic(mime=True)
            filetype = mime.from_file(filepath)
            time.sleep(10)
        sys.stderr.write("Unable to download %s" % filename)
        
    def _check_next_item(self):
        basedir = os.path.join(self.homeDir,self.booksDir)
        bidx = 1
        blen = len(self._bookdb)
        for book_idx,book_data in self._bookdb.items():
            #filename = "%05d_%s.%s" % (int(book_idx),book_data['short-title'],book_data['bookFormat'])
            short_title = self._shortify(book_data["title"])
            filename =  "%s_%s.pdf" % (book_idx, short_title)
            filepath = os.path.join(basedir, filename)
            if not os.access(filepath, os.F_OK):
                soup = get_page(book_data["url-itbooks"])
                a = soup.find('td', text="Download:").find_all_next('a')[0]
                url_download = a['href']
                #print('%s/../wget2.sh "%s" %s %s' % (basedir, filename, book_data['url-itbooks'],url_download))
                return (filename, book_data['url-itbooks'],url_download)
                break
            
    def _new_items(self):
        items = []
        basedir = os.path.join(self.homeDir,self.booksDir)
        bidx = 1
        blen = len(self._bookdb)
        for book_idx,book_data in self._bookdb.items():
            filename = "%05d_%s.%s" % (int(book_idx),book_data['short-title'],book_data['bookFormat'])
            filepath = os.path.join(basedir,filename)
            if not os.access(filepath, os.F_OK):
                soup = get_page(book_data["url-itbooks"])
                a = soup.find('td', text="Download:").find_all_next('a')[0]
                url_download = a['href']
                #print('%s/../wget2.sh "%s" %s %s' % (basedir, filename, book_data['url-itbooks'],url_download))
                items.append( (filename, 
                                   book_data['url-itbooks'],
                                   url_download)
                                   )
        return items


            

        