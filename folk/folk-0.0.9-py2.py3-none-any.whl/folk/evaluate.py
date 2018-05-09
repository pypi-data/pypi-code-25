"""Evalute folk parameterized pipelines and models."""

import time
from datetime import datetime

from pdutil.transform import x_y_by_col_lbl
from sklearn.model_selection import (
    cross_val_score,
)

from .metricsdb import (
    MetricKey,
    write_experiment_res,
)


def _print_func_by_verbosity(verbose):
    if verbose:
        return print
    return lambda x: None


def eval_model_by_params(
        run_id, model, model_id, df, lbl_col, params, metric_db=None,
        n_folds=None, n_jobs=None, verbose=None):
    _print = _print_func_by_verbosity(verbose)
    if n_folds is None:
        n_folds = 5
    if n_jobs is None:
        n_jobs = 1
    _print("  - Testing {}...".format(model_id))
    X, y = x_y_by_col_lbl(df, lbl_col)
    _print("    Starting cross validation at {}".format(datetime.now()))
    _print('    Performing {}-fold cross validation...'.format(n_folds))
    start = time.time()
    scores = cross_val_score(
        model, X=X, y=y, cv=n_folds, scoring='accuracy',
        n_jobs=n_jobs,
    )
    end = time.time()
    total_time = end - start
    per_fold_time = total_time / n_folds
    _print("    Finished cross validation at {}".format(datetime.now()))
    _print("    Cross validation took {:.2f} s ({:.2f} per fold)".format(
        total_time, per_fold_time))
    acc_mean = scores.mean()
    acc_std = scores.std()
    _print("    Accuracy: {:.2f} (+/- {:.2f})".format(
        scores.mean(), scores.std() * 2))
    n_classes = len(df[lbl_col].unique())
    if metric_db:
        _print("    Writing results to db...")
        write_experiment_res(
            res_doc={
                MetricKey.RUN_ID: run_id,
                MetricKey.MODEL_ID: model_id,
                MetricKey.LBL_COL: lbl_col,
                MetricKey.ACC_MEAN: acc_mean,
                MetricKey.ACC_STD: acc_std,
                MetricKey.N_FOLDS: n_folds,
                MetricKey.N_JOBS: n_jobs,
                MetricKey.CROSS_VAL_TIME: total_time,
                MetricKey.FOLD_TIME: per_fold_time,
                MetricKey.DATASET_SIZE: len(df),
                MetricKey.N_CLASS: n_classes,
                **params,
            },
            db_name=metric_db,
            run_id=run_id,
        )


def eval_pmodel_by_params(
        run_id, pipeline, pmodel, raw_df, pipe_params, metric_db=None,
        n_folds=None, n_jobs=None, verbose=None):
    _print = _print_func_by_verbosity(verbose)
    _print("=============================")
    _print("Testing parameterized model on pipeline with "
           "params {}".format(pipe_params))
    _print("Starting to apply pipeline at {}".format(datetime.now()))
    _print("Applying pipeline...")
    start = time.time()
    if verbose:
        df = pipeline.fit_transform(raw_df, verbose=True)
    else:
        df = pipeline.fit_transform(raw_df)
    end = time.time()
    pipe_time = end - start
    _print("Finished applying pipeline at {}".format(datetime.now()))
    _print("Pipeline application took {:.2f} seconds.".format(pipe_time))
    _print("Dataset size: {}".format(len(df)))
    _print("Number of columns: {}".format(len(df.columns)))
    _print("Resulting dataset size: {}".format(len(df)))
    _print("Resulting columns: {}".format(sorted(list(df.columns))))
    partial_pmodel = pmodel.partial(pipe_params)
    j = 1
    for model, mparams in partial_pmodel.model_n_params_iter():
        model_id = pmodel.model_id_by_params(mparams)
        _print("-------- Model {} --------".format(j))
        _print("Testing model with params: {}".format(mparams))
        full_params = mparams.copy()
        full_params.update(pipe_params)
        eval_model_by_params(
            run_id=run_id,
            model=model,
            model_id=model_id,
            df=df,
            lbl_col=pipe_params['lbl_col'],
            params=full_params,
            n_folds=n_folds,
            n_jobs=n_jobs,
            metric_db=metric_db,
            verbose=verbose,
        )
        j += 1
    _print("=============================\n")


def eval_param_pipeline_n_model(
        param_pipeline, param_model, dataset, metric_db=None, n_folds=None,
        n_jobs=None, verbose=None):
    """Evaluates the given parameterized pipeline and model.

    Parameters
    ----------
    param_pipeline : folk.ParameterizedPipeline
        The parameterized pipeline to evaluate.
    param_model : folk.ParameterizedModel
        The parameterized model to evaluate.
    dataset : pandas.DataFrame
        The dataset to evaluate the parameterized pipeline and model on.
    metric_db : str, optional
        The name of the folk metrics db to write results to. Must be included
        in folk's configuration. If not given, results are not written to db.
    n_folds : int, optional
        The number of folds to perform cross validation on. Defaults to 5.
    n_jobs : int, optional
        The number of threads to run evaluation on. Defaults to 1.
    verbose : bool, optional
        If set to True, informative messages are _printed. Defaults to False.
    """
    _print = _print_func_by_verbosity(verbose)
    run_at = datetime.utcnow()
    run_id = str(run_at.timestamp()).replace('.', '')
    i = 1
    for pipeline, params in param_pipeline.pipe_n_params_iter():
        _print("Pipeline #{}".format(i))
        eval_pmodel_by_params(
            run_id=run_id,
            pipeline=pipeline,
            pmodel=param_model,
            raw_df=dataset,
            pipe_params=params,
            metric_db=metric_db,
            n_folds=n_folds,
            n_jobs=n_jobs,
            verbose=verbose,
        )
        i += 1
