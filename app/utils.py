# app/utils.py
import numpy as np

def calcular_similitud(embedding1, embedding2):
    """
    Retorna la similitud coseno entre dos vectores. Más cercano a 1 = más similar.
    """
    e1 = embedding1 / np.linalg.norm(embedding1)
    e2 = embedding2 / np.linalg.norm(embedding2)
    return np.dot(e1, e2)
