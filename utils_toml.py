import os
import sys
import toml
import logging

# load toml file
def load_toml(path):
    if not os.path.exists(path):
        logging.error("File not found: %s" % path)
        sys.exit(1)
    with open(path, "r") as f:
        return toml.load(f)
