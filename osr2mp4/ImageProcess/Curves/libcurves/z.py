import subprocess
import sys


subprocess.check_call([sys.executable, "setup.py", "build_ext", "--inplace"])
