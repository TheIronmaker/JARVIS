# Modules
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from jarvis_kinematics.matricies import dh_matrix, PI
from jarvis_core.databus import pub

class Display:
    def __init__(self, robot):
        self.robot = robot

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_aspect('equal', adjustable='box')

        self.ax.set_xlim3d([-20, 20])
        self.ax.set_ylim3d([-20, 20])
        self.ax.set_zlim3d([-20, 20])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.size = len(robot.params)
        self.line, = self.ax.plot([], [], [], 'o-', lw=4, color='teal')
        self.sliders = [self.make_slider(i, self.update, f'Theta {i+1}', -2*PI, 2*PI) for i in range(self.size)]

        self.update(None) # Draw starter frame to initialize

    def make_slider(self, index, func, label=None, min=-1, max=1, init=0.0):
        slider_ax = self.fig.add_axes([0.2, 0.05 + index * 0.05, 0.6, 0.03])
        slider = Slider(
            ax=slider_ax,
            label=label if label else f"Slider {index}",
            valmin=min,
            valmax=max,
            valinit=init
        )
        slider.on_changed(func)
        return slider
    
    def update(self, val):
        slider_values = [s.val for s in self.sliders]

        matrix = np.array([self.robot.solve_fast[i](*slider_values) for i in range(self.size)])
        xs = []
        ys = []
        zs = []
        
        for mat in matrix:
            xs.append(mat[0, 3])
            ys.append(mat[1, 3])
            zs.append(mat[2, 3])
        
        #coords = matrix[:, :self.size, 3]

        #for i in range(self.size):
        self.line.set_data(xs, ys)
            #self.line.set_data([coords[i, 0]], [coords[i, 1]])
        self.line.set_3d_properties(zs)# [coords[i, 2]]

        self.fig.canvas.draw_idle()
        

class FK:
    def __init__(self, params, mask):
        """Forward Kinematic Solver

        Args:
            params: D-H joint configurations
            mask: Replaces selected values with SciPy Symbol variable

        Methods:
            solve_fast(slider_values):
                Optimizes Function for faster, less precise floating values.
            solve_exact(slider_values, format='numpy'):
                Calculates decimal points for a more precise result.
                Returns sympy or numpy matrix
        """

        param_names = ['a', 'd', 'alpha', 'theta']
        self.params = [[sp.Symbol(f'{param_names[i]}_{j}') if sym else params[j][i] for i, sym in enumerate(j_mask)] for j, j_mask in enumerate(mask)]
        free_symbols = [sym for row in self.params for sym in row if isinstance(sym, sp.Symbol)]
        self.T = [dh_matrix(*joint) for joint in self.params]
        self.T_mult = [self.T[0]]
        for i in range(1, len(self.T)):
            self.T_mult.append(self.T_mult[-1] @ self.T[i])
        
        # Solves full chain each time, so needs to keep previous work instead. Example: T_0 is calculated for each joint.
        self.solve_fast: list[function] = [sp.lambdify(free_symbols, joint, 'numpy') for joint in self.T_mult]

params = np.array([
    [0, 2, sp.pi/2, 0],
    [10, 0, 0, 0],
    [8, 0, 0, 0],
])

mask = np.array([
    [False, False, False, True],
    [False, False, False, True],
    [False, False, False, True]
])

if __name__ == "__main__":
    robot = FK(params, mask)
    app = Display(robot)
    plt.show()