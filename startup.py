import sys
import pandas as pd
import numpy as np



def configure(repl):

    repl.confirm_exit = False

try:
    from ptpython.repl import embed
except ImportError:
    print("ptpython is not available: falling back to standard prompt")
else:
    sys.exit(embed(globals(), locals(), configure=configure, vi_mode=True))
