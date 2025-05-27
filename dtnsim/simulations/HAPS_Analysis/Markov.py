from quickpomdps import QuickPOMDP
import copy
from julia.api import Julia
jl = Julia(compiled_modules=False)

from julia import Pkg
Pkg.add(["POMDPs", "POMDPTools", "Distributions", "QMDP", "MCTS"])

from julia.Main import Float64
from julia.POMDPs import solve, pdf
from julia.QMDP import QMDPSolver
from julia.MCTS import MCTSSolver, action_info
from julia.POMDPTools import stepthrough, alphavectors, Uniform, Deterministic
from julia.Distributions import Normal

def state():
    states = [] 
    statesT = [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0]]
    for element in statesT:
        states.append(copy.deepcopy(element))

    for i in range(10):
        for i in range(len(statesT)):
            statesT[i][5] += 1
        for element in statesT:
            states.append(copy.deepcopy(element))
    states.append([0,0,0,0,0,0])
    return states


def action():
    ["keep","toHAGS1","toHAGS2","ToGS1","ToGS2"]

def transition(s, a):
    if a == "keep":
        s[5] += 1
        return s
    elif a == "toHAGS1":
        s[0] -= 1
        s[1] += 1
        return s
    elif a == "toHAGS2":
        s[1] -= 1
        s[2] += 1
        return s
    elif a == "toGS1":
        fail = copy.deepcopy(s)
        fail[5] += 1
        success = copy.deepcopy(s)
        success[2] -= 1
        success[3] += 1
        return zip([fail, success],[0.2,0.8])
    elif a == "toGS2":
        fail = copy.deepcopy(s)
        fail[5] += 1
        success = copy.deepcopy(s)
        success[3] -= 1
        success[4] += 1
        return zip([fail, success],[0.6,0.4])
    elif reward(s) > 0:
        return [0,0,0,0,0,0]

def reward(s, a, sp):
    if s == [0,0,0,0,0,0]:
        return 10 
    else:
        return -1.0
    
def observation(s,a,sp):
    return s

def is_terminal(state):
    # Example condition to check if a state is terminal
    return state == [0,0,0,0,0,0]

mcts_mdp = QuickPOMDP(
    states = state,
    statetype = list,
    actions = action,
    actiontype = str,
    isterminal = is_terminal,
    transition = transition,
    observation = observation,
    obstype = list,
    reward = reward,
    initialstate = state
)

mcts_solver = MCTSSolver(n_iterations=50,
	                     depth=20,
	                     exploration_constant=5.0,
                         enable_tree_vis=True)
mcts_planner = solve(mcts_solver, mcts_mdp)

a, info = action_info(mcts_planner)