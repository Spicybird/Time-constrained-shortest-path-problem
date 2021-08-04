# Time-constrained-shortest-path-problem
Python implementation of Lagrangian relaxation for time-constrained shortest path problem.

## Time-constrained shortest path problem

Given a network, try to find the shortest path from an origin node to a destination node while the total traversal time cannot exceed a predefined threshold. The total traversal time constraint is a side constraint which makes the problem difficult to be solved. In this repository, we use Python to implement Lagrangian relaxation to solve such a problem. Note that the Lagrangian multiplier is updated by sub-gradient technique.

## How to use this source code?

Run main.py. The console will automatically show messages for you to find the output results.

## TODOList
- [x] Refactor the structure of the code. 
- [x] Implement output process and encpasulte the process into a function.
- [ ] Implement a heuristic for attain an upper bound solution through the information provided by the lower bound solution.
- [ ] Visualization: gap evolution curve.
- [ ] Find more complicated and solvable numerical examples (maybe chapter exercises from MIT Ahuja textbook and RCSPP can provide some examples).
- [ ] Integrate branch-and-bound algorithm with Lagrangian relaxation.

## Reference
[1] R. K. Ahuja, T. L. Magnanti, and J. B. Orlin, Network Flows: Theory, Algorithms, and Applications. Prentice Hall, 1993.
[2] P. Li, “Path4GMNS Package,” 2021. [Online]. Available: https://github.com/jdlph/Path4GMNS
[3] airqzhu, "lagrangian-relaxation, GitHub Repository" https://github.com/airqzhu/lagrangian-relaxation
