# Execute in root dir. 
# For the docs:
jupyter nbconvert --to markdown --output-dir=docs/source "src/test_demos/Demo - PipeNet.ipynb" "src/test_demos/Demo - Fault Diagnosis.ipynb" "src/test_demos/Demo - Pedestrian.ipynb" "src/test_demos/Demo - Scripted Model Construction.ipynb" "src/test_demos/Demo - Trace Parser.ipynb"
jupyter nbconvert --to markdown --output-dir=docs/source --output=README.md "src/test_demos/Doc_Readme.ipynb"

# For the readme.
jupyter nbconvert --to markdown --output-dir=. --output=README.md "src/test_demos/Doc_Readme.ipynb"