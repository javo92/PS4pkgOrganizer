# coding=utf-8
#!/usr/bin/python3

import os
import shutil

from fnmatch import fnmatch

dry_run = 0
root = './'
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
    print("pkg region not detected in: " + pkg.name)
  if pkg.type == "":
    pkg.type = "Game"
    print("pkg type not detected in: " + pkg.name)
  if pkg.version == "":
    if pkg.type != "Addon":
      pkg.version = "v00.00"
      print("pkg version not detected in: " + pkg.name)

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
      if dry_run == 0:
        print(os.path.join(element.filepath, element.filename) + " -> " + new_game_dir)
        shutil.move(os.path.join(element.filepath, element.filename), new_game_dir)
      # Remove the element from the list to prevent it to be processed again
      elementlist.remove(element)

for pkg_game in pkg_Game_list:
  new_game_dir = pkg_game.name + " [" + pkg_game.region + "]" + " [" + pkg_game.psid + "]"
  print(os.path.join(pkg_game.filepath, pkg_game.filename) + " -> " + new_game_dir)
  if dry_run == 0:
    if not(os.path.exists(new_game_dir)):
      os.mkdir(new_game_dir)
      shutil.move(os.path.join(pkg_game.filepath, pkg_game.filename), new_game_dir)
  # Check the Patches
  checkListContent(pkg_Patch_list)
  # Check the Addons
  checkListContent(pkg_Addon_list)
  # Check the other files that might have been procesed and are not Patch nor Addon
  checkListContent(pkg_Others_list)

