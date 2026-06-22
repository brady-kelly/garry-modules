class Person:    
    def __init__(self, first, last) -> None:
        self.first_name = first
        self.last_name = last        
        
    def get_full_name(self):
        return self.first_name + " " + self.last_name
    
    def get_initials(self):
        return self.first_name[0] + "." + self.last_name[0] + "."