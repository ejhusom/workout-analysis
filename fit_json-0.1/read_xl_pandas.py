#!/usr/bin/python

try:
    import pandas
except ImportError:
    print "sudo apt-get install python-pandas"
    raise

import math

def isnan(x):
    if type(x)==float:
        return math.isnan(x)
    else:
        return False

import read_profile

class Profiles(read_profile.Profiles):

    def load_xls(self,filename):
        self.read_types(pandas.read_excel(filename,"Types"))
        self.read_messages(pandas.read_excel(filename,"Messages"))
        
    def read_types(self, types):
        base_type_index={}
        type_index={}
        fields={}
        working_type_name=None

        for type_name,base_type,value_name,value in types[['Type Name',
                                                           'Base Type',
                                                           'Value Name',
                                                           'Value']].values:
            if not isnan(type_name):
                if working_type_name:
                    base_type_index[working_type_name]=working_base_type
                    type_index[working_type_name]=fields
                    fields={}

                working_type_name=type_name.encode('ascii')
                working_base_type=base_type.encode('ascii')

            else:
                if not isnan(value):
                    row2={'Type Name':type_name,
                          'Base Type':base_type,
                          'Value Name':value_name,
                          'Value':value}
                    try:
                        fields[int(value,0)]=row2
                    except TypeError:
                        fields[int(value)]=row2     

        self.type_index.update(type_index)
        self.base_type_index.update(base_type_index)

    def read_messages(self, messages):
        NaN = pandas.np.NaN
        working_message_name=None
        message_d={}
        for (message_name, 
             field_name, 
             field_type,
             def_num) in messages[['Message Name',
                                   'Field Name',
                                   'Field Type',
                                   'Field Def #']].values:

            if not isnan(message_name):
                working_message_name=message_name
                message_d[message_name]=[]

            elif not isnan(field_name):
                row2={'Field Type':field_type,
                      'Field Name':field_name,
                      'Field Def #':def_num}
                
                message_d[working_message_name].append(row2)

        self.message_d.update(message_d)
    
if __name__=="__main__":

    p=Profiles()
    p.load_xls("Profile.xls")
    p.save_pickle()
    print p['mesg_num'][3]
    print p['mesg_num'][0]
    print p['mesg_count'][2]


