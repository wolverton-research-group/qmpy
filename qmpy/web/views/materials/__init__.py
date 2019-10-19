from entry import *
from structure import *
from composition import *
from discovery import *
from chem_pots import *
from element_groups import *
from deposit import *

def common_materials_view(request):
    return render_to_response('materials/index.html', {})
