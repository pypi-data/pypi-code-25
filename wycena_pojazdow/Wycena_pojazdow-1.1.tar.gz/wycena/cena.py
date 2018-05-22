from pojazdy.modele import Vehicles
from pojazdy.ceny import Prices
from pojazdy.roczniki import AverageYears
from wycena.wyposazenie import Equipment


class Calculation:
    vehicles = Vehicles()
    prices = Prices()
    average_years = AverageYears()
    equipment = Equipment()

    tab_vehicles = [vehicles.getTabVehicles(0), vehicles.getTabVehicles(1), vehicles.getTabVehicles(2),
                vehicles.getTabVehicles(3), vehicles.getTabVehicles(4)]

    def calculate(self, id_company, id_model, year, mileage, capacity, engine_type, tab_equipments=None):
        price = self.prices.getVehiclePriceByID(id_company, id_model)
        average_year = self.average_years.getVehicleAverageYearByID(id_company, id_model)

        if engine_type == "PB":
            price = price * 0.97
        else:
            price = price * 1.05

        difference = year - average_year

        if difference < 0:
            if difference < -4:
                price = price * 0.7
            elif difference < -2:
                price = price * 0.75
            else:
                price = price * 0.85

        else:
            if difference < 2:
                price = price * 0.95
            elif difference < 4:
                price = price * 1.15
            else:
                price = price * 1.35

        if mileage < 100000:
            price *= 1.1
        elif mileage > 400000:
            price *= 0.9

        if capacity < 1:
            price *= 0.9
        elif capacity < 1.4:
            price *= 0.98
        elif capacity < 1.7:
            price *= 1.05
        elif capacity < 1.9:
            price *= 1.1
        elif capacity < 2.2:
            price *= 1.25
        elif capacity < 2.5:
            price *= 1.35
        else:
            price *= 1.5

        if not tab_equipments is None:
            price *= self.equipment.getEquipmentValueByTabEquipments(tab_equipments)

        return price

# tablica= [8]
# calculation = Calculation()
# print(calculation.calculate(0,1,2005,156000,1.6,"PB",tablica))