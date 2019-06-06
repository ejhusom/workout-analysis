#!/usr/bin/python

import fit,fit_writer
import json

import sys

def fit_to_json(fd_in, fd_out):
    data_fields=[]
    def stash_data(name,data): 
        data_fields.append({name:data})

    f = fit.Fit(fd_in, data_field_disposition=stash_data)

    data = {'data_records':data_fields,
            'unknown_messages':f.unknown_messages,
            'unknown_fields':f.unknown_fields}

    json.dump(data, fd_out,
              indent = 4, ensure_ascii=False,
              sort_keys=True)

import sys
    
def json_to_fit(fd_in, fd_out):
    fw=fit_writer.FitWriter(fd_out)
    jdata = json.load(fd_in)

    fw.add_unknown_messages(jdata['unknown_messages'])
    fw.add_unknown_fields(jdata['unknown_fields'])

    for f in jdata['data_records']:
        (name,data), = f.iteritems()
        fw.write_record(name,data)

    fw.flush()

def print_usage(fd=None):
    fd=fd or sys.stderr

    print >> fd, """
 %s -- convert fit to editable json and back again

Use like this:

  %s --to_json [FIT_FILENAME JSON_FILENAME]

or 

  %s --to_fit [JSON_FILENAME FIT_FILENAME]

where FIT_FILENAME are the filenames of fit and json files,
respectively.  If these are omitted stdin and stdout will be used.
"""%(3*(sys.argv[0],))

def main(argv):
    def choose_io(argv):
        if len(argv)==2:
            fd_in = file(argv[0],'r')
            fd_out = file(argv[1],'wb')
        else:
            fd_in = sys.stdin
            fd_out = sys.stdout
        return fd_in, fd_out

    if argv[1:] and argv[1] in ["--to_json", "-j"]:
        fit_to_json(*choose_io(argv[2:]))
        
    elif argv[1:] and argv[1] in ["--to_fit", "-f"]:
        json_to_fit(*choose_io(argv[2:]))

    else:
        print_usage()
        sys.exit(-1)

if __name__=="__main__":    
    main(sys.argv)
