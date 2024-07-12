import sys
#sys.path.append("/opt/homebrew/lib/python3.11/site-packages/pylotec")

import site
import os
import pylotec

site_packages_path = site.getsitepackages()[0]

sys.path.append(os.path.join(site_packages_path, 'pylotec'))

import pylotec
