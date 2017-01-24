import csv
import json
from pprint import pprint
from pyomo.environ import *
from pyomo.opt import SolverFactory


'''
*********************************************************************************************************
*********************************************************************************************************
            *********importing json file and saving it in variable data as a dictionary**********
*********************************************************************************************************
*********************************************************************************************************
'''

with open('ProblemData2.json') as data_file:
    data = json.load(data_file)

#print(len(data[0]))
#print(data[0]['capacity'])

#solving the LP problem with imported data

IP_Objective_value = []
LP_Objective_value = []
for mod_IP_LP in range(2):
    for reza in range(len(data)):
        objective_terms = data[reza]['values']
        constraint_terms = [data[reza]['sizes']]
        RHS_vector = data[reza]['capacity']

        #initialize model
        opt = SolverFactory('cbc')

        ## por katrdan
        model = ConcreteModel()

        #create dummy branch variable (no part of our solution)
        model.branch = Var([0], domain=Integers, bounds=(0, 1))

        #define index sets (parts of pyomo)
        def i_rule(model):
            return [i for i in range(len(objective_terms))]
        model.I = Set(rule=i_rule)
        #here is set in pyomo

        def j_rule(model):
            return [j for j in range(len(constraint_terms))]
        model.J = Set(rule=j_rule)

        #define variables
        if mod_IP_LP==0:
            model.x = Var(model.I, bounds=(0, 1))
        else:
            model.x = Var(model.I, domain=Integers, bounds=(0, 1))

        #define terms
        def obj_terms_rule(model, i):
            return objective_terms[i]
        model.obj_terms = Param(model.I, rule=obj_terms_rule)

        def constr_terms_rule(model, j, i):
            return constraint_terms[j][i]
        model.constr_terms = Param(model.J, model.I, rule=constr_terms_rule)

        def RHS_terms_rule(model, j):
            return RHS_vector[j]
        model.RHS = Param(model.J, rule=RHS_terms_rule)


        #define objective
        def obj_rule(model):
            return summation(model.obj_terms, model.x) + model.branch[0]
        model.obj = Objective(rule=obj_rule, sense=maximize)


        #define constraints
        def constr_rule(model, j):
            t = [model.constr_terms[j, i] for i in model.I]
            return summation(t, model.x) <= model.RHS[j]
        model.constr = Constraint(model.J, rule=constr_rule)

        results = opt.solve(model)
        model.solutions.load_from(results)

        ##saving vector x in a csv file**********************************

        x_vals = [model.x[i].value for i in model.I]
        mohammad = 0
        for ashkan in range(len(data[reza]['values'])):
            mohammad += data[reza]['values'][ashkan]*x_vals[ashkan]
        if mod_IP_LP == 0:
            LP_Objective_value.append(mohammad)
        else:
            IP_Objective_value.append(mohammad)

print(LP_Objective_value)
print(IP_Objective_value)

#Putting integrality gaps in a list including the infinity integrality gaps
Integrality_gap = []
for gap in range(len(LP_Objective_value)):
    if IP_Objective_value[gap] == 0:
        Integrality_gap.append('inf')
    else:
        Integrality_gap.append((LP_Objective_value[gap]/IP_Objective_value[gap]))

print(Integrality_gap)

# creating a list without integrality gaps of infinity
if 'inf' in Integrality_gap:
        Integrality_gap_without_inf = [gapol for gapol in Integrality_gap if gapol != 'inf']

#printing Minimum integrality gap
print('Minimum Integrality Gap = ', min(Integrality_gap_without_inf))

#printing maximum of integrality gap
print('Maximum Integrality Gap = ', max(Integrality_gap_without_inf))

#calculating average integrality gap
sum_for_ave = 0
for gapoli in range(len(Integrality_gap_without_inf)):
    sum_for_ave += Integrality_gap_without_inf[gapoli]
average_integrality_gap = sum_for_ave / (len(Integrality_gap_without_inf))
print('Average Integrality Gap = ', average_integrality_gap)


#finding the index for minimum integrality gap
index_of_min_integrality_gap = 0
for gapolio in range(len(Integrality_gap)):
    if Integrality_gap[gapolio] == min(Integrality_gap_without_inf):
        index_of_min_integrality_gap = gapolio
print('Index for Minimum Integrality Gap = ', index_of_min_integrality_gap)


#reporting the integrality gaps for integers in a csv file
with open ('ProblemSoln2.csv', 'w', newline='') as fp:
    afinal = csv.writer(fp, delimiter = '\n')
    afinal.writerow(Integrality_gap)

# reporting minimum integrality gap in a json file
data_of_minimum_integralty_gap = data[index_of_min_integrality_gap]

with open('ProblemSoln2.json', 'w') as fp:
    json.dump(data_of_minimum_integralty_gap, fp)

'''
print([('o_'+str(i), model.obj_terms[i]) for i in model.I])
print([('c_'+str(j)+','+str(i), model.constr_terms[j, i]) for j in model.J for i in model.I])
print([('v_'+str(j), model.RHS[j]) for j in model.J])
print([('x_'+str(i), model.x[i].value) for i in model.I])
'''