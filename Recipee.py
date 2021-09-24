# -*- coding: utf-8 -*-
"""
MENU PLANNING MATHEMATICAL MODEL

This code contains a class to represent a dish recipee, in order to compute its
nutrients

Created on Mon Apr 15 13:55:41 2019
"""

__author__ = 'Caleb Andrade'

import os
import glob
import csv 

#******************************************************************************
# HELPER FUNCTIONS
#******************************************************************************

NUTRIENTS = ['agua',
             'energia', 
             'proteina', 
             'grasa_total', 
             'carbohidratos', 
             'fibra_dietetica',
             'ceniza',
             'calcio', 
             'fosforo', 
             'hierro', 
             'tiamina', 
             'riboflavina', 
             'niacina',
             'vitamina_c', 
             'vitamina_a_rae', 
             'ac_graso_mono', 
             'ac_graso_poli',
             'ac_graso_sat', 
             'colesterol', 
             'potasio', 
             'sodio', 
             'zinc',
             'magnesio', 
             'vitamina_b6', 
             'vitamina_b12', 
             'acido_folico', 
             'folato'
            ]
             

def readRecipee(filename):
    """
    Reads a recipee from a csv file.
    """
    
    name = filename[:-4] # Extracting recipee's name
    ingredients = []
       
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ",")
        line_count = 0
        
        for row in csv_reader:
            if line_count == 0:
                servings = int(row[1])
                line_count += 1
            elif line_count == 1:
                grams = float(row[1])
                line_count += 1
            elif line_count == 2:
                classification = [int(x) for x in row[1:-1]]
                line_count += 1
            elif line_count == 3:
                line_count += 1
            else:
                ingredients.append(row)
                            
    return name, servings, grams, classification, ingredients


def convert(string):
    """
    Converts a string into a float.
    """
    if string == '':
        return 0
    return float(string)


def foodTable(filename):
    """
    Reads food composition table and builds a dictionary.
    Keys are food ingredients, values are nutrients vectors.
    Nutrients correspond to servings of 100g.
    """
    
    nutrients = {}
    
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ",")
        line_count = 0
        
        for row in csv_reader:
            if line_count < 2:
                line_count += 1
            else:
                nutrients[row[1]]=[convert(x) for x in row[2:]]
                
    return nutrients


def costTable(filename):
    """
    Reads food costs from a table and builds a dictionary.
    Keys are food ingredients, values is a vector [food costs, grams]
    """
    
    costs = {}
    
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ",")
        
        for row in csv_reader:
            costs[row[0]] = [float(row[1]), float(row[2])]
                
    return costs


def nutrientCalculator(recipees):
    """
    Computes the overall nutrients values for a set of recipees.
    """
    
    nutrients_sum = {}
    
    for i in range (len(NUTRIENTS)):
        nutrients_sum[NUTRIENTS[i]] = 0
        
    for nutrient in NUTRIENTS:
        for recipee in recipees:
            nutrients_sum[nutrient] += recipee.nutrients[nutrient]
            
    return nutrients_sum    
 
        
#******************************************************************************
# RECIPEE CLASS
#******************************************************************************

class Recipee:
    """
    Class to contain a dish recipee.
    """
    
    def __init__(self, filename, food_table, cost_table):
        """
        Initialize a recipee.
        Input: csv file with a recipee, nutrients food table, food cost table.
        """
        
        temp_recipee = readRecipee(filename)
        
        self.name = temp_recipee[0]
        self.servings = temp_recipee[1]
        self.grams = temp_recipee[2]
        self.classification = temp_recipee[3]
        self.ingredients = {}
        
        for ingredient in temp_recipee[4]:
            self.ingredients[ingredient[3]] = float(ingredient[2])
        
        self.number_ingredients = len(self.ingredients)
        
        # Initializing nutrients values
        self.nutrients = {}
        for i in range (len(NUTRIENTS)):
            self.nutrients[NUTRIENTS[i]] = 0
            
        # Computing nutrients values
        self.recipeeNutrients(food_table)
        
        # Computing cost of recipee
        self.cost = self.recipeeCost(cost_table)
        
   
    def __str__(self):
        """
        As string.
        """
        
        recipee = "\n" + self.name + "\n" + "servings: " + str(self.servings) + "\n"
        
        for key in self.ingredients.keys():
            recipee += "\n" + str(self.ingredients[key]) + "g" + " ... " + key
            
        recipee += "\n\n" + "grams: " + str(self.grams) + "\n" + "classification: " + str(self.classification) + "\n"
            
        return recipee
    
    
    def recipeeNutrients(self, food_table):
        """
        Computes nutrients of recipee.
        """
  
        for i in range(len(NUTRIENTS)):
            for ingredient in self.ingredients.keys():
                # Compute nutrient value for each ingredient in recipee, add it up.
                if ingredient in food_table:
                    value = food_table[ingredient][i]*self.ingredients[ingredient]/100
                    self.nutrients[NUTRIENTS[i]] += value/self.servings
                else:
                    print "No food ", ingredient, " was found"
    
    
    def recipeeCost(self, cost_table):
        """
        Computes cost of recipee.
        """
    
        cost = 0
    
        for ingredient in self.ingredients:
            if ingredient in cost_table:
                food_cost = cost_table[ingredient][0]
                grams = cost_table[ingredient][1]
                cost += food_cost*self.ingredients[ingredient]/grams
            else:
                 print "No cost of ", ingredient, " was found"
            
        return round(cost/self.servings, 2)
    
    
    def getNutrients(self):
        """
        Returns nutrients.
        """        
        return dict(self.nutrients)
    
    
    def getIngredients(self):
        """
        Returns ingredients.
        """        
        return dict(self.ingredients)
    
    
    def getCost(self):
        """
        Returns cost.
        """
        return self.cost

#******************************************************************************
# TESTING
#******************************************************************************

def recipeeBuilder():
    """
    Builds a list of recipees.
    """
   
    os.chdir("C:\Users\caleb\Documents\DOCTORADO UNAM\FUNSALUD\PLANEACION DE MENU")
    food_table = foodTable('tabla_composicion_alimentos.csv')
    cost_table = costTable('tabla_costos_alimentos.csv')
    
    
    os.chdir("C:\Users\caleb\Documents\DOCTORADO UNAM\FUNSALUD\PLANEACION DE MENU\RECETARIO")

    extension = 'csv'
    all_filenames = [x for x in glob.glob('*.{}'.format(extension))]
    
    recipees = []
    
    for filename in all_filenames:
        recipees.append(Recipee(filename, food_table, cost_table))
        
    return recipees, food_table, cost_table


def main():
    """
    Testing.
    """
    
    recipees, food_table, cost_table = recipeeBuilder()
    
#    for recipee in recipees:
#        print recipee
#        print "Cost per serving: $", recipee.getCost()
 

#        for nutrient in NUTRIENTS:
#            print nutrient, ": ", recipee.nutrients[nutrient]
            
#    print "\nNUTRIENT CALCULATOR"
            
#    nutrients_sum = nutrientCalculator([recipees[0], recipees[1]])
#    print recipees[0].name
#    print recipees[1].name
#    print
    
    
#    for nutrient in NUTRIENTS:
#            print nutrient, ": ", nutrients_sum[nutrient]
        
    
main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
            