# Execute in root dir. 
# Required packages: nbconvert pandoc
# For the docs:
jupyter nbconvert --to markdown --output-dir=docs/source "src/test_demos/Demo1-PipeNet.ipynb" "src/test_demos/Demo2-Pedestrian.ipynb" "src/test_demos/Demo3-Fault Diagnosis.ipynb" "src/test_demos/Demo4-Scripted Model Construction.ipynb" "src/test_demos/Demo5-Trace Parser.ipynb"
jupyter nbconvert --to markdown --output-dir=docs/source --output=README.md "src/test_demos/Doc_Readme.ipynb"

# For the readme.
jupyter nbconvert --to markdown --output-dir=. --output=README.md "src/test_demos/Doc_Readme.ipynb"