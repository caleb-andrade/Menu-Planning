# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:11:01 2019

@author: caleb
"""

from gurobipy import *
from Recipee import *

# Nutrition guidelines, based on
# http://www.nutripac.com.mx/software/rec-mex.pdf
# Hombres: 25-65

def recipeeBook(recipees):
    """
    Classifies recipees into three categories: breakfast, lunch, dinner;
    and each category into four subcategories (entree, main dish, etc).
    Builds a dictionary with recipee's cost.
    Builds a dictionary with recipee's nutritional information.
    """
    
    category = {'b1':[], 'b2':[], 'b3':[], 'b4':[], 'b5':[],
                  'l1':[], 'l2':[], 'l3':[], 'l4':[], 'l5':[],
                  'd1':[], 'd2':[], 'd3':[], 'd4':[]}
    cost = {}
    nutrition_values = {}
    
    for recipee in recipees:
        index = recipee.classification
        x = ['b', 'l', 'd']
        for i in range(3):
            if index[i] != 0:
                key = x[i] + str(index[i])
                name = recipee.name + '_' + key
                # Build a dictionary with recipee categories
                category[key].append(name)
                # Build a dictionary with recipee cost
                cost[name] = recipee.cost                
                # Build a dictionary with nutrition values
                for nutrient in NUTRIENTS:
                    nutrition_values[(name, nutrient)] = recipee.nutrients[nutrient]
                
    return category, cost, nutrition_values


def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nCost: %g' % m.objVal)
        print('\nBuy:')
        buyx = m.getAttr('x', buy)
        for f in foods:
            if buy[f].x > 0.0001:
                print('%s %g' % (f, buyx[f]))
    else:
        print('No solution')
    

categories, minNutrition, maxNutrition = multidict({
             'agua': [0, GRB.INFINITY],
             'energia': [1800, 2700], 
             'proteina': [46, 56], 
             'grasa_total': [28, 43], 
             'carbohidratos': [0, GRB.INFINITY], 
             'fibra_dietetica': [18, 24],
             'ceniza': [0, GRB.INFINITY],
             'calcio': [800, GRB.INFINITY], 
             'fosforo': [800, GRB.INFINITY], 
             'hierro': [15, GRB.INFINITY], 
             'tiamina': [1.5, GRB.INFINITY], 
             'riboflavina': [1.7, GRB.INFINITY], 
             'niacina': [20, GRB.INFINITY],
             'vitamina_c': [60, GRB.INFINITY], 
             'vitamina_a_rae': [1000, GRB.INFINITY], 
             'ac_graso_mono': [0, GRB.INFINITY], 
             'ac_graso_poli': [0, GRB.INFINITY],
             'ac_graso_sat':[0, GRB.INFINITY], 
             'colesterol': [0, 300], 
             'potasio': [2000, GRB.INFINITY], 
             'sodio': [0, 2500], 
             'zinc': [15, GRB.INFINITY],
             'magnesio': [350, GRB.INFINITY], 
             'vitamina_b6': [2, GRB.INFINITY], 
             'vitamina_b12': [2, GRB.INFINITY], 
             'acido_folico': [200, GRB.INFINITY], 
             'folato': [0, GRB.INFINITY]})


# Read recipees
recipees, food_table, cost_table = recipeeBuilder()
recipee_category, recipee_cost, nutrition_values = recipeeBook(recipees)
foods, cost = multidict(recipee_cost)

# Create a new model
m = Model("mip1")

# Create decision variables for the foods to buy
b1 = recipee_category['b1']
b2 = recipee_category['b2']
b3 = recipee_category['b3']
b4 = recipee_category['b4']
b5 = recipee_category['b5']
l1 = recipee_category['l1']
l2 = recipee_category['l2']
l3 = recipee_category['l3']
l4 = recipee_category['l4']
l5 = recipee_category['l5']
d1 = recipee_category['d1']
d2 = recipee_category['d2']
d3 = recipee_category['d3']
d4 = recipee_category['d4']

buy = m.addVars(foods, vtype = GRB.BINARY, name="buy")

# Set objective
m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

# Nutrition constraints
m.addConstrs(
    (quicksum(nutrition_values[f,c] * buy[f] for f in foods)
    	== [minNutrition[c], maxNutrition[c]]
     for c in categories), "_")

# Quantity constraints
m.addConstr(sum(buy[f] for f in b1) <= 1)
m.addConstr(sum(buy[f] for f in b2) <= 1)
m.addConstr(sum(buy[f] for f in b3) <= 1)
m.addConstr(sum(buy[f] for f in b4) <= 1)
m.addConstr(sum(buy[f] for f in b5) <= 1)
m.addConstr(sum(buy[f] for f in l1) <= 1)
m.addConstr(sum(buy[f] for f in l2) <= 1)
m.addConstr(sum(buy[f] for f in l3) <= 1)
m.addConstr(sum(buy[f] for f in l4) <= 1)
m.addConstr(sum(buy[f] for f in l5) <= 1)
m.addConstr(sum(buy[f] for f in d1) <= 1)
m.addConstr(sum(buy[f] for f in d2) <= 1)
m.addConstr(sum(buy[f] for f in d3) <= 1)
m.addConstr(sum(buy[f] for f in d4) <= 1)


# Write model
m.write("menu_planning_mip2.lp")

# Solve
m.optimize()

# Print solution
printSolution()

#"""

# Irreducible Infeasible Sets (IIS)
m.computeIIS()
print('\nThe following constraint(s) cannot be satisfied:')
for c in m.getConstrs():
    if c.IISConstr:
        print('%s' % c.constrName)


"""     
# Loop until reduce to a model that can be solved
removed = []

while True:
    
    m.computeIIS()
    print('\nTHE FOLLOWING CONSTRAINT CANNOT BE SATISFIED:')
    for c in m.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)
            # Remove a single constraint from the model
            removed.append(str(c.constrName))
            m.remove(c)
            break
    print('')
        
    m.optimize()
    status = m.status
        
    if status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        exit(0)
    if status == GRB.Status.OPTIMAL:
        break
    if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
        exit(0)
        print('\nThe following constraints were removed to get a feasible model:')
        print(removed)

printSolution()

"""

# Relax the constraints to make the model feasible
print('The model is infeasible; relaxing the constraints')
orignumvars = m.NumVars
m.feasRelaxS(0, False, False, True)
m.optimize()
status = m.status
if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
    print('The relaxed model cannot be solved \
           because it is infeasible or unbounded')
    exit(1)
    
if status != GRB.Status.OPTIMAL:
    print('Optimization was stopped with status %d' % status)
    exit(1)

print('\nSlack values:')
slacks = m.getVars()[orignumvars:]
for sv in slacks:
    if sv.X > 1e-6:
        print('%s = %g' % (sv.VarName, sv.X))

printSolution()
       