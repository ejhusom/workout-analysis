#!/usr/bin/python

import struct,sys

import os

class FitCRCError(Exception): pass
class FitDataTypeError(Exception): pass

class MessageType(object):
    pass

import cPickle as pickle
import time

epoch=time.mktime((1989,12,31,0,0,0,0,0,0))-time.timezone

class EofException(Exception): pass

def print_fields(names, d, parsed):
    print ", ".join("%s=%s"%(a,b) for a,b in parsed)

def get_profiles():
    import read_profile
    p = read_profile.Profiles()
    p.load_pickle()
    return p

def base_type_id_from_string(base_type_name):
    return {'enum':0x00, # 0
            'sint8':0x01, # 1
            'uint8':0x02, # 2
            'bool':0x02, # 2.
            'sint16':0x83, # 3
            'uint16':0x84, # 4
            'sint32':0x85, # 5
            'uint32':0x86, # 6
            'string':0x07, # 7
            'float32':0x88, # 8
            'float64':0x89, # 9
            'uint8z':0x0a, # 10
            'uint16z':0x8b, # 11
            'uint32z':0x8c, # 12
            'byte':0x0d}[base_type_name]

def base_type_size_from_id(base_type_id):
    #       0 1 2 3 4 5 6 7 8 910111213
    return [1,1,1,2,2,4,4,1,4,8,1,2,4,1][base_type_id & 0xf]

def base_type_format_from_id(base_type_id):
    #       01234567890123
    return "BbBhHiIsfdBHIs"[base_type_id & 0xf]

