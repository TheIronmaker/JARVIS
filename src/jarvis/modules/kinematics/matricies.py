import numpy as np
import sympy as sp
from functools import reduce

# Rotation Matrix 2D and 3D
rotate_2D = lambda theta: np.array([
    [np.cos(theta), -np.sin(theta)],
    [np.sin(theta), np.cos(theta)]])

""" Individual Transformations / Rotations """
alpha, beta, gamma, theta = sp.symbols('alpha beta gamma theta')

trans_xa = sp.Matrix([
    [1, 0, 0, alpha],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]])

trans_yb = sp.Matrix([
    [1, 0, 0, 0],
    [0, 1, 0, beta],
    [0, 0, 1, 0],
    [0, 0, 0, 1]])

trans_zc = sp.Matrix([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, gamma],
    [0, 0, 0, 1]])

rot_xalpha = sp.Matrix([
    [1, 0, 0, 0],
    [0, sp.cos(alpha), -sp.sin(alpha), 0],
    [0, sp.sin(alpha),  sp.cos(alpha), 0],
    [0, 0, 0, 1]])

rot_ybeta = sp.Matrix([
    [sp.cos(beta), 0, sp.sin(beta), 0],
    [0, 1, 0, 0],
    [-sp.sin(beta), 0, sp.cos(beta), 0],
    [0, 0, 0, 1]])

rot_zgamma = sp.Matrix([
    [sp.cos(gamma), -sp.sin(gamma), 0, 0],
    [sp.sin(gamma),  sp.cos(gamma), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]])

# Assemble Transformation from a list: [trans_xa, rot_ybeta]
def as_tr(transformations:list) -> np.ndarray:
    result = np.eye(4)
    if len(transformations) != 0:
        for T in transformations:
            result = result @ T
    return result

# Alternate Version
def as_tr_reduce(transformations:list) -> np.ndarray:
    return reduce(lambda x, y: x @ y, transformations)


""" Universal 3D Transformation Matrix Generator """
# optional: dh_matrix = lambda: a, d, aplha, theta: np.array(...)
def dh_matrix(a, d, alpha, theta):
    return sp.Matrix([
        [sp.cos(theta), -sp.sin(theta)*sp.cos(alpha),  sp.sin(theta)*sp.sin(alpha), a*sp.cos(theta)],
        [sp.sin(theta),  sp.cos(theta)*sp.cos(alpha), -sp.cos(theta)*sp.sin(alpha), a*sp.sin(theta)],
        [0,              sp.sin(alpha),               sp.cos(alpha),              d],
        [0,              0,                           0,                          1]
    ])
