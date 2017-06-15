# marc-remake
A reinvention of the JSON-to-MARC code for MUSICat.

The purpose of this is to put MUSICat's MARC export capability on a sound footing. (Because, Dear Reader, I myself wrote the hasty and entirely crap implementation presently in place.)

Goals of this **very short project** will include:
 - A sane and sensible abstract representation of the MARC record data.
 - Externalization of rendered data forms.
 - Externalization of per-library preferences as to inclusion/exclustion of data items.
 - Externalization of per-library preferences as to minor formatting tweaks.
 - A useful set of commandline utilities for working with MARC.
 - _Understandable code for those who will come after._
 - MVP in just a few workdays.

So, here's what this is: a complete component that isolates MARC-v-JSON data and formatting for MUSICat standard form. Will implement as a set of Python commandline tools, then as a Javascript code module that can be pulled into musicat-api.

The MARC formats will be: 
 - ISO-2709 binary (original MARC byte-oriented format)
 - MARC text as developed by Rabble, CCR, and SPL for editor-based 
 
"JSON" format does _not_ refer to the "MARCjson" proposed form. It means 

There will be roundtripping (as time permits) where there is no data loss.
