class Module:
    def __init__(self,id, tittle, description):
        self.id = id
        self.tittle = tittle
        self.description = description

    def __str__(self):
        return f"Course(title={self.title}, description={self.description})"
