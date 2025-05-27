using QuickPOMDPs, POMDPs, POMDPTools, QMDP, MCTS, BasicPOMCP, D3Trees, DiscreteValueIteration
using Parameters

global indexOfLeos = [6]
global indexOfHags = [3,5]
global maxOfTime = 100

struct CustomStateGenerator
    num_routers::Int
    max_packets::Int
    max_time::Int
end

function generate_states(n::Int, p::Int, current_state::Vector{Int}, current_router::Int, target_index::Int, current_index::Int=1)
    if current_router > n || p < 0
        return
    end

    if isempty(current_state)
        current_state = zeros(Int, n)
    end

    # For each possible number of packets in the current router
    for packets in 0:p
        current_state[current_router] = packets

        # Calculate how many states are left to skip
        remaining_states = binomial(n - current_router + p - packets - 1, p - packets)

        if current_index + remaining_states >= target_index
            # If target_index is within the range of the current configuration
            if current_router == n
                return current_state
            else
                return generate_states(n, p - packets, current_state, current_router + 1, target_index, current_index)
            end
        else
            # Skip the number of states in this configuration
            current_index += remaining_states
        end
    end
end


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

# Define the length of the state space, accounting for all routers and possible states
function Base.length(generator::CustomStateGenerator)
    # Calculate the total number of states based on your constraints
    n = generator.num_routers
    p = generator.max_packets
    t = generator.max_time
    
    # Number of states is determined by all combinations of (n, p, t)
    total_states = 0
    for bundles in 0:p
        total_states += binomial(n + bundles - 1, bundles)
    end
    
    return total_states * (t + 1)
end


# Indexing into a specific state
function Base.getindex(generator::CustomStateGenerator, si::Int)
    @assert si <= length(generator) "Index out of bounds"
    @assert si > 0 "Index out of bounds"

    # Translate si into an (n, p, t) state
    bundles_accumulated = 0
    n = generator.num_routers
    p = generator.max_packets
    t = generator.max_time
    
    # Identify which bundle and time this index corresponds to
    for bundles in 0:p
        state_count = binomial(n + bundles - 1, bundles)
        if si <= bundles_accumulated + state_count * (t + 1)
            bundle_index = si - bundles_accumulated - 1
            time_step = bundle_index % (t + 1)
            state_index = div(bundle_index, (t + 1)) + 1
            
            # Generate the specific state
            current_state = zeros(Int, n)
            generate_states(n, bundles, current_state, 1, state_index)
            
            return append!(copy(current_state), [time_step, 0])
        end
        bundles_accumulated += state_count * (t + 1)
    end
end

# First and last index
Base.firstindex(generator::CustomStateGenerator) = 1
Base.lastindex(generator::CustomStateGenerator) = length(generator)


# Create the iterator for the custom state generator
function Base.iterate(generator::CustomStateGenerator, ii::Int=1)
    if ii > length(generator)
        return nothing
    end
    state = getindex(generator, ii)
    return (state, ii + 1)
end



function transition(s, a)
    transitionMatrix = [
        [1-clear_sky_prob[1], clear_sky_prob[1]], # HAGS 1 : fail, success
        [1-clear_sky_prob[2], clear_sky_prob[2]] # HAGS 2 : fail, success
    ]
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
            bundlesLeftHAGS2 = floor(transitionMatrix[2][2] * (maxOfTime - savedTime))
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
        totalReward += 2 * (sp[5] - s[5])
        totalReward += 5 * (s[1] - sp[1])
        totalReward += 2 * (s[4] - sp[4])
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

# Define the MDP using the generator
generator = CustomStateGenerator(3, 50, maxOfTime)


mcts_mdp = QuickMDP(
    states = generator,
    actions = ["keep","toHAGS1","toHAGS2"],
    isterminal = is_terminal,
    transition = transition,
    reward = reward,
    statetype = Vector{Int64}
)

mcts_solver = MCTSSolver(n_iterations=5000,
                         depth=500,
                         exploration_constant=500.0,
                         enable_tree_vis=true,
                        # init_Q=special_Q,
                         )

                        
mcts_planner = solve(mcts_solver, mcts_mdp)

if length(ARGS) < 6
    println("Error: Expected at least 6 arguments")
    return
end

# # Parse the first four arguments as integers
# l1 = parse(Int, ARGS[1])
# h1 = parse(Int, ARGS[2])
# h2 = parse(Int, ARGS[3])
# t = parse(Int, ARGS[4])

# # The next two arguments are strings, so you don't need to parse them
# TTF = split(ARGS[5], "_")
# TTR = split(ARGS[6], "_")

l1 = 49 
h1 = 0 
h2 = 1 
t = 0 
TTR = split("25_25", "_")
TTF = split("3_6", "_")

TTF = [parse(Int, x) for x in TTF]
TTR = [parse(Int, x) for x in TTR]
# println("TTF: ", TTF)
# println("TTR: ", TTR)

# Calculate the clear sky probability
global clear_sky_prob = zeros(Float64, length(TTF))
for i in 1:length(TTF)
    clear_sky_prob[i] = TTF[i] / (TTF[i] + TTR[i])
end

# println("Clear sky probabilities: ", clear_sky_prob)

initial_state = [l1, h1, h2, t, 0]
a, info = action_info(mcts_planner, initial_state)
tree = D3Tree(info[:tree], initial_state, init_expand=1)
# display(tree)
treeAct = mcts_planner.tree

# using JSON

# results = Dict()

# for sn in MCTS.state_nodes(treeAct)  
#     for san in MCTS.children(sn)
#         if MCTS.q(san) != 0
#             state = MCTS.state(sn)
#             action = MCTS.action(san)
#             q_value = MCTS.q(san)
#             results[state] = (action, q_value)
#         end
#     end
# end

# json_data = JSON.json(results)
# file_path = "/home/benoitcoeugnet/git/dtnsim/dtnsim/simulations/HAPS_Analysis/policy.json"
# open(file_path, "w") do file
#     write(file, json_data)
# end

inchrome(tree)


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
