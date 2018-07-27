#!/bin/bash

# Build up the bbr user so that it can run the site.  This user cannot sudo.

chmod 600 .pgpass

git clone https://github.com/BrassBandResults/bbr4.git

# create virtualenv