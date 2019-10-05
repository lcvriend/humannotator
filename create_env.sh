#!/bin/bash
conda env create -f environment.yml
source activate humannotator
python -m ipykernel install --user --name humannotator --display-name "humannotator"
