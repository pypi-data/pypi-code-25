class Equipment:

    rodzaje = ["ABS", "Alarm", "Alufelgi", "Czujniki parkowania", "ESP", "Klimatyzacja", "Nawigacja", "Napęd 4x4",
               "Reflektor LED", "Tempomat"]

    mnoznik=[1.01,1.001,1.04,1.03,1.01,1.015,1.07,1.06,1.1,1.01]

    def getEquipmentValueByID(self,id):
        return self.mnoznik[id]
    def getEquipmentValueByTabEquipments(self,tab):
        if len(tab) == 1:
            return self.getEquipmentValueByID(tab[0])
        else:
            temp=1
            for i in tab:
                temp *= self.mnoznik[i]
                if temp>1.2:
                    return temp
            return temp


    def getTabEquipments(self):
        return self.rodzaje