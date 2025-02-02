from mip import Model, xsum, minimize, BINARY, CONTINUOUS, MINIMIZE, INTEGER
from time import time
import numpy as np
from data_tp_final import return_datas

'''
datas = return_datas()
    Objects    = datas['Objects']
        Stock   =Objects['Stock  ']
        Cost    =Objects['Cost   ']
        Length  =Objects['Length ']
        Height  =Objects['Height ']
        
    Items      = datas['Items']
        Demand   = Items['Demand   ']
        DemandMax= Items['DemandMax']
        Value    = Items['Value    ']
        Length   = Items['Length   ']
        Height   = Items['Height   ']
'''


from mip import Model, xsum, minimize, BINARY, CONTINUOUS, INTEGER
import numpy as np
from data_tp_final import return_datas

# Load data
datas = return_datas()
Objects = datas['Objects']
Items = datas['Items']

# Extract data
Stock = Objects['Stock']
Cost = Objects['Cost']
Length = Objects['Length']
Height = Objects['Height']

Demand = Items['Demand']
DemandMax = Items['DemandMax']
Value = Items['Value']
ItemLength = Items['Length']
ItemHeight = Items['Height']

# Preprocessing
def preprocess_bins_and_items(Stock, Length, Height, ItemLength, ItemHeight):
    # Shrink bins
    W_star = [max_combination(ItemLength, W) for W in Length]
    H_star = [max_combination(ItemHeight, H) for H in Height]
    
    # Enlarge items
    w_star = [W - max_combination(ItemLength, W - w) for w in ItemLength]
    h_star = [H - max_combination(ItemHeight, H - h) for h in ItemHeight]
    
    return W_star, H_star, w_star, h_star

def max_combination(items, limit):
    # Dynamic programming to find the maximum combination of items that fits within the limit
    dp = [0] * (limit + 1)
    for item in items:
        for j in range(limit, item - 1, -1):
            dp[j] = max(dp[j], dp[j - item] + item)
    return dp[limit]

# Apply preprocessing
W_star, H_star, w_star, h_star = preprocess_bins_and_items(Stock, Length, Height, ItemLength, ItemHeight)

# Model definition
model = Model()

# Define variables
u = [model.add_var(var_type=BINARY) for _ in range(len(Stock))]
v = [[model.add_var(var_type=BINARY) for _ in range(len(Stock))] for _ in range(len(Demand))]
x = [model.add_var(var_type=CONTINUOUS) for _ in range(len(Demand))]
y = [model.add_var(var_type=CONTINUOUS) for _ in range(len(Demand))]

# Objective function
model.objective = minimize(xsum(Cost[j] * u[j] for j in range(len(Stock))))

# Constraints
# Add constraints based on the problem definition

# Solve model
model.optimize()

# Output results
if model.num_solutions:
    print('Optimal solution found:')
    for j in range(len(Stock)):
        if u[j].x >= 0.99:
            print(f'Use bin {j} with cost {Cost[j]}')
else:
    print('No feasible solution found')