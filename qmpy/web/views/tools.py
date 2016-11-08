from qmpy.data.meta_data import GlobalInfo, GlobalWarning
from qmpy.models import Project, Host

def get_globals(in_dict=None):
    if in_dict:
        data = in_dict
    else:
        data = {}
    data['global_warnings'] = GlobalWarning.list()
    data['global_info'] = GlobalInfo.list()
    data['project_list'] = Project.objects.all()
    data['host_list'] = Host.objects.all()
    #v
    #data['user_list'] = Users.objects.all()
    return data
