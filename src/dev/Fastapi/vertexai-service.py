import numpy
import pandas as pd
# import google generative AI API
import google.generativeai as genai  


class VertexAIService:
    def __init__(self):
        self.data = pd.read_csv("data.csv")

    def predict(self, data):
        return numpy.mean(data)