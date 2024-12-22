class Course:
    def __init__(self,id, tittle, description, level):
        self.id = id
        self.tittle = tittle
        self.description = description
        self.level = level

    def __str__(self):
        return f"ID: {self.id} - Course(title={self.tittle}, description={self.description}, level={self.level})"
