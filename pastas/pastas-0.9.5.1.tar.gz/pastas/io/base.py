"""
Import model
"""

import importlib
import os

import pandas as pd

import pastas as ps


def load(fname, **kwargs):
    """Method to load models from file supported by the pastas library.

    Parameters
    ----------
    fname: str
        string with the name of the file to be imported including the file
        extension.
    kwargs: extension specific

    """
    # Dynamic import of the export module
    ext = os.path.splitext(fname)[1]
    load_mod = importlib.import_module("pastas.io" + ext)

    # Get dicts for all data sources
    data = load_mod.load(fname, **kwargs)

    # Determine whether it is a Pastas Project or a Pastas Model
    if "models" in data.keys():
        ml = load_project(data)
        kind = "Project"
    else:
        ml = load_model(data)
        kind = "Model"

    print("Pastas %s from file %s succesfully loaded. The Pastas-version "
          "this file was created with was %s. Your current version of Pastas "
          "is: %s" % (kind, fname, data["file_info"]["pastas_version"],
                      ps.__version__))

    return ml


def load_project(data):
    """Method to load a Pastas project.

    Parameters
    ----------
    data: dict
        Dictionary containing all information to construct the project.

    Returns
    -------
    mls: Pastas.Project class
        Pastas Project class object

    """

    mls = ps.Project(name=data["name"])

    mls.metadata = data["metadata"]
    mls.file_info = data["file_info"]

    mls.stresses = pd.DataFrame(data["stresses"],
                                columns=data["stresses"].keys()).T

    mls.oseries = pd.DataFrame(data["oseries"],
                               columns=data["oseries"].keys()).T

    for ml_name, ml in data["models"].items():
        name = ml["oseries"]["name"]
        ml["oseries"]["series"] = mls.oseries.loc[name, "series"]
        if ml["stressmodels"]:
            for ts in ml["stressmodels"].values():
                for i, stress in enumerate(ts["stress"]):
                    stress_name = stress["name"]
                    ts["stress"][i]["series"] = mls.stresses.loc[
                        stress_name, "series"]

        try:
            ml = load_model(ml)
            mls.models[ml_name] = ml
        except:
            try:
                mls.del_model(ml_name)
            except:
                pass
            print("model", ml_name, "could not be added")
    return mls


def load_model(data):
    # Create model
    oseries = ps.TimeSeries(**data["oseries"])

    if "constant" in data.keys():
        constant = data["constant"]
    else:
        constant = False

    if "settings" in data.keys():
        settings = data["settings"]
    else:
        settings = dict()

    if "metadata" in data.keys():
        metadata = data["metadata"]
    else:
        metadata = dict(name="Model")  # Make sure there is a name

    if "name" in data.keys():
        name = data["name"]
    else:
        name = metadata["name"]

    if "noisemodel" in data.keys():
        noise = True
    else:
        noise = False

    ml = ps.Model(oseries, constant=constant, noisemodel=noise, name=name,
                  metadata=metadata, settings=settings)
    if "file_info" in data.keys():
        ml.file_info.update(data["file_info"])

    # Add stressmodels
    for name, ts in data["stressmodels"].items():
        stressmodel = getattr(ps.stressmodels, ts["stressmodel"])
        ts.pop("stressmodel")
        ts["rfunc"] = getattr(ps.rfunc, ts["rfunc"])
        for i, stress in enumerate(ts["stress"]):
            ts["stress"][i] = ps.TimeSeries(**stress)
        stressmodel = stressmodel(**ts)
        ml.add_stressmodel(stressmodel)

    # Add transform
    if "transform" in data.keys():
        transform = getattr(ps.transform, data["transform"]["transform"])
        data["transform"].pop("transform")
        transform = transform(**data["transform"])
        ml.add_transform(transform)

    # Add noisemodel if present
    if "noisemodel" in data.keys():
        n = getattr(ps.noisemodels, data["noisemodel"]["type"])()
        ml.add_noisemodel(n)

    # Add parameters, use update to maintain correct order
    ml.parameters = ml.get_init_parameters(noise=ml.settings["noise"])
    ml.parameters.update(data["parameters"])
    ml.parameters = ml.parameters.apply(pd.to_numeric, errors="ignore")
    return ml


def dump(fname, data, **kwargs):
    """Method to save a pastas-model to a file. The specific dump-module is
    automatically chosen based on the provided file extension.

    Parameters
    ----------
    fname: str
        string with the name of the file, including a supported
        file-extension. Currently supported extension are: .pas.
    data: dict
        dictionary with the information to store.
    kwargs: extension specific keyword arguments can be provided using kwargs.

    Returns
    -------
    message:
        Message if the file-saving was successful.

    """
    ext = os.path.splitext(fname)[1]
    dump_mod = importlib.import_module("pastas.io" + ext)
    return dump_mod.dump(fname, data, **kwargs)
