# 產生預測rating的json檔
from esg_evaluator import *

input_file = "./static/tmp/2020_Applied_Request_W3.csv"
output_file = "./static/input/applied_request.json"

model = PredictModel()
model.getPredict_bycsv_tojson(input_file, output_file)
