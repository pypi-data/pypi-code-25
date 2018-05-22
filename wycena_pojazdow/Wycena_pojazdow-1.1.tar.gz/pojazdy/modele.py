class Vehicles:
    tabVehicles = ["Ford", "Volkswagen", "Citroen", "Skoda", "Opel"]

    tabFord = ["Focus MK1", "Focus MK2", "Focus MK3", "Mondeo MK2", "Mondeo MK3", "Mondeo MK4", "Mondeo MK5",
               "Fiesta MK4",
               "Fiesta MK5", "Fiesta MK6", "S-MAX MK1", "S-MAX MK2", "Transit MK5", "Transit MK6", "Transit MK7"]
    tabVolkswagen = ["Passat B5", "Passat B6", "Passat B7", "Passat B8", "Golf III", "Golf IV", "Golf V", "Golf VI",
                     "Golf VII",
                     "Polo III", "Polo IV", "Polo V", "Polo VI", "Scirroco", "Up!"]

    tabCitroen = ["C1", "C2", "C3", "C4", "C4 Cactus", "C-Elysee", "C4 Grand Picasso", "C5", "C6"]

    tabSkoda = ["Octavia", "Octavia 2", "Octavia 3", "Fabia", "Fabia 2", "Fabia 3", "Superb", "Superb 2", "Superb 3",
                "Citigo",
                "Rapid"]

    tabOpel = ["Astra F", "Astra G", "Astra H", "Astra J", "Astra K", "Corsa B", "Corsa C", "Corsa D", "Corsa E",
               "Insignia A",
               "Insignia B", "Zafira A", "Zafira B", "Zafira C"]

    def getVehicleByID(self, id_company, id_model):
        if id_company == 0:
            return self.tabFord[id_model]
        elif id_company == 1:
            return self.tabVolkswagen[id_model]
        elif id_company == 2:
            return self.tabCitroen[id_model]
        elif id_company == 3:
            return self.tabSkoda[id_model]
        else:
            return self.tabOpel[id_model]

    def getTabVehicles(self, id_company):
        if id_company == 0:
            return self.tabFord
        elif id_company == 1:
            return self.tabVolkswagen
        elif id_company == 2:
            return self.tabCitroen
        elif id_company == 3:
            return self.tabSkoda
        else:
            return self.tabOpel