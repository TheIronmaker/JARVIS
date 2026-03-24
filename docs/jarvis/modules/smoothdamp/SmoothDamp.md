# Understanding the Math
## Variables:
### Setup: Constants
- `f` Frequency response time: This is the oscillation period. Range: 
- `z` Damping ratio: How far the smooth damp will dampen
- `r` Response: How quickly it will respond
---
- `T` Time step between updates (0.01 = 100Hz)
- `R` Amount of decimals rounded to
### Prep Calculations: Damping Coefficients
- `k1` Frequency derived from `f`
- `k2` Damping ratio derived from `z`
- `k3` Response derived from `r`
### Input: Data Variables
- `x` The actual input value provided (raw, un-smoothed data)
- `xp` Previous x value (used to calculate velocity if not explicitly provided)
### Output Returns
- `y` The smoothed output value: return value
- `dy` Velocity/derivative of `y`: how fast y is changing
- `acc` Acceleration: how fast velocity (`dy`) is changing

## Math and Process:
1. Calculate velocity: $xd = \frac{x-xp}{T}$ (if xp not provided)
2. Update position: $y = y+T\cdot dy$ (move output by velocity)
3. Calculate acceleration: $acc = \frac{x + k3\cdot xd - y - k1\cdot dy}{k2}$
    - Pulls $y$ toward the input $x$
    - Resists based on current velocity $k1\cdot dy$
    - Responds based on input velocity $k3\cdot xd$
4. Update velocity: $dy = dy+T\cdot acc$
    - Velocity changes by acceleration
5. Return smoothed $y$
    
## Result
Smooth exponential following of input with controllable lag/response

# Code
## Smooth Damp Array
### Data Storage

All of the data is stored in Numpy arrays. This code is built out to the Nth degree, so any level of data can be stored in a nested list format.

---
There are two main data storage points.
1. `self.defaults` This stores the unchanged `f`, `z`, and `r` values or the array.
2. `self.k` This stores the calculated `k1`, `k2`, and `k3` values or the array based from the `f`, `z`, and `r` values.

## Receiving data
### Input: X
The code receives the `x` value. From this, it is either provided with a `xp` (previous iteration's x value) or it calculates it from the available data. Then, we shift to `y` values. This is no longer the original data given, but out newly calculated smoothed out data.
### Output: Y
There are three y values:
- `y` The actual smoothed out value derived from the `x` data.
- `dy` The derivative of `y`. This is the slope of the `x` data and represents the speed of `x`
- `acc`, or `acceleration` This is the second derivative of the `x` data, and represents the acceleration of `x`.

With all of this data combined, and some predefined constants to find the final values.<br>*Note: The Predefined constants are variables when using functions to change them*