class Fit(object): 
    def __init__(self, fd, data_field_disposition=-1):
        self.timestamp0=None
        
        self.profiles=get_profiles()
        self.message_types=[None]*16

        # None has special meaning..
        if data_field_disposition==-1:
            self.data_field_disposition = print_fields
            self.ofd=sys.stdout
        else:
            self.data_field_disposition = data_field_disposition
            self.ofd=sys.stderr

        self.fd=fd
        self.unknown_messages={}
        self.unknown_fields={}
       
        self.parse_file_header()
        try:
            while 1:            
                self.parse_record()

        except EofException:
            return

        except:
            print >> sys.stderr, "File is at",self.fd.tell()
            raise        

    def fd_read(self,ct):
        data=self.fd.read(ct)
        if len(data)<ct:
            raise EofException
        return data
        
    def parse_file_header(self):
        data=self.fd_read(1)
        data+=self.fd_read(ord(data)-1)

        (length,
         self.protocol_version,
         self.profile_version,
         self.data_size,
         self.data_type)= struct.unpack("<BBHI4s",data[:12])

        if len(data)==14:
            (CRC,) = struct.unpack("<H",data[12:14])
        else:
            CRC=None

        if (self.data_type != ".FIT"):
            raise FitDataTypeError

        if CRC and CRC!=crc(data[:-2]):
            raise FitCRCError

    def parse_record(self):
        record_header=ord(self.fd_read(1))
        normal_header = not (record_header & (1<<7))

        if normal_header:

            local_message_type=record_header & 0x0f

            #print >> logfd, "local",local_message_type

            if record_header & (1<<6): # definition message
                self.message_types[local_message_type]=self.parse_def_message()
                #print >> logfd, "newly defined %d"%local_message_type

            else:
                message=self.parse_data_message(self.message_types[local_message_type])
        
        else: # compressed timestamp
            time_offset=record_header & 0x1f
            local_message_type=(record_header>>5)&0x3
            message=self.parse_data_message(self.message_types[local_message_type])

            #print >> self.ofd, 'record_header',record_header
            
    def parse_def_message(self):
        m=MessageType()
        
        self.fd_read(1)
        arch="<>"[ord(self.fd_read(1))]
        
        m.global_message_number,field_ct=struct.unpack(arch+"HB",self.fd_read(3))
        m.parse=arch

        try:
            message_name=self.profiles['mesg_num'][m.global_message_number]
        except KeyError:
            message_name="unknown_message_%03d"%m.global_message_number

        m.name=message_name

        #print >> self.ofd, 'global_message_number', repr(m.global_message_number),repr(message_name)
        #print >> self.ofd, 'fields',repr(field_ct)
        m.size=0
        m.names=[]
        m.string_fields=[]
        m.field_counts=[]

        fields=[]
        for i in range(field_ct):
            field_number,total_size,base_type=struct.unpack(arch+"BBB",self.fd_read(3))
 
            try:
                name = self.profiles.get_field_name(message_name,field_number)
                m.names.append(name)
            except KeyError:
                name = "unknown_field_%03d_of_%s"%(field_number,m.name)
                assert(not name in m.names)
                m.names.append(name)
                self.unknown_fields[name]={'field_number':field_number,
                                           'total_size':total_size,
                                           'base_type':base_type}
                

            #print >> self.ofd, "num, size, base",field_number, total_size, base_type
            base_type_number=base_type&0x0f
            #print >> self.ofd, 'base_type_number', base_type_number
            fields.append([field_number,total_size,base_type])
            assert(total_size)

            if base_type_number==7:
                m.string_fields.append(i)

            f=base_type_format_from_id(base_type_number)

            #print >> logfd, "field type",base_type_number
            #print >> logfd, "field size",struct.calcsize(f)
            #print >> logfd, "base size",base_type_size_from_id(base_type_number)
            #print >> logfd, "total size",total_size
            #print >> logfd, "format spec",f

            assert(struct.calcsize(f))
            assert(total_size >= struct.calcsize(f))


            value_count = total_size/struct.calcsize(f)
            assert(value_count)
            
            m.parse+="%d%s"%(value_count,f)
            m.size+=total_size
            #print >> logfd, name, "parse as", f, "base type",base_type_number
            m.field_counts.append(value_count)

        #print >> logfd, "name and parse",m.name,m.parse

        m.fields=fields

        if m.name.startswith('unknown_message'):
            if self.unknown_messages.has_key(m.name):
                old_message = self.unknown_messages[m.name]
                assert(old_message['message_number']==m.global_message_number)
                assert(old_message['fields']==m.names[:])

            self.unknown_messages[m.name] = {'message_number':m.global_message_number,
                                             'fields':m.names[:], #fields
                                             }
        #sys.exit(0)

        return m
        
    def parse_data_message(self, m):
        if not m: return

        data=self.fd_read(m.size)

        # The python struct module doesn't group multiples (except for
        # strings) so we read in, then group after.

        v1=struct.unpack(m.parse,data)
        v=[]

        #print >> logfd, "parsewith", repr(m.parse)
        #print >> logfd, "parseto", repr(v1)

        #print >> logfd, "string fields", m.string_fields

        for i,ct in enumerate(m.field_counts):
            # remove trailing \0 from strings
            if i in m.string_fields:
                s = v1[0]
                v1 = v1[1:]
                #print >> logfd, "field",i, repr(s)
                v.append(s[:s.index('\0')])                
            else:
                this_values=v1[:ct]
                v1=v1[ct:]
                if len(this_values)==1:
                    v.append(this_values[0])
                else:
                    v.append(this_values)

        if len(m.names) != len(v):
            #print >> logfd, repr(m.parse)
            #print >> logfd, repr(data)
            #print >> logfd, repr(m.names)
            #print >> logfd, repr(v)
            raise Exception
        
        if self.data_field_disposition:
            self.data_field_disposition(m.name, zip(m.names,v))

def crc(data):
    crc=0
    crc_table=[0x0000, 0xCC01, 0xD801, 0x1400, 
               0xF001, 0x3C00, 0x2800, 0xE401,
               0xA001, 0x6C00, 0x7800, 0xB401, 
               0x5000, 0x9C01, 0x8801, 0x4400]

    for d in data:
        byte=ord(d)
        # compute checksum of lower four bits of byte
        tmp = crc_table[crc & 0xF];
        crc = (crc >> 4) & 0x0FFF;
        crc = crc ^ tmp ^ crc_table[byte & 0xF];
        # now compute checksum of upper four bits of byte
        tmp = crc_table[crc & 0xF];
        crc = (crc >> 4) & 0x0FFF;
        crc = crc ^ tmp ^ crc_table[(byte >> 4) & 0xF];
    return crc
            
if __name__=="__main__":
    f=Fit(sys.stdin)
    

