# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:57:38 2014

@author: fnavarro
"""

queries = {}

queries["clean_english_pdf_2013_2014_bysize_tech_topics"] = """
SELECT 
    updated.id, 
    updated.md5,
    updated.Title,
    updated.Author,
    updated.Year,       /* Filtered, only 2013-2014 */
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

queries["clean_english_pdf_2014_bysize"] = """
SELECT 
    updated.id, 
    updated.md5,
    updated.Title,
    updated.Author,
    updated.Year,       /* Filtered, only 2013-2014 */
    updated.Publisher,
    updated.Pages,
    updated.Language,   /* Filtered, only "English" */
    updated.Extension,  /* Filtered, only "pdf" */
    updated.Identifier, /* Usually ISBN13.ISBN10 */
    updated.topic  /* Format topic\\subtopic */
FROM updated
WHERE updated.Extension =  'pdf'
    AND updated.Filename !=  ""
    AND updated.Generic =  ""
    AND updated.Visible =  ""
    AND updated.Language =  "English"
    AND updated.Year IN ("2014")
ORDER BY  
    updated.Filesize DESC
"""

queries["clean_english_pdf"] = """
SELECT *
FROM updated
WHERE updated.Extension IN ("pdf", "PDF")
    AND updated.Filename !=  ""
    AND updated.Generic =  ""
    AND updated.Visible =  ""
    AND updated.Language =  "English"
    LIMIT 0,300
"""

fields = [
    ('ID','int(15)'),
    ('Title','varchar(2000)'),
    ('VolumeInfo','varchar(100)'),
    ('Series','varchar(300)'),
    ('Periodical','varchar(200)'),
    ('Author','varchar(1000)'),
    ('Year','varchar(14)'),
    ('Edition','varchar(60)'),
    ('Publisher','varchar(400)'),
    ('City','varchar(100)'),
    ('Pages','varchar(100)'),
    ('Language','varchar(150)'),
    ('Topic','varchar(500)'),
    ('Library','varchar(50)'),
    ('Issue','varchar(100)'),
    ('Identifier','varchar(600)'),
    ('ISSN','varchar(9)'),
    ('ASIN','varchar(200)'),
    ('UDC','varchar(200)'),
    ('LBC','varchar(200)'),
    ('DDC','varchar(45)'),
    ('LCC','varchar(45)'),
    ('Doi','varchar(45)'),
    ('Googlebookid','varchar(45)'),
    ('OpenLibraryID','varchar(200)'),
    ('Commentary','varchar(10000)'),
    ('DPI','int(6)'),
    ('Color','varchar(1)'),
    ('Cleaned','varchar(1)'),
    ('Orientation','varchar(1)'),
    ('Paginated','varchar(1)'),
    ('Scanned','varchar(1)'),
    ('Bookmarked','varchar(1)'),
    ('Searchable','varchar(1)'),
    ('Filesize','bigint(20)'),
    ('Extension','varchar(50)'),
    ('MD5','char(32)'),
    ('CRC32','char(8)'),
    ('eDonkey','char(32)'),
    ('AICH','char(32)'),
    ('SHA1','char(40)'),
    ('TTH','char(39)'),
    ('Generic','char(32)'),
    ('Filename','char(50)'),
    ('Visible','char(3)'),
    ('Locator','varchar(733)'),
    ('Local','int(10)'),
    ('TimeAdded','timestamp'),
    ('TimeLastModified','timestamp'),
    ('Coverurl','varchar(200)')
    ]

fields_dict = { i:(f, f.lower(), t) for i,(f,t) in enumerate(fields) }