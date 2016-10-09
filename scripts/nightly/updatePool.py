#!/usr/bin/python

# Python script to update the CACTUS RPM Pool
# 
# Author: Christos Lazaridis

import os, sys, fnmatch
from os.path import join

global unmatched_packages 

def query_yes_no(question):
    valid = {"yes": True, "y": True, "no": False, "n": False}

    while True:
        choice = raw_input(question).lower()
        if choice in valid:
            return valid[choice]
        else:
            print "Please respond with 'yes/y' or 'no/n'.\n"

def find_unmatched_packages(path) :
  global unmatched_packages
  for root, dir, files in os.walk(path):
    print root
    for package in fnmatch.filter(files, "*.rpm") :
      if len(fnmatch.filter(cactus_package_list, package)) == 0 and "src.rpm" not in package :
        print "Package",package,"not found in pool"
        unmatched_packages.append([path,package])
    print ""  
    break

def show_usage():
  print """Usage: """,sys.argv[0],""" prod/dev source
Updates the RPM POOL from which the Puppet CACTUS snapshots are created.

required arguments:
   prod/dev   Update the PRODUCTION or DEVELOPMENT POOL directory 
   source     CACTUS release version number OR custom source directory path

"""  

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

if len(sys.argv) != 3 or ( sys.argv[1].lower() != "dev" and sys.argv[1].lower() != "prod" ) :
  show_usage()
  
source="/afs/cern.ch/user/c/cactus/www/release/"+sys.argv[2]+"/slc6_x86_64"

cactus_package_list = [] # to keep track of packages already in the pool
unmatched_packages = []  # packages not found in the pool

if sys.argv[1].lower() == "prod" :
  dest="/afs/cern.ch/user/c/cactus/www/release/POOL/slc6_x86_64"
elif sys.argv[1].lower() == "dev" :
  dest="/afs/cern.ch/user/c/cactus/www/release/POOL_DEV/slc6_x86_64"

print "Source directory : ",source
print "Destination directory : ",dest

if not os.path.isdir(source) :
  print "ERROR: Source directory does not appear to exist!"
  exit(2)

print "Checking POOL contents..."
for root, dir, files in os.walk(dest):
  print root
  for items in fnmatch.filter(files, "*.rpm") :
    cactus_package_list.append(items)
  print ""  
  break
  
print "Looking for new packages..."
find_unmatched_packages(source+"/base/RPMS")
find_unmatched_packages(source+"/updates/RPMS")

if len(unmatched_packages) > 0 :
  print "The following packages have been identified as new:"
  for package in unmatched_packages :
    print package[1]
    
  if sys.argv[1].lower() == "prod" :
    print "\nThis will update the PRODUCTION POOL."
  elif sys.argv[1].lower() == "dev" :
    print "\nThis will update the DEVELOPMENT POOL."
  
  if query_yes_no("Continue? [y/N] ") :
    errors = False
    for package in unmatched_packages :
      print "Creating symlink for",package[1]
      os.chdir(dest)
      try: 
        os.symlink(join(package[0],package[1]), package[1])
      except OSError, e:
        print "OSError:", str(e)
        errors = True
        pass
    if errors :
      print "There were some errors, please check the output." 
    sys.exit(0)
  else :
    print "No modifications made, exiting."
    sys.exit(0)
else :
  print "No new packages found, exiting."
  sys.exit(0)    
    
    
    
