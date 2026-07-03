# Modules
import numpy as np
import sympy as sp
from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# System Modules
from matricies import dh_matrix

PI = np.pi

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

        self.line, = self.ax.plot([], [], [], 'o-', lw=4, color='teal')

        self.sliders = []
        for i in range(3):
            self.make_slider(i)
        
        self.update(None) # Draw extra first frame to initialize

    def make_slider(self, index):
        y_pos = 0.05 + index * 0.05

        slider_ax = self.fig.add_axes([0.2, y_pos, 0.6, 0.03])
        slider = Slider(
            ax=slider_ax,
            label=f"Theta {index + 1}",
            valmin=-2*PI,
            valmax=2*PI,
            valinit=0.0
        )
        slider.on_changed(self.update)
        self.sliders.append(slider)
    
    def update(self, val):
        slider_values = [s.val for s in self.sliders]
        T_matrices = self.robot.solve_exact(slider_values)

        # Line goes from global (0, 0, 0) to the end affector
        # The 4th column of each T matrix is a tranlation vector
        # Broken with sympy matrix return
        x = [0, T_matrices[0, 3]]
        y = [0, T_matrices[1, 3]]
        z = [0, T_matrices[2, 3]]

        self.line.set_data(np.array(x), np.array(y))
        self.line.set_3d_properties(np.array(z))
        self.fig.canvas.draw_idle()
        

class FK_3DOF:
    def __init__(self):
        """Forward Kinematic Solver.

        Methods:
            solve_fast(slider_values):
                Optimizes Function for faster, less precise floating values.
            solve_exact(slider_values, format='numpy'):
                Calculates decimal points for a more precise result.
                Returns sympy or numpy matrix
        """

        self.sym = {f'theta{i}': sp.symbols(f'theta{i}') for i in range(1,4)}

        # Create DH Matrices (Chain Links) for Forward Kinematics
        self.T01 = dh_matrix(a=2,  d=0, alpha=sp.pi/2, theta=self.sym['theta1'])
        self.T12 = dh_matrix(a=10, d=0, alpha=0, theta=self.sym['theta2'])
        self.T23 = dh_matrix(a=8,  d=0, alpha=0, theta=self.sym['theta3'])
        self.T03 = self.T01 @ self.T12 @ self.T23 # Chain by multiplication

        self.calc_fast = sp.lambdify(([v for v in self.sym.values()]), self.T03, 'numpy')

    def solve_fast(self, values:list):
        return self.calc_fast(*values)

    def solve_exact(self, values:list, format:str='numpy', dtype=float):
        matrix = self.T03.subs({val: values[i] for i, val in enumerate(self.sym)})
        return np.array(matrix, dtype=dtype) if format=='numpy' else matrix


if __name__ == "__main__":
    robot = FK_3DOF()
    app = Display(robot)
    plt.show()