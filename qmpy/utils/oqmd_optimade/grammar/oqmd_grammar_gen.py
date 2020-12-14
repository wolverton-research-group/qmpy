import json

propd={}

propd["chemical_formula_reduced"]   = 'composition__formula__in'
propd['chemical_formula']           = 'composition__formula__in'

propd["chemical_formula_anonymous"] = 'composition__generic'
propd['formula_prototype']          = 'composition__generic'
propd['generic']                    = 'composition__generic'

propd["nelements"]        = 'entry__composition__ntypes'
propd["ntypes"]           = 'entry__composition__ntypes'

propd["elements"]         = 'composition__element_list__contains'

propd["nsites"]           = 'entry__natoms'
propd['natoms']           = 'entry__natoms'

#propd["_oqmd_entry_id"]   = 
#propd["_oqmd_calculation_id"] = 
#propd["_oqmd_icsd_id"]    = 

propd["element"]         = 'composition__element_list__contains'

propd['_oqmd_volume']     = 'calculation__output__volume'
propd['volume']           = 'calculation__output__volume'

propd["_oqmd_band_gap"]   = 'calculation__band_gap'
propd["band_gap"]         = 'calculation__band_gap'

propd["_oqmd_delta_e"]    = 'delta_e'
propd["delta_e"]          = 'delta_e'

propd["_oqmd_stability"]  = 'stability'
propd["stability"]        = 'stability'

propd["_oqmd_prototype"]  = 'entry__prototype'
propd["prototype"]        = 'entry__prototype'

propd["_oqmd_spacegroup"] = 'calculation__output__spacegroup__hm'
propd["spacegroup"]       = 'calculation__output__spacegroup__hm'

logic_queryable_list = ["stability","_oqmd_stability","delta_e","_oqmd_delta_e",
                        "band_gap", "_oqmd_band_gap", 'volume', '_oqmd_volume',
                        'natoms',"nsites","ntypes","nelements"]
chem_formula_list= ['chemical_formula',"chemical_formula_reduced"]
set_queryable_list   = ['elements']
length_prop_dict     = {'elements':'nelements',}


props = {}
for item in propd.keys():
    props[item] = {
        'name'        : item,
        'db_value'    : propd[item],
        'is_queryable': True,
        'length_prop' : length_prop_dict[item] if item in length_prop_dict else None,
        'is_chem_form'     : True if item in chem_formula_list    else False,
        'is_set_operable'  : True if item in set_queryable_list   else False,
        'is_logic_operable': True if item in logic_queryable_list else False,
    }
    
#props['elements']['length_prop'] = 'nelements'
#props['elements']['is_set_operable']    = True

for item in ['_oqmd_entry_id','_oqmd_calculation_id','_oqmd_icsd_id','id', 
             'type', 'last_modified', 'lattice_vectors', 
             '_oqmd_direct_site_positions', 'species_at_sites', 'dimension_types', 
             'nperiodic_dimensions', 'elements_ratios', 'structure_features', 
             'chemical_formula_descriptive', 'species', 'cartesian_site_positions', ]:
    props[item] = {
        'name'     : item,
        'db_value' : None,
        'length_prop' : None,
        'is_queryable': False,
        'is_chem_form'     : False,
        'is_set_operable'  : False,
        'is_logic_operable': False,
    }
json.dump(props,open('v1.0.0.oqmd','w'),indent=4)
