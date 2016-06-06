### TODO:

1. ~~Port to python2~~  (DONE)  
2. ~~Case sensitivity - Change the type of the namedtuple to exactly match Tommy's. E.g., LPAREN to Lparen~~  (DONE)  
3. Comment for all code (NEARLY DONE)
4. Change to code to ensure that either everything in the control is a tuple or everything is a Token (may not be possible)
5. ~~Change the code in the evaluator's step function to reflect the following:~~   (DONE)  
```
If C is a value:  
  If stack is empty:  
    return finished  
  else:  
    5 possible rules may apply depending on what the stack top contains  
  else:  
    return stuck  
else:  
  Control dictates which rule to follow (4 possible)  
  else:  
    return stuck
```
