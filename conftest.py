import sys
import os

# Make the colivingscore package directory available so that `from pdf.generate_report`
# resolves correctly (app.py is run from inside colivingscore/ in production).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "colivingscore"))
