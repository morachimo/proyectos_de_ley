from .base import *
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
print(TESTING)
