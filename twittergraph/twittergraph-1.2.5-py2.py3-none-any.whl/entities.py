class Follower(object):

    def __init__(self, idMe, nameMe, idFollower, nameFollower):
        """__init__(idMe, nameMe, idFollower, nameFollower) 
           
        Crea un follower a partir de los datos de dos usuarios
        se ve de la forma b -> c
        que se lee b sigue a c
        donde b y c son usuarios
        

        @keyword idMe: el id del usuario que hace referencia al usuario c.
        @keyword nameMe: el nombre del usuario que hace referencia al usuario c.
        @keyword idFollower: el id del usuario que hace referencia al usuario b.
        @keyword nameFollower: el nombre del usuario que hace referencia al usuario b.
         """ 
        self.md = {}
        self.idMe = self.md["idMe"] = idMe
        self.nameMe = self.md["nameMe"] = nameMe
        self.idFollower = self.md["idFollower"] = idFollower
        self.nameFollower = self.md["nameFollower"] = nameFollower

    def __str__(self):
        return self.idFollower+","+self.nameFollower+","+self.idMe+","+self.nameMe

    def __getitem__(self,key):
        return self.md[key]

    def __setitem__(self, key, item):
        self.md[key] = item

    def dicti(self):
        """dicti()
        
        returna un diccionario con los elementos que posee un follower

        @return: el solo diccionario
        """
        return self.md


class Following(object):

    def __init__(self, idMe, nameMe, idFollowing, nameFollowing):
        """__init__(idMe, nameMe, idFollower, nameFollower) 
           
        Crea un following a partir de los datos de dos usuarios
        se ve de la forma b -> c
        que se lee b sigue a c
        donde b y c son usuarios
        

        @keyword idMe: el id del usuario que hace referencia al usuario b.
        @keyword nameMe: el nombre del usuario que hace referencia al usuario b.
        @keyword idFollowing: el id del usuario que hace referencia al usuario c.
        @keyword nameFollowing: el nombre del usuario que hace referencia al usuario c.
         """ 
        self.md = {}
        self.idMe = self.md["idMe"] = idMe
        self.nameMe = self.md["nameMe"] = nameMe
        self.idFollowing = self.md["idFollowing"] = idFollowing
        self.nameFollowing = self.md["nameFollowing"] = nameFollowing

    def __str__(self):
        return self.idMe+","+self.nameMe+","+self.idFollowing+","+self.nameFollowing

    def __getitem__(self,key):
        return self.md[key]

    def __setitem__(self, key, item):
        self.md[key] = item

    def dicti(self):
        """dicti()
        
        returna un diccionario con los elementos que posee un following

        @return: el solo diccionario
        """
        return self.md
