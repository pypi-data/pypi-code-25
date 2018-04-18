"""This files contains the Project class that deals with multiple models at
once.

Notes
-----
This module is created at Artesia Water by Raoul Collenteur.

Usage
-----

>>> mls = Project()

"""

import logging
import os

import numpy as np
import pandas as pd
import pastas as ps

logger = logging.getLogger(__name__)


class Project:
    """The Project class is a placeholder when multiple time series models
    are analyzed in a batch.

    """

    def __init__(self, name, metadata=None):
        """Initialize a Project instance.

        Parameters
        ----------
        name: str
            Name of the project
        metadata: dict
            Dictionary with any metadata information on the project.

        """
        self.models = {}
        self.name = name
        # Store the data in Pandas dataframes
        self.data = pd.DataFrame()

        # DataFrames to store the data of the oseries and stresses
        self.stresses = pd.DataFrame(columns=["name", "series", "kind", "x",
                                              "y", "z"])
        self.oseries = pd.DataFrame(columns=["name", "series", "kind", "x",
                                             "y", "z"])

        # Project metadata and file information
        self.metadata = self.get_metadata(metadata)
        self.file_info = self._get_file_info()

    def add_series(self, series, name=None, kind=None, metadata=None,
                   settings=None, **kwargs):
        """Method to add series to the oseries or stresses database.

        Parameters
        ----------
        series: pandas.Series / pastas.TimeSeries
            Series object.
        name: str
            String with the name of the series that will be maintained in
            the database.
        kind: str
            The kind of series that is added. When oseries are added it is
            necessary to state "oseries" here.
        metadata: dict
            Dictionary with any metadata that will be passed to the
            TimeSeries object that is created internally.
        settings: dict or str
            Dictionary with any settings that will be passed to the
            TimeSeries object that is created internally.

        Returns
        -------

        """
        if name is None:
            name = series.name

        if kind == "oseries":
            data = self.oseries
        else:
            data = self.stresses

        if name in data.index:
            logger.error("Time series with name %s is already present in the \
                         database. Please provide a different name." % name)

        try:
            ts = ps.TimeSeries(series=series, name=name, settings=settings,
                               metadata=metadata, **kwargs)
        except:
            logger.warning("Time series %s is ommitted from the database."
                           % name)
            return

        data.at[name, "name"] = name
        data.at[name, "series"] = ts  # Do not add as first!
        data.at[name, "kind"] = kind

        # Transfer x, y and z to dataframe as well to increase speed.
        for i in ts.metadata.keys():
            value = ts.metadata[i]
            data.at[name, i] = value

    def del_oseries(self, name):
        """Method that savely removes oseries from the project. It validates
        that the oseries is not used in any model.

        Parameters
        ----------
        name: str
            string with a single oseries name.

        """
        if name in self.oseries.index:
            logger.error("Time series with name %s is not present in the \
                         database. Please provide a different name." % name)
        else:
            self.oseries.drop(name, inplace=True)

    def del_stress(self, name):
        """Method that removes oseries from the project.

        Parameters
        ----------
        stress: list or str
            list with multiple or string with a single oseries name.

        Returns
        -------

        """
        self.stresses.drop(name, inplace=True)

    def add_model(self, oseries, model_name=None, **kwargs):
        """Method to add a Pastas Model instance based on one of the oseries.

        Parameters
        ----------
        oseries: str
            string with the exact names of one of the oseries indices.
        model_name: str
            Name of the model
        kwargs: dict
            any arguments that are taken by the Pastas Model instance can be
            provided.

        Returns
        -------
        ml: pastas.Model
            Pastas Model generated with the oseries and arguments provided.

        """
        if model_name is None:
            model_name = oseries

        # Validate name and ml_name before continuing
        if model_name in self.models.keys():
            logger.error("Model name is not unique, provide a new ml_name.")
        if oseries not in self.oseries.index:
            logger.error("Oseries name is not present in the database. "
                         "Make sure to provide a valid oseries name.")

        oseries = self.oseries.loc[oseries, "series"]
        ml = ps.Model(oseries, name=model_name, **kwargs)

        # Add new model to the models dictionary
        self.models[model_name] = ml

        return ml

    def del_model(self, ml_name):
        """Method to safe-delete a model from the project.

        Parameters
        ----------
        model_name: str
            String with the model name.

        """
        name = self.models.pop(ml_name, None)
        logger.info("Model with name %s deleted from the database." % name)

    def add_recharge(self, ml, rfunc, name="recharge", **kwargs):
        """Adds a recharge element to the time series model. The
        selection of the precipitation and evaporation time series is based
        on the shortest distance to the a stresses in the stresseslist.

        Returns
        -------

        """
        key = ml.oseries.name
        prec_name = self.get_nearest_stresses(key, kind="prec").iloc[0][0]
        prec = self.stresses.loc[prec_name, "series"]
        evap_name = self.get_nearest_stresses(key, kind="evap").iloc[0][0]
        evap = self.stresses.loc[evap_name, "series"]

        recharge = ps.StressModel2([prec, evap], rfunc, name=name, **kwargs)

        ml.add_stressmodel(recharge)

    def get_nearest_stresses(self, oseries=None, stresses=None, kind=None,
                             n=1):
        """Method to obtain the nearest (n) stresses of a specific kind.

        Parameters
        ----------
        oseries: str
            String with the name of the oseries
        kind:
            String with the name of the stresses
        n: int
            Number of stresses to obtain

        Returns
        -------
        stresses:
            List with the names of the stresses.

        """

        distances = self.get_distances(oseries, stresses, kind)

        sorted = pd.DataFrame(columns=np.arange(n))

        for series in distances.index:
            series = pd.Series(distances.loc[series].sort_values().index[:n],
                               name=series)
            sorted = sorted.append(series)

        return sorted

    def get_distances(self, oseries=None, stresses=None, kind=None, ):
        """Method to obtain the distances in meters between the stresses and
        oseries.

        Parameters
        ----------
        oseries: str or list of str
        stresses: str or list of str
        kind: str

        Returns
        -------
        distances: pandas.DataFrame
            Pandas DataFrame with the distances between the oseries (index)
            and the stresses (columns).

        """
        if isinstance(oseries, str):
            oseries = [oseries]
        elif oseries is None:
            oseries = self.oseries.index

        if stresses is None and kind is None:
            stresses = self.stresses.index
        elif stresses is None:
            stresses = self.stresses[self.stresses.kind == kind].index

        xo = pd.to_numeric(self.oseries.loc[oseries, "x"])
        xt = pd.to_numeric(self.stresses.loc[stresses, "x"])
        yo = pd.to_numeric(self.oseries.loc[oseries, "y"])
        yt = pd.to_numeric(self.stresses.loc[stresses, "y"])

        xh, xi = np.meshgrid(xt, xo)
        yh, yi = np.meshgrid(yt, yo)

        distances = pd.DataFrame(np.sqrt((xh - xi) ** 2 + (yh - yi) ** 2),
                                 index=oseries, columns=stresses)

        return distances

    def get_parameters(self, parameters, models=None, param_value="optimal"):
        """Method to get the parameters from each model. NaN-values are
        returned when the parameters is not present in the model.

        Parameters
        ----------
        parameters: list
            List with the names of the parameters. The parameter does not
            have to be used in all models.
        models: list
            List with the names of the models. These have to be in the
            Project models dictionary.
        param_value: str
            String with the parameter value that needs to be collected:
            Options are: initial, optimal (default), pmax, pmin and vary.

        Returns
        -------
        data: pandas.DataFrame
            Returns a pandas DataFrame with the models name as the index and
            the parameters as columns. A pandas Series is returned when only
            one parameter values is collected.

        """
        if models is None:
            models = self.models.keys()

        data = pd.DataFrame(index=models, columns=parameters)

        for ml_name in models:
            ml = self.models[ml_name]
            for parameter in parameters:
                if parameter in ml.parameters.index:
                    value = ml.parameters.loc[parameter, param_value]
                    data.loc[ml_name, parameter] = value

        data = data.squeeze()
        return data.astype(float)

    def get_statistics(self, statistics, models=None, **kwargs):
        """Method to get the statistics for each model.

        Parameters
        ----------
        statistics: list
            List with the names of the statistics to calculate for each model.
        models: list
            List with the names of the models. These have to be in the
            Project models dictionary.

        Returns
        -------
        data: pandas.DataFrame



        """
        if models is None:
            models = self.models.keys()

        data = pd.DataFrame(index=models, columns=statistics)

        for ml_name in models:
            ml = self.models[ml_name]
            for statistic in statistics:
                value = ml.stats.__getattribute__(statistic)(**kwargs)
                data.loc[ml_name, statistic] = value

        data = data.squeeze()
        return data.astype(float)

    def get_locations_geodataframe(self, models=None, **kwargs):
        import geopandas as gpd
        from shapely.geometry import Point

        if models is None:
            models = self.models.keys()

        data = pd.DataFrame(index=models)

        data = data.join(self.oseries.loc[models, "z"])
        data["geometry"] = [Point(xy[0], xy[1]) for xy in
                            self.oseries.loc[models, ["x", "y"]].values]
        data = gpd.GeoDataFrame(data, geometry="geometry", **kwargs)
        return data

    def get_metadata(self, meta=None):
        metadata = dict(
            projection=None
        )
        if meta:
            metadata.update(meta)

        return metadata

    def _get_file_info(self):
        file_info = dict()
        file_info["date_created"] = pd.Timestamp.now()
        file_info["date_modified"] = pd.Timestamp.now()
        file_info["pastas_version"] = ps.__version__
        try:
            file_info["owner"] = os.getlogin()
        except:
            file_info["owner"] = "Unknown"
        return file_info

    def dump(self, fname=None, **kwargs):
        """Method to write a Pastas project to a file.

        Parameters
        ----------
        fname

        Returns
        -------

        """
        data = self.dump_data(**kwargs)
        return ps.io.base.dump(fname, data)

    def dump_data(self, series=False, metadata=True, sim_series=False):
        """Method to export a Pastas Project and return a dictionary with
        the data to be exported.

        Parameters
        ----------
        fname: string
            string with the name and optionally the file-extension.

        Returns
        -------
        message: str
            Returns a message if export was successful or not.

        """
        data = dict(
            name=self.name,
            models=dict(),
            metadata=self.metadata,
            file_info=self.file_info
        )

        # Series DataFrame
        data["oseries"] = self._series_to_dict(self.oseries)
        data["stresses"] = self._series_to_dict(self.stresses)

        # Models
        data["models"] = dict()
        for name, ml in self.models.items():
            data["models"][name] = ml.dump_data(series=series,
                                                metadata=metadata,
                                                sim_series=sim_series,
                                                file_info=False)

        return data

    def _series_to_dict(self, series):
        series = series.to_dict(orient="index")

        for name in series.keys():
            ts = series[name]["series"]
            series[name]["series"] = ts.dump(series=True)

        return series
