# This function is used only to generate grammer files. It is not called directly anywhere in Django
# models or functions

import json

db_grammer_data = {
    "band_gap": "calculation__band_gap",
    "natoms": "entry__natoms",
    "volume": "calculation__output__volume",
    "nytpes": "entry__composition__ntypes",
    "nelements": "entry__composition__ntypes",
    "stability": "stability",
    "delta_e": "delta_e",
    "prototype": "entry__prototype",
    "spacegroup": "calculation__output__spacegroup__hm",
    "generic": "composition__generic",
    "formula_prototype": "composition__generic",
    "chemical_formula": "composition__formula__in",
    "element": "composition__element_list__contains",
}


json.dump(db_grammer_data, open("./new_grammer.oqmd", "w"))
