class Challenge:
    def __init__(self, tittle, description, is_docker, version, id, has_file, completed):
        self.tittle = tittle.lower()
        self.description = description
        self.is_docker = int(is_docker)
        self.version = version
        self.id = id
        self.has_file = int(has_file)
        self.completed = int(completed)

    def __str__(self):
        return f"Challenge(tittle={self.tittle}, description={self.description}, is_docker={self.is_docker}), version={self.version}, id={self.id}, has_file={self.has_file}, completed={self.completed}"
