class AverageYears:
    avYearFord = [2002, 2008, 2014, 1998, 2003, 2011, 2016, 1998, 2001, 2005, 2011, 2016, 2003, 2012, 2015]
    avYearVolkswagen = [1998, 2007, 2012, 2016, 1995, 2002, 2006, 2011, 2015, 1996, 2005, 2013, 2017, 2010, 2016]
    avYearCitroen = [2010, 2006, 2010, 2011, 2016, 2015, 2012, 2010, 2009]
    avYearSkoda = [2003, 2008, 2016, 2004, 2011, 2016, 2005, 2011, 2016, 2016, 2015]
    avYearOpel = [1996, 2004, 2009, 2014, 2017, 1996, 2003, 2010, 2016, 2013, 2017, 2002, 2008, 2014]

    def getVehicleAverageYearByID(self, id_company, id_model):
        if id_company == 0:
            return self.avYearFord[id_model]
        elif id_company == 1:
            return self.avYearVolkswagen[id_model]
        elif id_company == 2:
            return self.avYearCitroen[id_model]
        elif id_company == 3:
            return self.avYearSkoda[id_model]
        else:
            return self.avYearOpel[id_model]