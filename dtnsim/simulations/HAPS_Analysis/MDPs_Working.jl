using QuickPOMDPs, POMDPs, POMDPTools, QMDP, MCTS, BasicPOMCP, D3Trees, DiscreteValueIteration
using Parameters

global indexOfLeos = [6]
global indexOfHags = [3,5]
global maxOfTime = 100

function contactPlanGatherer()
    # Read the file
    file_path = "/home/benoitcoeugnet/git/dtnsim/dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/test.txt"
    file_contents = read(file_path, String)
    contactList = [[],[]]
    # print(file_contents)
    
    # Process the file contents
    for leo in indexOfLeos
        lines = split(file_contents, "\n")
        result = ""
        for line in lines
            words = split(line)
            if length(words) >= 5 && words[5] == string(leo)
                result *= line
                result *= "\n"
            end
        end

        lines = split(result, "\n")
        for line in lines
            words = split(line)
            if !isempty(words) && parse(Int, words[6]) in indexOfHags
                for t in div(parse(Int,words[3][2:end]),100):(div(parse(Int, words[4][2:end]), 100)-1)
                    append!(contactList[div(parse(Int, words[6])-1,2)], t)
                end
            end
        end
    end
    return contactList
end

function generate_states(n, p, current_state=[], current_router=1, states=[])
    if current_router > n || p < 0
        if p == 0 
            push!(states, copy(current_state))
        end
        return
    end

    if isempty(current_state)
        current_state = zeros(Int, n)
    end

    for packets in 0:p
        current_state[current_router] = packets
        generate_states(n, p - packets, current_state, current_router + 1, states)
    end

    if current_router <= n
        current_state[current_router] = 0
    end

    if current_router == 1
        return states
    end
end





function state()
    states = []
    TimedSteps = []
    maxBundles = 50
    for bundles in 0:maxBundles
        append!(states, generate_states(3, bundles))
    end

    for time in 0:maxOfTime
        for state in states
            ns = append!(copy(state), [time,0])
            TimedSteps = append!(TimedSteps, [ns])
        end
    end

    # print(length(TimedSteps), "\n")
    # for state in TimedSteps
    #     print(state, "\n")
    # end
    # print(TimedSteps, "\n")
    return TimedSteps
end


function transition(s, a)
    transitionMatrix = [[0.2, 0.8], [0.6, 0.4]]
    contactPlan = contactPlanGatherer()
    # println("Transition from state $s with action $a")
    ns = copy(s)

    if (s[1] >= 1 && a == "toHAGS1" && (s[4] in contactPlan[1]))
        # println("Transition from state $s with action $a to HAGS 1")
        ns[1] -= 1
        ns[2] += 1
    end

    if (s[1] >= 1 && a == "toHAGS2" && (s[4] in contactPlan[2]))
        # println("Transition from state $s with action $a to HAGS 2")
        ns[1] -= 1
        ns[3] += 1
    end

    # If there is still bundles in the HAGS
    if (s[1] >= 1)
        sameState = copy(ns)
        sameState[4] += 1
        sameStateProb = transitionMatrix[1][1] * transitionMatrix[2][1] # fail / fail

        firstSucceeded = copy(ns)
        if firstSucceeded[2] >= 1
            firstSucceeded[2] -= 1
            firstSucceeded[5] += 1 # Final destination
            firstSucceeded[4] += 1 # Time
            firstSuceededProb = transitionMatrix[1][2] * transitionMatrix[2][1] # success / fail
        else # there are no bundles in HAGS 1
            firstSuceededProb = 0
            sameStateProb += transitionMatrix[1][2] * transitionMatrix[2][1] 
        end

        secondSucceeded = copy(ns)
        if secondSucceeded[3] >= 1
            secondSucceeded[3] -= 1
            secondSucceeded[5] += 1 # Final destination
            secondSucceeded[4] += 1 # Time
            secondSucceededProb = transitionMatrix[1][1] * transitionMatrix[2][2] # fail / success
        else # there are no bundles in HAGS 2
            secondSucceededProb = 0
            sameStateProb += transitionMatrix[1][1] * transitionMatrix[2][2]
        end
        
        bothSucceeded = copy(ns)
        if (bothSucceeded[2] >= 1 && bothSucceeded[3] >= 1)
            bothSucceeded[2] -= 1
            bothSucceeded[3] -= 1
            bothSucceeded[5] += 2 # Final destination
            bothSucceeded[4] += 1 # Time
            bothSucceededProb = transitionMatrix[1][2] * transitionMatrix[2][2] # success / success
        else # there are no bundles in HAGS 1 or HAGS 2
            bothSucceededProb = 0
            sameStateProb += transitionMatrix[1][2] * transitionMatrix[2][2]
        end

        return SparseCat((sameState, firstSucceeded, secondSucceeded, bothSucceeded), 
                (sameStateProb, firstSuceededProb, secondSucceededProb, bothSucceededProb))
    else # Fast forward if there is not bundles in the LEO but bundle left in HAGS 1 or 2
        savedTime = s[4]

        totalTimeToRouteHAGS1 = (div(s[2], transitionMatrix[1][2]) === NaN ? 0 : div(s[2], transitionMatrix[1][2]))
        totalTimeToRouteHAGS2 = (div(s[3], transitionMatrix[2][2]) === NaN ? 0 : div(s[3], transitionMatrix[2][2]))
        maxTime = (max(totalTimeToRouteHAGS1, totalTimeToRouteHAGS2) == 0 ? 1 : max(totalTimeToRouteHAGS1, totalTimeToRouteHAGS2))
        ns[4] += maxTime
        # If we go over the time limit
        if ns[4] > maxOfTime
            ns[4] = maxOfTime
            bundlesLeftHAGS1 = floor(transitionMatrix[1][2] * (maxOfTime - savedTime))
            bundlesLeftHAGS2 = floor(transitionMatrix[2][2] * (maxOfTime - sameTime))
            ns[5] += (ns[2] + ns[3] - bundlesLeftHAGS1 - bundlesLeftHAGS2)
            ns[2] = bundlesLeftHAGS1
            ns[3] = bundlesLeftHAGS2
        else # The true state at the end of the time
            ns[5] += (ns[2] + ns[3])
            ns[2] = 0
            ns[3] = 0
        end
        
        return SparseCat((ns,), (1.0,))
    end

