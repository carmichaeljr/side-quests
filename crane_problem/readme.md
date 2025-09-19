You are a crane operator on a construction site. Unfortunately, your crane is a
bit old and rusty. The steering is broken so you can only drive in a straight
line. Your crane has an arm of length _l_ which may extend any distance from 0
to _l_. However, the arm is not sturdy enough change length while carrying an
object. In addition, the engine is not strong enough to drive forward while
carrying an object. Once you have picked up an object, your crane arm can
rotate a full 360 degrees before setting it down.

You are asked to move a set objects in the construction site from their initial
locations to their desired locations. These objects are delicate so you may
only lift up and set down each object once. You must determine if it is
possible to move all objects to their desired locations while driving along a
single straight line through the construction site.

The first line of input contains two space separated numbers: _l_ and _n_. _l_
is a float representing the maximum length of your crane arm. _n_ is an integer
representing the total number of objects to move. The next _n_ lines are each 4
numbers x_i y_i x_d y_d representing the xy coordinates of the initial point
and destination point for each object. If it possible to move all objects while
driving along a single straight line, print POSSIBLE. Otherwise, print
IMPOSSIBLE.
