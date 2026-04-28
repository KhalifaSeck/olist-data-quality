"""Configuration pytest — ajoute la racine au sys.path."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitoring'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))