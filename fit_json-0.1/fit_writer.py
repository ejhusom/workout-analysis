#!/usr/bin/python

import struct
import time
import fit
import sys

from fit import get_profiles
profiles=get_profiles()
#from fit import logfd

def local_hash(message_type, definition, value_counts):
    if not value_counts: value_counts=[]
    return repr([message_type]+list(definition)+value_counts)

class LocalDef(object):
    def __init__(self, num):
        self.message_type=''
        self.struct_format=''
        self.value_counts=[]
        self.definition=[]
        self.message_type_index={}
        self.num=num
        self.last_used=0

    @property
    def mhash(self):
        return local_hash(self.message_type, 
                          self.definition, 
                          self.value_counts)

class FitWriter(object):
    def __init__(self,fd):        
        self.fd=fd
        self.data=[]

        self.global_id={}
        for k in profiles['mesg_num']:
            val = profiles['mesg_num'][k]
            self.global_id[val]=k
        self.global_def=profiles.message_d

        self.local_defs=[LocalDef(n) for n in range(16)]
        self.local_def_hashes={}

        self.unknown_messages={}
        self.unknown_fields={}

    def write(self, out):
        self.data.append(out)

    def add_unknown_messages(self, messages):
        for k,v in messages.iteritems():
            self.unknown_messages[k] = v['fields']
            global_id = v['message_number']
            self.global_id[k]=global_id

    def add_unknown_fields(self, fields):
        self.unknown_fields.update(fields)
    
    def flush(self):
        data = ''.join(self.data)
        file_header = struct.pack("<BBHI4c",
                                  14, # size
                                  0x10,
                                  0x0514,
                                  len(data),
                                  '.','F','I','T')
        crc = '\0\0'
        crc = struct.pack('<H',fit.crc(file_header))
        self.fd.write(file_header)
        self.fd.write(crc)
        self.fd.write(data)
        crc = struct.pack('<H',fit.crc(file_header+crc+data))
        self.fd.write(crc)
        
    def get_string_fields(self, message_type, data_fields):
        base_types=[self.get_base_type_id(message_type, df) for df in data_fields]
        return map(lambda bt:bt[1]==7, base_types)
        
    def get_definition(self, message_type):
        """ returns a list of field names """
        return [f['Field Name'] for f in profiles.message_d[message_type]]

    def get_base_type_id(self, message_type, field_name):
        """ returns (number, size, base_type) tuple """
        
        message_type_index={}
        if message_type in profiles.message_d:
            for k in profiles.message_d[message_type]:
                message_type_index[k['Field Name']]=k

        if message_type_index.has_key(field_name):
            k=message_type_index[field_name]

            number=int(k['Field Def #'])
            field_type=k['Field Type']
            try:
                base_type_name=profiles[field_type]['Base Type']
            except KeyError:
                base_type_name=field_type

            base_type_id = fit.base_type_id_from_string(base_type_name)
            base_size = fit.base_type_size_from_id(base_type_id)
            return number,base_type_id,base_size
        else:
            field = self.unknown_fields[field_name]
            base_type_id=field['base_type']
            base_size = fit.base_type_size_from_id(base_type_id)
            return (field['field_number'],
                    base_type_id,
                    base_size)        
       
    def get_local_id(self, message_type, definition=None, value_counts=None):
        """- message_type is a string containing the message_type

        - definition is a list containing field names included in message

        - value_counts is a list of the field lengths.  This is 1 for
          scalar values and >1 for strings, arrays, etc.

        If field names are provided, then the loop proceeds with
        those.  Otherwise, the definitions are pulled from the profile.

        """

        try:
            profile_definition = self.get_definition(message_type)
        except KeyError:
            profile_definition = []

        definition = definition or profile_definition

        for d in definition:
            if not d in profile_definition and not d in self.unknown_fields:
                raise KeyError("field %s not in definition"%d)

        if not value_counts is None:
            assert(len(definition)==len(value_counts))

        this_hash = local_hash(message_type, definition, value_counts)
        try:
            local_def=self.local_def_hashes[this_hash]
        except KeyError:
            minimum_def=None
            for local_def in self.local_defs:
                if minimum_def is None or local_def.last_used < minimum_def.last_used:
                    minimum_def=local_def

            try:
                del self.local_def_hashes[minimum_def.mhash]
            except KeyError:
                pass

            local_def = LocalDef(minimum_def.num)
            local_def.message_type = message_type
            local_def.definition = definition
            local_def.value_counts = value_counts

            self.local_defs[local_def.num]=local_def
            self.local_def_hashes[this_hash] = local_def

            self.write_definition(local_def)

        local_def.last_used=time.time()        
        return local_def.num

    def write_definition(self, local_def):

        definition_header=0x40
        self.write(chr(definition_header|local_def.num))

        self.write(struct.pack('<BBHB',
                               0, # reserved
                               0, # little-endian
                               self.global_id[local_def.message_type],
                               len(local_def.definition)))

        message_type_index={}
        if local_def.message_type in profiles.message_d:
            for k in profiles.message_d[local_def.message_type]:
                message_type_index[k['Field Name']]=k

        def get_definition(field_name):
            """ returns (number, size, base_type) tuple """
            if message_type_index.has_key(d):
                k=message_type_index[d]

                number=int(k['Field Def #'])
                field_type=k['Field Type']
                try:
                    base_type_name=profiles[field_type]['Base Type']
                except KeyError:
                    base_type_name=field_type

                base_type = fit.base_type_id_from_string(base_type_name)
                return number,base_type

            else:
                field = self.unknown_fields[field_name]
                return field['field_number'],field['base_type']

        local_def.struct_format='<'

        for i,(d,count) in enumerate(zip(local_def.definition,local_def.value_counts)):
            import sys

            number,base_type = get_definition(d)

            struct_fmt = fit.base_type_format_from_id(base_type)
            base_size = fit.base_type_size_from_id(base_type)

            if base_type in [3,4,5,6,8,9,11,12]:
                base_type |= 0x80

            local_def.struct_format+="%%d%s"%(struct_fmt)

            assert(base_size == struct.calcsize(struct_fmt))
            assert(base_size)
            assert(count)
                
            self.write(struct.pack('<BBB',
                                   number,
                                   base_size*count,
                                   base_type))

            #print >> logfd,"Definition ",d,"base_num",base_type,"count",count,"base_size",base_size,"size",base_size*count

    def write_record(self, message_type, data):
        """
        message_type is a string of the message_type name.
        
        data is a list of (key, val) pairs.
        
        for variable-length data, data is e.g., (key, (val1, val2))
        """

        import sys
        data_fields,data_values=zip(*data)

        df2=[]
        sf = self.get_string_fields(message_type, data_fields)
        #print >> logfd, "String fields",repr(sf)
        
        for field_value,x in zip(data_values, self.get_string_fields(message_type, data_fields)):
            if x:
                df2.append(str(field_value)+'\0')
            else:
                df2.append(field_value)
        data_values = df2
       
        def count_values(d):
            try:
                return len(d)
            except:
                return 1

        data_lengths = map(count_values, data_values)

        local_id=self.get_local_id(message_type, data_fields, data_lengths)

        self.write(chr(local_id))

        #print >> logfd, "Local Format:",self.local_defs[local_id].struct_format
        #print >> logfd, "Data values:",data_values
        #print >> logfd, "Data lengths:",data_lengths

        struct_format = self.local_defs[local_id].struct_format%tuple(data_lengths)
        #print >> logfd, "Format:",repr(struct_format)

        flattened=[]
        for dv,l in zip(data_values,data_lengths):
            if type(dv)==str:
                flattened.append(dv)
            elif l==1:
                flattened.append(dv)
            else:
                flattened+=dv

        #print >> logfd, "Flattened:",repr(flattened)

        self.write(struct.pack(struct_format,*flattened))