end

function reward(s, a, sp)
    # println("Reward from state $s with action $a and next state $sp")
    # print(s, a, sp, "\n")
    totalReward = 0
    if sum(sp[1:3]) == 0
        totalReward += maxOfTime*10 - (10 * sp[4])
    else
        totalReward += 10 * (sp[5] - s[5])

        totalReward += 5 * (sp[4] - s[4])
    end
    if (sp[4] == maxOfTime && sum(s[1:3]) >= 1)
        totalReward += -50
    end
    return totalReward
end

function is_terminal(s)
    # println("Checking if state $s is terminal : ", all(s[1:3] .== 0) || s[4] == 20)
    return all(s[1:3] .== 0) || s[4] == maxOfTime
end


mcts_mdp = QuickMDP(
    states = state,
    actions = ["keep","toHAGS1","toHAGS2"],
    isterminal = is_terminal,
    transition = transition,
    reward = reward,
    statetype = Vector{Int64}
)

mcts_solver = MCTSSolver(n_iterations=50,
                         depth=100,
                         exploration_constant=500.0,
                         enable_tree_vis=true,
                        # init_Q=special_Q,
                         )

                        
mcts_planner = solve(mcts_solver, mcts_mdp)

args = Base.parse.(Int, ARGS)
if length(args) < 4
    println("Usage: julia MDPs_Working.jl <n> <p>")
    return
end

l1 = args[1]
h1 = args[2]
h2 = args[3]
t = args[4]

initial_state = [l1, h1, h2, t, 0]
a, info = action_info(mcts_planner, initial_state)
tree = D3Tree(info[:tree], initial_state, init_expand=1)
# display(tree)
treeAct = mcts_planner.tree
for sn in MCTS.state_nodes(treeAct)  
    for san in MCTS.children(sn)
        println(MCTS.state(sn), " ", MCTS.action(san), " ", MCTS.q(san))
    end
end

# inchrome(tree)


# --------------------------- 2000 simulations statistics ---------------------------
# results = []
# for _ in 1:2000
#     a, info = action_info(mcts_planner, [1,0,0,0,0,0])
#     push!(results, a)
# end


# counts = Dict()
# for a in results
#     counts[a] = get(counts, a, 0) + 1
# end

# println("Action statistics:")
# for (a, count) in counts
#     println("Action $a: $count times")
# end


# --------------------------- Next actions from initial state ---------------------------
# treeAct = mcts_planner.tree


# for sn in MCTS.state_nodes(treeAct)
#     local counter = 0   
#     for san in MCTS.children(sn)
#         println("State: ", MCTS.state(sn), " Action: ", MCTS.action(san), " Q value: ", MCTS.q(san))
#         counter += 1
#         if counter == 3
#             break
#         end
#     end
#     if counter == 3
#         break
#     end
# end
# print(a, "\n")

# ------------------------------------- All actions -------------------------------------
# tree = mcts_planner.tree
# for sn in MCTS.state_nodes(tree)
#     for san in MCTS.children(sn)
#         println("State: ", MCTS.state(sn), " Action: ", MCTS.action(san), " Q value: ", MCTS.q(san), " N: ", MCTS.n(san))
#     end
# end
