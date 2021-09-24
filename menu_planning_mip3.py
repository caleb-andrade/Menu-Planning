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

# Recommended nutrient intake
NUTRIENT_INTAKE = {
             'agua': 3200.0,
             'energia': 2250.0, 
             'proteina': 53.0, 
             'grasa_total': 60.0, 
             'carbohidratos': 300.0, 
             'fibra_dietetica': 31.0,
             'calcio': 800.0, 
             'fosforo': 800.0, 
             'hierro': 15.0, 
             'tiamina': 1.5, 
             'riboflavina': 1.7, 
             'niacina': 20.0,
             'vitamina_c': 60.0, 
             'vitamina_a_rae': 1000.0, 
             'ac_graso_mono': 20, 
             'ac_graso_poli': 10,
             'ac_graso_sat':10, 
             'colesterol': 300.0, 
             'potasio': 2000.0,
             'sodio': 2000.0, 
             'zinc': 15.0,
             'magnesio': 350.0, 
             'vitamina_b6': 2.0, 
             'vitamina_b12': 2.0, 
             'acido_folico': 200.0, 
             'folato': 400}


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
                            
                for nutrient in NUTRIENTS:
                    # Build a dictionary with nutrition values
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
#m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

m.setObjective(sum(NUTRIENT_INTAKE[n] - sum(nutrition_values[f,n] * buy[f] for f in foods) for n in NUTRIENT_INTAKE), GRB.MINIMIZE)

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
m.write("menu_planning_mip3.lp")

# Solve
m.optimize()

"""for v in m.getVars():
    print('%s %g' % (v.varName, v.x))

print('Obj: %g' % m.objVal)
"""
# Print solution
printSolution()
