========
OQMD API
========

.. automodule:: qmpy

.. role:: query-url(literal)
.. role:: field(literal)

Introduction
============

RESTful API is now supported at oqmd.org! It allows the users to access the data of more than 900,000 materials easily by using simple HTTP requests. Downloading the entire SQL database is no longer required to extract materials data unless the DFT calculation-related files are to be viewed. This system is implemented within Django Python API framework. The querying on database is supported with a form-based user interface at oqmd.org/browse. But the documention provided in this page may be used for a more flexible querying and eliminating the need to use a UI. 

Querying
========

A simple request can be made like this 
:query-url:`http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,spacegroup,ntypes,band_gap,delta_e&filter=element_set=(Al-Fe),O`:

    .. code:: jsonc

     {
       "links": {
        "next": "http://oqmd.org/oqmdapi/formationenergy?fields=name%2Centry_id%2Cspacegroup%2Cntypes%2Cband_gap%2Cdelta_e&filter=element_set%3D%28Al-Fe%29%2CO&icsd=True&limit=2&offset=2",
        "previous": null,
        "base_url": {
            "href": "http://oqmd.org/oqmdapi",
            "meta": {
                "_oqmd_version": "1.0"
            }
        }
       },
       "resource": {},
       "data": [
        {
            "name": "NaAlH2CO5",
            "entry_id": 16974,
            "spacegroup": "Imma",
            "ntypes": 5,
            "band_gap": 5.255,
            "delta_e": -2.05739610121138
        },
        {
            "name": "CaAl2SiH4O8",
            "entry_id": 16995,
            "spacegroup": "I41/a",
            "ntypes": 5,
            "band_gap": 5.087,
            "delta_e": -2.49008973723542
        }
       ],
       "meta": {
        "query": {
            "representation": "/formationenergy?fields=name,entry_id,spacegroup,ntypes,band_gap,delta_e&icsd=True&limit=2&filter=element_set=(Al-Fe),O"
        },
        "api_version": "1.0",
        "time_stamp": "2019-10-08 15:13:12",
        "data_returned": 2,
        "data_available": 1078,
        "comments": "",
        "query_tree": "",
        "more_data_available": true
       },
       "response_message": "OK"
     }


URL Format
~~~~~~~~~~

Primary Query Fields
--------------------
    -  :field:`filter`: customized filters, e.g. 'element_set=O AND ( stability<-0.1 OR delta_e<-0.5 )'
    -  :field:`limit`: number of data return at once
    -  :field:`offset`: the offset of data return
    -  :field:`noduplicate`: whether the data should include duplicate entries or not
    -  :field:`sort_by`: the property on which the data has to be sorted
    -  :field:`sort_offset`:
    -  :field:`desc`:
    -  :field:`format`:
    -  :field:`fields`: return subset of fields, e.g. 'name,id,delta_e'
    -  :field:`icsd`: whether the structure exists in ICSD, e.g. False, True, F, T
    
  Keywords exclusively available for for usage in :field:`fields`:
   (eg: :field:`fields=sites,natoms,name`)
    1. :field:`sites`: list of atomic sites within the unit-cell
    2. :field:`formationenergy_id`: ID of this instance in formation energy dataset
    3. :field:`duplicate_entry_id`: OQMD ID of the preferred entry with this same crystal structure
    4. :field:`unit_cell`: unit cell dimensions (an array of 3x3) 
    5. :field:`fit`: the type of analysis
    6. :field:`calculation_label`
    7. :field:`icsd_id`: ICSD ID of this structure, if it exists
    8. :field:`composition_generic`: chemical formula abstract, e.g. AB, AB2
    9. :field:`name`: name of the compound
      
  Keywords exclusively available for usage in :field:`filter`: 
    (eg: :field:`filter=element_set=(S,O) AND (NOT element=As) AND stability=0`)
      1. :field:`element_set`: the set of elements that the compound must have, '-' for OR, ',' for AND, e.g. (Fe-Mn),O
      2. :field:`element`: specify the elements inclusion or exclusion of individual elements  
      
  Keywords commonly available for both :field:`filter` and :field:`fields`
    1. :field:`composition`: compostion of the materials or phase space, e.g. Al2O3, Fe-O
    2. :field:`prototype`: structure prototype of that compound, e.g. Cu, CsCl
    3. :field:`generic`: chemical formula abstract, e.g. AB, AB2
    4. :field:`spacegroup`: the space group of the structure, e.g. Fm-3m
    5. :field:`natoms`: number of atoms in the supercell, e.g. 2, >5
    6. :field:`volume`: volume of the supercell, e.g. >10
    7. :field:`ntypes`: number of elements types in the compound, e.g. 2, <3
    8. :field:`stability`: hull distance of the compound, e.g. 0, <-0.1,
    9. :field:`delta_e`: formation energy of that compound, e.g. <-0.5,
    10. :field:`band_gap`: band gap of the materials, e.g. 0, >2
    
Defaults
--------
    -  :field:`sort_by`: :field:`None` (default), :field:`delta_e` , :field:`stability` 
    
Response Format
~~~~~~~~~~~~~~~
1. Standard Django API Format
2. JSON
3. XML
4. YAML


More Example Queries
~~~~~~~~~~~~~~~~~~~~
1. :query-url:`http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,icsd_id,prototype,ntypes,natoms,volume,delta_e,band_gap,stability&limit=50&offset=0&sort_offset=0&noduplicate=False&desc=False&filter=stability<0.5 AND element_set=(Al-Fe),O AND (ntypes>=3 AND natoms<9) OR ntypes<3`
 Here, the `filter` key contains a logical expression using `AND` and `OR` functions. Also, response format filters such as `desc`, `noduplicate`, etc. are also shown in this example
2. :query-url:`http://oqmd.org/oqmdapi/formationenergy`
 All the properties of all materials
3. :query-url:`http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,band_gap&limit=50&offset=350&filter=stability=0.0`
 Limit and offset
4. :query-url:`http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,spacegroup,prototype&sort_by=delta_e&limit=50&sort_offset=350&noduplicate=True&desc=False&filter=stability=0`
 Showing the use of `sort`, `sort_offset`, and `noduplicate`

Practical Data Retrieval
~~~~~~~~~~~~~~~~~~~~~~~~

Command line
------------
:query-url:`wget "http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,delta_e&filter=stability=0&format=json" -O outfile.json`

or 

:query-url:`wget "http://oqmd.org/oqmdapi/formationenergy?fields=name,entry_id,delta_e&filter=stability=0&format=yaml" -O outfile.yaml`

Web Browser
-----------
:field:`CTRL+S` on the webpage
