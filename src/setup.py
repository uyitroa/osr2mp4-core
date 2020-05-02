import subprocess
import sys


def install(package):
	subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def uninstall(package):
	subprocess.check_call([sys.executable, "-m", "pip", "uninstall", package])


def read_requirements():
	requirements = open("../requirements.txt").read().split("\n")
	if requirements[-1] == '':
		requirements = requirements[:-1]
	return requirements


def setup():
	requirements = read_requirements()
	print("Ignore warning")
	uninstall("pil")
	uninstall("pillow")

	for r in requirements:
		install(r)

	have_pillowsimd = False
	try:
		from PIL import Image
		have_pillowsimd = True
	except ModuleNotFoundError as e:
		print("You don't have Pillow-SIMD installed")
		print("Download it here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow-simd")
	except Exception as e:
		print(e)


setup()
