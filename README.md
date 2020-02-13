# CribbageLearning
Machine Learning project for CptS 437 to program a relatively smart Cribbage AI

# Results
## Throwing 
Most recent results:
    
    ACTUAL 11.002982246376813
    
    RANDOM 9.354994685990336

Using a decision forest with AdaBoost, the AI performed significantly than random. 

## Pegging
We attempted to use reinforcement learning in order to implement pegging, however the sample space proved to be too large and because of that, reinforcement learning did not produce the expected results.

## TODO:
- Fix the bugs in the Cribbage engine itself
- Maybe turn the Cribbage engine into a submodule? Perhaps the two programs are unnecessarily coupled
- Redo the pegging AI using a more programmatic, heuristic approach instead of a machine learning one
