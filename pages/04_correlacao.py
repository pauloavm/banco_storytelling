"""
04_correlacao.py
----------------
Página 4: Correlação entre atividade bancária e indicadores macroeconômicos.
"""

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.etl import kpi_correlacao_macro
from src.viz import plot_correlacao_

