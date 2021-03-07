from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@api_view(['POST'])
def validate_finite_values_entity(request):
    received_json_data=json.loads(request.body)
    validate,filled,values,invalid_trigger,partially_filled,params = False,False,[],"",True,{} 
    allvalues = received_json_data['values']
    supported_values = received_json_data['supported_values']
    pick_first = received_json_data['pick_first']
    support_multiple = received_json_data['support_multiple']
    if len(allvalues) == 0:
        partially_filled = False

    if len(allvalues) >0:
        for each in allvalues:
            values.append(each['value'])   
            
    if len(values)>0 :
        for each in values:
            validate = True
            if each not in supported_values:
                validate = False
                break
        for each in values:
            if each not in supported_values:
                filled = False
                break
    if validate == False:
        invalid_trigger = "invalid_ids_stated"

    if validate  and support_multiple:
        filled = True
        partially_filled = False
   
    if invalid_trigger == "": 
        params = {'ids_stated':[]}
        for each in allvalues:
            params['ids_stated'].append(each['value'])
            if each['value'] not in supported_values:
                filled = False
    if pick_first == True:
        params['ids_stated'] = str(params['ids_stated'][0])

    SlotValidationResult = dict_arrangement(filled,partially_filled,invalid_trigger,params)
   
    return Response(SlotValidationResult)

@api_view(['POST'])
def validate_numeric_entity(request):
    received_json_data=json.loads(request.body)
    validate,filled,partially_filled,values,params,invalid_trigger = False,False,True,[],{},""
    allvalues = received_json_data['values']
    constraint = received_json_data['constraint']
    var_name = received_json_data['var_name']
    
    if len(allvalues) == 0:
        partially_filled = False

    if len(allvalues) >0:
        validate = True
        for each in allvalues:
            values.append(each['value'])   
    
    validate,values = validate_for_constraint(constraint,values,validate)
        
    if validate == False:
        invalid_trigger = "invalid_age_stated"
        if len(values)>0:
            params = {'age_stated':''}
            params['age_stated'] = values[0]
    
    if validate  :
        filled = True
        partially_filled = False
    
    if invalid_trigger == "": 
        params = {'age_stated':''}
        params['age_stated'] = max(values)

    if 'support_multiple' in received_json_data:
        support_multiple = received_json_data['support_multiple']        
        if support_multiple == True:
            params['age_stated'] = values

    SlotValidationResult = dict_arrangement(filled,partially_filled,invalid_trigger,params)

    return Response(SlotValidationResult) 

def validate_for_constraint(constraint,values,validate):
    if 'and' in constraint:
        condition = constraint.split('and')
        for each in condition:
            conditions = ' '.join(each.split())
            if '<=' in conditions:
                for each in values:
                    if each>= int(conditions.split('<=')[1]) or  len(values)>0 and each<0 :

                        values.remove(each)
                        validate =False
                        break
            if '>=' in conditions:
                for each in values:
                    if each<= int(conditions.split('>=')[1]):
                        values.remove(each)
                        validate =False
                        break
    return validate,values

def dict_arrangement(filled,partially_filled,invalid_trigger,params):
    SlotValidationResult = {
        "filled": filled,
        "partially_filled": partially_filled,
        "trigger": invalid_trigger,
        "parameters": params
    }
    return SlotValidationResult