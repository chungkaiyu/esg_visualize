from esg_evaluator import *
from pathlib import Path
import os
file_path = os.getcwd() + '/static/input'
#print(file_path)
dp = DocProcessor()
text = dp.get_file_text(str(file_path + '/Test9-2019-IntelCSR-Report.pdf'))
print(text)