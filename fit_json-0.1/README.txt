Round-trip FIT -> json -> FIT conversion.

Here is a small pure-Python .fit interpreter that converts a FIT
file[1] into a json-format text file.

Motivation
----------

This is useful for examining files in the FIT format, which is an
opaque format not easily processed with textual tools.

There is a fit-to-csv utility included in the FIT SDK, but CSV is a
terrible format, and the utility doesn't do clean round-tripping of
undefined fields and profiles.

Usage
-----

To convert a FIT file to json, use the "-j" option:

  ./fit_json.py -j < Settings.fit > Settings.json

The json file may be edited with any editor.

To convert back to FIT, use the "-f" option.

  ./fit_json.py -f < Settings.json > Settings.fit

Limitations
-----------

The FIT decoder and encoder do not support arrays or subfields.
Everything is represented in the most basic form; enums are
represented in their integer form and no scaling or offseting or units
are applied.

String lengths are not maintained through the round trip; string field
lengths are calculated to hold the strings they contain.

No special handling of null values is taken.  Missing values are not
encoded at all.

Files
-----

| filename          | description                                     |
|-------------------+-------------------------------------------------|
| fit_json.py       | Main script                                     |
| fit.py            | FIT decoder                                     |
| fit_writer.py     | FIT encoder                                     |
| profile.pickle    | FIT profile definitions                         |
| read_profile.py   | Script to read profile.pickle                   |
| read_xl_pandas.py | Script to convert Profile.xls to profile.pickle |
| Settings.fit      | Example FIT file (settings from an Edge 510)    |
| Settings.json     | Example decoded file                            |
| COPYING           | 2-clause BSD                                    |
| README.txt        | This file                                       |

[1] http://www.thisisant.com/developer/ant/ant-fs-and-fit1 

