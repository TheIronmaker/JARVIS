
## Things to come back to
elasticity, backlash, friction, and hysteresis

## Math

$\begin{bmatrix}x'\\ y'\end{bmatrix} = \begin{bmatrix}\cos(\theta) & -\sin(\theta)\\\sin(\theta)&\cos(\theta)\end{bmatrix}\begin{bmatrix}x\\y\end{bmatrix}$

$\displaystyle{\begin{aligned}x'&=x\cos \theta -y\sin \theta \,\\y'&=x\sin \theta +y\cos \theta \,\end{aligned}}$

---
# Configuration
Each joint will have four parameters: `a` (link length), `d` (offset along z), `α` (twist), `θ` (joint angle — output variable to be solved for)
