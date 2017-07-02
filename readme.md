Mjolnir
=======

Mjolnir is a simple Python3 script that can be used to automate simple computer administrative tasks.

Currently it can create, delete and copy directories, copy files, execute commands and set environment variables (the latter only on Windows).

It accepts as input an XML file that describes the actions to be taken.

**WARNING:** Currently no input validation is performed and thus you have to be very careful about the contents of the input file you use.
             Also, note that the program deletes and alters the filesystem and system environment with all the security issues this implies.

Refer to the sample.xml file and the `parse_and_run` method in the source code for details on the format of the input file.

Runtime requirements
--------------------

Python 3

