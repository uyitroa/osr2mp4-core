import setuptools
import sys
import subprocess
import os
# from distutils.command.install import install
try:
	from wheel.bdist_wheel import bdist_wheel
except ImportError:
	subprocess.call([sys.executable, "-m", "pip", "install", "wheel", "--upgrade"])
	from wheel.bdist_wheel import bdist_wheel


class cd:
	"""Context manager for changing the current working directory"""

	def __init__(self, newPath):
		self.newPath = os.path.expanduser(newPath)

	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)

	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)


def compile_():
	if os.name == 'nt':
		return
	try:
		from Cython.Distutils import build_ext
	except ImportError:
		subprocess.call([sys.executable, "-m", "pip", "install", "cython"])

	curpath = os.path.dirname(__file__)
	curvepath = os.path.join(curpath, "osr2mp4/ImageProcess/Curves/libcurves/")
	with cd(curvepath):
		subprocess.check_call([sys.executable, "setup.py", "build_ext", "--inplace"])


class new_install(bdist_wheel):
	def run(self):
		compile_()
		bdist_wheel.run(self)


with open("pypiREADME.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt", "r") as fr:
	requirements = fr.read().split("\n")
	if requirements[-1] == "":
		requirements = requirements[:-1]
print(sys.argv)
setuptools.setup(
	name="osr2mp4",
	version="0.0.5.a1",
	author="yuitora",
	author_email="shintaridesu@gmail.com",
	description="Convert osr replay file to video file",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/uyitroa/osr2mp4-core",
	packages=setuptools.find_packages(exclude=("tests/",)),
	install_requires=requirements,
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
	cmdclass={'bdist_wheel': new_install}
)
