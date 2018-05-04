from rpi_featureSelection.MergeArrays import mergeArrays
from rpi_featureSelection.calculateConditionalEntropy import ConditionalEntropy

def cmi(dataVector, targetVector, conditionVector, length = 0):
    cmi = 0
    firstCondition = 0
    secondCondition = 0
    
    if length == 0:
        length = dataVector.size
    
    results = mergeArrays(targetVector, conditionVector, length)
    mergedVector = results[1]
    
    firstCondition = ConditionalEntropy(dataVector, conditionVector, length)
    secondCondition = ConditionalEntropy(dataVector, mergedVector, length)
    
    cmi = firstCondition - secondCondition
    
    return cmi
    
     
