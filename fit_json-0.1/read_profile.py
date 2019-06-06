#!/usr/bin/python

import os
scriptdir=os.path.dirname(os.path.realpath(__file__))
default_pickle=os.path.join(scriptdir,'profile.pickle')

class Profiles(object):
    def __init__(self):
        self.type_index={}
        self.base_type_index={}
        self.message_d={}

    def __getitem__(self, item):
        x=self.type_index[item]
        ret=dict([(k,x[k]['Value Name']) for k in x.keys()])        
        ret['Base Type']=self.base_type_index[item]
        return ret

    def get_field_name(self,message_name,num):
        mess=self.message_d[message_name]
        for m in mess:
            if not m.has_key('Field Def #'): continue
            if m['Field Def #']==num:
                return m['Field Name']
        raise KeyError

    def save_pickle(self, fname=None):
        if fname is None:
            fname = 'profile.pickle'

        import cPickle as pickle
        pickle.dump({'types':self.type_index,
                     'messages':self.base_type_index,
                     'message_names':self.message_d},
                    file(fname,'wb'))

    def load_pickle(self, fname=None):
        if fname is None:
            fname = 'profile.pickle'
            
        import cPickle as pickle
        j = pickle.load(file(fname,'rb'))
        self.type_index.update(j['types'])
        self.base_type_index.update(j['messages'])
        self.message_d.update(j['message_names'])
    
if __name__=="__main__":
    p=Profiles()
    p.load_pickle()    
    print p['mesg_num'][3]
    print p['mesg_num'][0]
    print p['mesg_count'][2]
