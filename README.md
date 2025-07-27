pypatch-url
===========

Automatically apply patches to third-party libraries as part of your build.

Now and again, a specific fix is needed for a python package that isn't available from the vendor/community.
This project was created to allow a way for us to patch specific python modules during the build process.

pypatch-url is a fork of Sitka Technology Group's PyPatch tool, which itself is a command wrapper based around Anatoly Techtonik's patch.py utility. This fork adds two important features that were already present in the underlying patch.py utility but weren't accessible from the command line:

1. **Path stripping** with `-p NUM` or `--strip=NUM` to strip leading components from file names (matching the standard Unix `patch` tool)
2. **URL support** to automatically download patches when a URL is specified instead of a local file path

These enhancements were contributed by sfinktah@github.spamtrak.org, although the underlying functionality already existed in Anatoly Techtonik's patch.py library.

Usage
---
```
pypatch-url apply custom_diff.patch [library.package]```
With the new options:
```

pypatch-url apply -p 1 custom_diff.patch [library.package]  # Strip one directory level from paths
pypatch-url apply https://example.com/patches/fix.patch [library.package]  # Download and apply patch
```
As a part of the work flow:
```

c:\project\pip install django
c:\project\pip install pypatch-url
c:\project\pypatch-url apply c:\project\patches\my_auth_fix.patch django.contrib.auth
```
How it works
------------
pypatch-url applies patches to files relative to the root directory of the named package. So it does have to be installed into the target environment.

For example, if the django package was installed to "C:\Python27\Lib\site-packages\django" and you needed to patch the auth contrib package (django.contrib.auth), your command might look like
```
pypatch-url apply c:\project\patches\my_auth_fix.patch django.contrib.auth```
and the files named in my_auth_fix.patch would use relative pathing from the package directory:
```

--- models.py    2013-05-06 15:12:14.212220100 -0700
+++ models.py	2013-05-06 14:36:20.535220100 -0700
```
If you used
```
pypatch-url apply c:\project\patches\my_auth_fix.patch django.contrib```
instead, your diff patch would read
```

--- auth/models.py	2013-05-06 15:12:14.212220100 -0700
+++ auth/models.py	2013-05-06 14:36:20.535220100 -0700
```
Path Stripping
-------------
The `-p NUM` or `--strip=NUM` option allows you to strip leading path components from file names in the patch. This is especially useful when applying patches created from different directory structures:
```

pypatch-url apply -p 1 c:\project\patches\my_fix.patch django
```
This would strip the first directory component from each path in the patch file.

URL Support
----------
You can directly specify a URL instead of a local patch file:
```

pypatch-url apply https://example.com/patches/fix.patch django
```
This will automatically download the patch file from the URL and apply it to the specified module.

Build
-----
To build the distributable python package, run 'sdist' from the Project Root Directory.
Recommended: setting the output directory to our Libraries folder
```
sdist --dist-dir="C:\outputdir"```
This will build the zipped python package that can be installed via pip or easy_install

Other
-----
Information on the Unified Diff format can be found at
https://www.gnu.org/software/diffutils/manual/html_node/Unified-Format.html#Unified-Format
