class overloadingTemplate:
    def __init__(self):
        pass
    
    def __repr__(self):
        #official string output
        pass
    
    def __str__(self):
        #loose string output, used by print
        pass
    
    
    ##comparator blocks##
    def __lt__(self, other):
        #less than 
        pass
    
    def __le__(self, other):
        #less than or equal
        pass
    
    def __eq__(self, other):
        #equal
        pass
    
    def __ne__(self, other):
        #not equal
        pass
    
    def __gt__(self, other):
        #greater than
        pass
    
    def __ge__(self, other):
        #greater than or equal
        pass
    
    def __nonzero__(self):
        #boolean testing
        pass