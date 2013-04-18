iAdDownload
===========

This is a function that can be used to download iad reports from iTunes Connect.

## Getting Started

It requires that the python requests library is installed:

*  pip install requests

It will download csv formatted files with daily information and save the files
in a specified output diriectory.

There is an optional argument for publisherId which I recommend you store for the
future since it will speed up the script and because the scraping to find the
value for publisherId is likely to be fragile.

## How to use it

python iaddownload.py login password publisherId

## Changes

### Version 1.1.1

* Update code to download iAd reports from iTunes connect
* Add support for command line exectution
* Retrieve ProviderId from iTunes doesn't work