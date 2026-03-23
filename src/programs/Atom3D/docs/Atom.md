# `def` Sample R
### Input variables
- `n` - from `self.n`
- `l` - from `self.l`
- `a0` - from `self.a0`

### Single Values:
- `N` = 4096
- `rMax` = $10\cdot n^2\cdot\text{a0}$
- `dr` = $\frac{\text{rMax}}{N-1}$
- `k` = $n-l-1$
- `alpha` = $2l+1$
- `norm`: Take $(\frac{2}{n\cdot\text{a0}})^3\cdot\frac{\Gamma(n-l)}{2n\cdot\Gamma(n+l+1)} \text{ and identity } \Gamma(a) = (a-1)! \rightarrow(\frac{2}{n\cdot\text{a0}})^3\cdot\frac{(n-l-1)!}{2n\cdot(n+l)!}$

### Arrays - must be numpy arrays of `dtype = np.float32`
- `r`: numpy array calculated from $i\cdot \text{dr}$ (length 4096, or N)
- `rho` (ρ): numpy array = $\frac{2r}{n\cdot \text{a0}}$
- `L`: Array of length [N,] formed from a compilation of logic and equations (detailed explanation below)
- `R` $=\sqrt{\text{norm}}\cdot e^{-\rho/2}\cdot\rho^l\cdot L$
- `pdf` $=r^2\cdot R^2$ both `r` and `R` are arrays
- `cfd` = a running sum of `pdf`, divided by the largest (last) value of `pdf`: $S_k=\sum_{i=1}^{k}{x_i}$
- `u` = random number array within range [0, 1], size (N,). Each particle has its own random value.
- `idx` = C++ `lower_bound`, python `np.searchsorted` cross reference `cfd` and `u` to refine `u` random values to a set pattern calculated with `cdf`
- `return value` $=\text{idx}\cdot\text{dr}$

## Code Explanations
### Elimination of first `for` loop
C++ code loops through values of range (0, N) with an increment pattern of 1.
Since N = 4096, there are 4096 iterations of values the code processes and calculates.
In the pursuit of vectorized calculations and an array based approach, an array of 4096 values may serve the purpose of a `for` loop.
<br> `np.linspace(a, b, N)` serves to create this array. a = starting value (0), b = maximum value (rMax), and N = number of samples between min and max (N=4096)
<br> Translation: `for (int i = 0; i < N; ++i)` → `r = np.linspace(0, rMax, N, dtype=np.float32)`

### Reduction of L based loop
`L` has three paths of calculation based on `k`. ($k = n - l - 1$ and is a constant)
- If `k=0` then `L=1`.
- If `k=1` then $L=1+\alpha-\rho$
- If `k>1` a for loop of (2, k + 1) starts, and: $L=(2j-1+\alpha-\rho)\cdot \text{Lm1}-(j-1+\alpha)\cdot\text{Lm2}\cdot j^{-1}$ then $\text{Lm2}=\text{Lm1}$ and $\text{Lm1}=L$

Details of `k>1`:
<br> `Lm1` is derived from $\text{Lm1}=1+\alpha-\rho$, and since rho is an array, Lm1 is also an array.
<br> C++ sets $\text{Lm2} = 1$ as an initial value. A numpy ones-array has the same effect, but creates N values, allowing for all calculations at once. Python: `np.ones(N, dtype=np.float32)`
<br> Next, a loop iterates from range `2` to `k+1`. Constant `k` allows simple iteration over dataset. `k` represents the number of radial nodes, which python should be able to handle in a `for loop`.
<br> Loop calculations: `L` is set to its calculated value, then Lm2 array becomes Lm1 array, and Lm1 array becomes L array.
<br> Once the small loop is complete, the final array value of `L` is known, and calculations may proceed.

### pdf to cfd
The C++ version loops 4096 times to build a `cdf`. At first, it calculates a standalone `pdf` value, and then adds that to a `sum` of all previous `pdf` values. This is a `running sum`. This sum is saved to the cdf for each value.  
The python version handles the running sum after the `pdf` calculations. Once all `pdf` values are known, a numpy `cumsum` operation is applied to the `pdf`. This tallies the `running sum` from pure un-summed values.  
The final step is to normalize the data and set the largest value to `1`. Since the last summed value is the largest, the dataset should be divided by that number to fit the range [0, 1]. It is at this point that the `cdf` of length 4096 is built.

