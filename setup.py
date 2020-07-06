import setuptools

with open("pypiREADME.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt", "r") as fr:
	requirements = fr.read().split("\n")
	if requirements[-1] == "":
		requirements = requirements[:-1]

setuptools.setup(
	name="osr2mp4",
	version="0.0.1b4",
	author="yuitora",
	author_email="shintaridesu@gmail.com",
	description="Convert osr replay file to video file",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/uyitroa/osr2mp4-core",
	packages=setuptools.find_packages(),
	install_requires=requirements,
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		],
	python_requires='>=3.6',
)
