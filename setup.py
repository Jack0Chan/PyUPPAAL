import setuptools
import re

def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open('./src/pyuppaal/__init__.py').read())
    return result.group(1)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyuppaal",
    version = get_property('__version__', 'pyuppaal'),
    author="Jack0Chan",
    author_email="",
    description="A research tool that can simulate, verify or modify UPPAAL models with python. It can also help to analyze counter-examples in .xml format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jack0Chan/pyuppaal",
    project_urls={
        "Bug Tracker": "https://github.com/Jack0Chan/pyuppaal/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        #   'myst_parser',# 'Sphinx -> markdown'
          # ^^^ Not sure if this is needed on readthedocs.org
          # 'something else?',
          ],
)