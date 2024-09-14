import sys
import os

# Get the parent directory of 'tests'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the Python path
sys.path.insert(0, parent_dir)