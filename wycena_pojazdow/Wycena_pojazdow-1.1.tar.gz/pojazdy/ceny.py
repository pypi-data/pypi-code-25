class Prices:
    pricesFord = [6000, 15000, 33000, 2500, 9000, 30000, 85000, 2000, 3500, 8000, 30000, 120000, 16000, 18000, 85000]
    pricesVolkswagen = [7000, 19000, 50000, 120000, 3000, 7000, 15000, 29000, 50000, 4000, 10000, 25000, 55000, 40000,
                        35000]
    pricesCitroen = [20000, 9000, 25000, 25000, 40000, 40000, 20000, 25000, 14000]
    pricesSkoda = [10000, 25000, 60000, 9000, 17000, 41000, 15000, 50000, 120000, 35000, 37000]
    pricesOpel = [3000, 7000, 14000, 28000, 52000, 2500, 6000, 15000, 45000, 40000, 115000, 9500, 15000, 40000]

    def getVehiclePriceByID(self, id_company, id_model):
        if id_company == 0:
            return self.pricesFord[id_model]
        elif id_company == 1:
            return self.pricesVolkswagen[id_model]
        elif id_company == 2:
            return self.pricesCitroen[id_model]
        elif id_company == 3:
            return self.pricesSkoda[id_model]
        else:
            return self.pricesOpel[id_model]