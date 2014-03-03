# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:07:21 2014

@author: fnavarro
"""

import json
import os

import itebooks
import genesis

jsonFile = "books.json"

class bookLibraryFactory:
    
    libraries = {
    "itebooks":itebooks.itebooks,
    "genesis":genesis.genesis
    }    
    
    def createLibrary(self, key, homedir):
        return self.libraries[key](homedir)
        
