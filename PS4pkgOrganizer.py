# coding=utf-8
#!/usr/bin/python3

import os
import shutil
import sys
import argparse
from fnmatch import fnmatch


parser = argparse.ArgumentParser(description=\
  'Process and organize PS4 pkgs using tags of the names in the following the structure.\
    {PSID} {TYPE} {VERSION} {REGION} GAME_NAME.pkg\
    example: {CUSA23491} {Game} {01.00} {EU} Bloodstained - Curse of the Moon 2.pkg\
    By default, it will process recursively, starting at the location of the script.')

parser.add_argument('-p', '--path', dest = 'root',
                    action = 'store', default = os.path.dirname(os.path.abspath(__file__)),
                    help = 'Specify the location of the pkgs to organize.')

parser.add_argument('-v', '--verbose', dest = 'verbose',
                    action = 'store_true', default = False,
                    help = 'Enable to show relevant information about the organization of the pkgs.')
parser.add_argument('-dr', '--dry_run', dest = 'dry_run',
                    action = 'store_true', default = False,
                    help = 'Do not perform the actions, only show what it would do.')

# Parse arguments and use them as the previously declared variables.
args = parser.parse_args()
root = args.root
dry_run = args.dry_run
if dry_run == True:
  verbose = True
else:
  verbose = args.verbose
#root = os.path.dirname(os.path.abspath(__file__))
pattern = "*.pkg"

# Python3 code here creating class
class pkg:
    def __init__(self, filepath, filename, psid, name, type, region, version):
      self.filepath = filepath
      self.filename = filename
      self.psid = psid
      self.name = name
      self.type = type
      self.region = region
      self.version = version
    def clear(self):
      # Clear pkg properties
      self.psid = ""
      self.name = ""
      self.type = ""
      self.region = ""
      self.version = ""

def printv (value, verbose = True):
  if verbose == True:
    print(value)

def mapParams (game_name):
  # Clear the attributes of the pkg instance to assign new ones
  pkg.clear(pkg)

  param_list = []
  param_start = game_name.find("{") + 1
  param_end   = game_name.find("}")
  while param_start >= 0 and param_end >= 0:
    param = game_name[param_start : param_end]
    game_name = game_name[param_end+2 : len(game_name)]
    if param.find("CUSA") != -1:
      pkg.psid = param
    elif param == "EU" or param == "HONG KONG" or param == "JAP" or param == "US":
      pkg.region = param
    elif param == "Game" or param == "Patch" or param == "Addon":
      pkg.type = param
    else: # param.find("v.") != -1 or param == "":
      pkg.version = param
      name_start = param_end + 1
    param_start = game_name.find("{") + 1
    param_end   = game_name.find("}")
  pkg.name = game_name
  # Set default params to prevent failures
  
  if pkg.region == "":
    pkg.region = "EU"
    printv("pkg region not detected in: " + pkg.name)
  if pkg.type == "":
    pkg.type = "Others"
    printv("pkg type not detected in: " + pkg.name)
  if pkg.version == "":
    if pkg.type != "Addon":
      pkg.version = "v00.00"
      printv("pkg version not detected in: " + pkg.name)

# creating lists
pkg_Game_list = []
pkg_Patch_list = []
pkg_Addon_list = []
pkg_Others_list = []

# List all files with .pkg extension and sort them depending of their name (Game, Patch, Addon or Others)
for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
          pkg.filename = name
          pkg.filepath = path
          mapParams (name.strip(".pkg"))
          if pkg.type == "Game":
            pkg_Game_list.append(pkg(pkg.filepath, pkg.filename, pkg.psid, pkg.name, pkg.type, pkg.region, pkg.version))
          elif pkg.type == "Patch":
            pkg_Patch_list.append(pkg(pkg.filepath, pkg.filename, pkg.psid, pkg.name, pkg.type, pkg.region, pkg.version))
          elif pkg.type == "Addon":
            pkg_Addon_list.append(pkg(pkg.filepath, pkg.filename, pkg.psid, pkg.name, pkg.type, pkg.region, pkg.version))
          else:
            pkg_Others_list.append(pkg(pkg.filepath, pkg.filename, pkg.psid, pkg.name, pkg.type, pkg.region, pkg.version))

# Check each Game entry in the game list, create a folder to store using the format "Name [Region] [PSID]
# and move each other file with the same ID as the game to the same folder
def checkListContent(elementlist):
  for element in elementlist:
    if pkg_game.psid == element.psid:
      OpStatus = ""
      if full_game_dir != element.filepath:
        if dry_run == False:
          shutil.move(os.path.join(element.filepath, element.filename), new_game_dir)
      else:
        OpStatus = (" (File not moved)")
      # Remove the element from the list to prevent it to be processed again
      printv(' ├─ ' + os.path.join(element.filepath, element.filename) + OpStatus, verbose)
      elementlist.remove(element)

for pkg_game in pkg_Game_list:
  new_game_dir = pkg_game.name + " [" + pkg_game.region + "]" + " [" + pkg_game.psid + "]"
  full_game_dir = os.path.join(root, pkg_game.name + " [" + pkg_game.region + "]" + " [" + pkg_game.psid + "]")
  OpStatus = ""
  if full_game_dir != pkg_game.filepath:
    if dry_run == False:
      if not(os.path.exists(full_game_dir)):
        os.mkdir(full_game_dir)
        shutil.move(os.path.join(pkg_game.filepath, pkg_game.filename), full_game_dir)
  else:
    OpStatus = (" (File not moved)")
  printv(os.path.join(pkg_game.filepath, pkg_game.filename) + " -> \n" + full_game_dir + OpStatus, verbose)
  # Check the Patches
  checkListContent(pkg_Patch_list)
  # Check the Addons
  checkListContent(pkg_Addon_list)
  # Check the other files that might have been procesed and are not Patch nor Addon
  checkListContent(pkg_Others_list)

