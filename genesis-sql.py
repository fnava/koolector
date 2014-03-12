# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:57:38 2014

@author: fnavarro
"""

queries = {}

queries["tech_topics_2013_2014"] = """
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

queries["everythign_2013_2014_bysize"] = """
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
    AND updated.Year IN ("2014","2013")
ORDER BY  
    updated.Filesize DESC
"""