### Final calculations
A fresh array of random [0, 1] values is made for the total number of particles. This array is completely random, and not set to any pattern. By using C++ `lower_bound` or python `np.searchsorted`, the random `u` values are set to a pattern calculated with the `cdf` values. In essence, the random values are rounded to a custom mask, called the `cdf`.  
Finally, this new `u` value is multiplied by the `dr` scalar, and returned as the final sampleR array.

# `def` Sample Theta
## Incomplete documentation
### Single Values
- `N` = 2048
- `dtheta` $=\frac{\pi}{N-1}

### Array Values
- `theta` $\theta$: (array of random numpy range [0, 1], length N) x `dtheta`
- `x` $=\cos(\theta)$   
- `Pmm`: numpy ones array of length N
- `Pll` $=(2\text{ll}-1)\cdot xP_{m1m}-(\text{ll}+m-1)\cdot P_{mm}\cdot(\text{ll}-m)^{-1}$
- `pdf` = $\sin(\theta)\cdot P_{lm}^2$

# `def` Sample Phi
An array of random values is generated and the function returns $2\cdot\pi\cdot\text{array}$

# `def` inferno($r, \theta, \phi$)
### Input variables
- `n` - from `self.n`
- `l` - from `self.l`
- `a0` - from `self.a0`

### Single Values:
- `k` $=n-l-1$
- `alpha` $\alpha=2l+1$

### Arrays:
- `rho` $\rho=\frac{2r}{n\cdot\text{a0}}$
- `L` Array of length [N,], built out from many calculations
- `norm`: Take $(\frac{2}{n\cdot\text{a0}})^3\cdot\frac{\Gamma(n-l)}{2n\cdot\Gamma(n+l+1)} \text{ and identity } \Gamma(a) = (a-1)! \rightarrow(\frac{2}{n\cdot\text{a0}})^3\cdot\frac{(n-l-1)!}{2n\cdot(n+l)!}$
- `R` $=\sqrt{\text{norm}}\cdot e^{-\rho/2}\cdot\rho^l\cdot L$
- `radial` $=R^2$
- `x` $=\cos{(\theta)}$
- `Pmm`: an array calculated in steps:
  - `Pmm` $=1$
  - If $m>0$, `somx2` $=\sqrt{1-x}\cdot\sqrt{1+x}$
  - `fact` $=1$
  - while $i=[1, m]$, `Pmm` $=P_{mm}\cdot(-\text{fact})\cdot\text{somx2}$ then fact = fact + 2
  - Alternate `Pmm` loop: fact = $[1, 2m]$ with step size = 2, `Pmm` $=P_{mm}\cdot(-\text{fact})\cdot\text{somx2}$
- `Plm`:  an array calculated in steps:
  - `Plm` = `Pmm`
  - If `l != m`:
  - `Pm1m` $=x\cdot(2m+1)\cdot P_{mm}$
  - If `l = m + 1`: $P_{lm} = P_{m1m}$
  - Else (`l != m + 1`): Loop variable: `ll` range $[m+2, l+1]$
  - And: `Pll` $=((2ll - 1) \cdot x \cdot P_{m1m} - (ll + m - 1) \cdot Pmm) / (ll - m)$
  - And: $\text{Lm2}=\text{Lm1}$
  - And: $\text{Lm1}=L$
  - Finally: `Plm` = `Pm1m`
- `angular` = $P_{lm}^2$
- `intensity` = radial $\cdot$ angular

### L calculation
Case 1 $k<1$, $L$ = array of value `1` and size [N,] where `N` is the number of particles.<br>
Case 2 $k=1$, $L=1+\alpha-\rho$<br>
Case 3 $k>1$, $L=(2i-1+\alpha-\rho)\cdot L_{m1}-(i-1+\alpha)\cdot L_{m2}\cdot i^{-1}$ then $\text{Lm2}=\text{Lm1}$ and $\text{Lm1}=L$ while $i=[2,3,...,k]$

### Plm Calculation
`Pmm` begins as an array of value 1, size $[N]$
