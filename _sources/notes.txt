Release Notes
=============

Version 1.1
-----------

The get_function_name utility function is new.

Optional (extra) requirements "pyinotify" and "requests" are now truly
optional; details are below.

`FileSystemNotifier` is no longer imported into the base package because it has
a requirement that is optional/extra for the library.  The name for the extra
feature has been changed from "FileSystemNotifier" to "fsnotify".

The "requests" extra feature name is new, and a project should require it if it
intends to make HTTP requests from the REST classes in pyneric.rest_requests.
Those REST classes are also now usable without the "requests" package
requirement (if not calling HTTP request methods, of course).

Version 1.0
-----------

This is the initial stable release.  Some util module functions and the meta
and rest_requests modules are new.

Version 0.2
-----------

The new pyneric.fsnotify module adds simple support for file system event
notifications with the FileSystemNotifier class.  The pyinotify library is
optional but is required to use this module.

Version 0.1
-----------

This was the first alpha release, containing a few utility functions and
extensions and fixes for using the future library.
