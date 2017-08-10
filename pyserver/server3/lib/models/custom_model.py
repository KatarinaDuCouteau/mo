import logging
import inspect

import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split

from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from server3.utility.str_utility import generate_args_str
from server3.service.custom_log_handler import MetricsHandler
from tensorflow.contrib.learn.python.learn import monitors
from tensorflow.contrib.learn.python.learn.estimators import estimator


def custom_model(conf, model_fn, input_data, **kw):
    """
    :param model_fn:
    :param params:
    :param input_data:
    :param kw:
    :return:
    """
    # predict_x = kw.pop('predict_x', None)
    # project_id = kw.pop('project_id', None)
    project_id = kw.pop('project_id', None)
    result_sds = kw.pop('result_sds', None)

    est_params = conf.get('estimator', None)
    fit_params = conf.get('fit', {})
    eval_params = conf.get('evaluate', {})

    if result_sds is None:
        raise RuntimeError('no result sds id passed to model')
    # if project_id is None:
    #     raise RuntimeError('no project_id input')

    # def eval_input_fn():
    #     return input_fn(test, continuous_cols, categorical_cols, label_col)
    return custom_model_help(model_fn, input_data, project_id, result_sds,
                             est_params, fit_params,
                             eval_params)


def custom_model_help(model_fn, input_data, project_id, result_sds,
                      est_params=None, fit_params=None,
                      eval_params=None):
    tf.logging.set_verbosity(tf.logging.INFO)

    # add handler to catch tensorflow log message
    mh = MetricsHandler()
    # pass result staging data set for logger to save results
    mh.result_sds = result_sds
    mh.project_id = project_id
    logger = logging.getLogger('tensorflow')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(mh)

    # input_data 是一整个数据集，分割 为训练集和测试集
    # X_train, X_test, y_train, y_test = train_test_split(
    #     input_data['df_features'], input_data['df_labels'],
    #     test_size=0.20,
    #     random_state=42)

    # input_data 已分割 为训练集和测试集
    X_train, X_test, y_train, y_test = \
        input_data['x_tr'], input_data['x_te'],\
        input_data['y_tr'], input_data['y_tr']

    train_input_fn = get_input_fn(model_name=input_data['model_name'],
                                  df_features=X_train,
                                  df_labels=y_train)
    eval_input_fn = get_input_fn(model_name=input_data['model_name'],
                                 df_features=X_test,
                                 df_labels=y_test)
    if ((input_data['model_name'] in ['Linear_classifier', 'Randomforest'])
        and est_params['args']['num_classes'] == 2) or input_data[
        'model_name'] == 'svm':
        validation_metrics = {
            "accuracy":
                tf.contrib.learn.MetricSpec(
                    metric_fn=tf.contrib.metrics.streaming_accuracy,
                    prediction_key=None),
            "precision":
                tf.contrib.learn.MetricSpec(
                    metric_fn=tf.contrib.metrics.streaming_precision,
                    prediction_key=None),
            "recall":
                tf.contrib.learn.MetricSpec(
                    metric_fn=tf.contrib.metrics.streaming_recall,
                    prediction_key=None),
            "confusion_matrix":
                tf.contrib.learn.MetricSpec(
                    metric_fn=tf.contrib.metrics.confusion_matrix,
                    prediction_key=None)
        }
    else:
        validation_metrics = {}

    val_monitor = tf.contrib.learn.monitors.ValidationMonitor(
        input_fn=eval_input_fn,
        eval_steps=1,
        every_n_steps=100,
        metrics=validation_metrics)

    # init model
    estimator = \
        tf.contrib.learn.Estimator(model_fn=model_fn,
                                   model_dir=None,
                                   config=
                                   tf.contrib.learn.RunConfig(
                                       save_checkpoints_steps=
                                       val_monitor._every_n_steps),
                                   params=est_params[
                                       'args'])

    # fit
    # result = {}
    # evaluation_times = max(fit_params['args']['steps'] / 100, 1)
    # while evaluation_times > 0:
    #     fit_params['args']['steps'] = 100
    #     estimator.fit(input_fn=train_input_fn, monitors=[
    # validation_monitor], **fit_params['args'])
    #     # evaluate
    #     metrics = estimator.evaluate(input_fn=eval_input_fn,
    #                                  **eval_params['args'])
    #     result.update({
    #         'eval_metrics': metrics
    #     })
    #     evaluation_times -= 1

    # fit

    estimator.fit(input_fn=train_input_fn,
                  monitors=[val_monitor],
                  **fit_params['args'])
    # evaluate
    metrics = estimator.evaluate(input_fn=eval_input_fn,
                                 metrics=validation_metrics,
                                 **eval_params['args'])

    result = {}
    result.update({
        'eval_metrics': metrics
    })

    # predict
    predict_feature = input_data.get('predict', None)
    if predict_feature:
        predictions = estimator.predict(predict_feature, as_iterable=True)
        result['predictions'] = predictions

    return result


def custom_model_to_str(conf, head_str, **kw):
    project_id = kw.get('project_id', None)
    result_sds = kw.get('result_sds', None)
    est_params = conf.get('estimator', None)['args']
    fit_params = conf.get('fit', {})
    eval_params = conf.get('evaluate', {})
    result_sds_id = result_sds['id']
    str_model = ''
    str_model += head_str
    str_model += "project_id = '%s'\n" % project_id
    str_model += "result_sds = staging_data_set_business.get_by_id('%s')\n" % \
                 result_sds_id
    str_model += inspect.getsource(get_input_fn)
    est_params = str(est_params)
    custom_model_help_str = inspect.getsource(custom_model_help)
    custom_model_help_str = \
        custom_model_help_str.replace("est_params['args']", est_params)
    custom_model_help_str = \
        custom_model_help_str.replace("**fit_params['args']",
                                      generate_args_str(
                                          fit_params['args']))
    custom_model_help_str = \
        custom_model_help_str.replace("**eval_params['args']",
                                      generate_args_str(eval_params['args']))
    str_model += custom_model_help_str
    str_model += 'print(custom_model_help(model_fn, input_dict, project_id, ' \
                 'result_sds))'
    return str_model


def get_input_fn(model_name, df_features, df_labels=None):
    assert isinstance(df_features, pd.DataFrame)

    # has labels  classification and regression
    if df_labels is not None:
        assert isinstance(df_labels, pd.DataFrame)

        if model_name == 'logistic_regressor':
            # labels type should be float
            def input_fn():
                return {k: constant_op.constant(df_features[k].values,
                                                shape=df_labels.shape,
                                                dtype=dtypes.float32) for k in
                        df_features.columns}, constant_op.constant(
                    df_labels[df_labels.columns[0]].values,
                    shape=df_labels.shape, dtype=dtypes.float32)
        else:
            def input_fn():
                return {k: constant_op.constant(df_features[k].values,
                                                shape=df_labels.shape,
                                                dtype=dtypes.float32) for k in
                        df_features.columns}, constant_op.constant(
                    df_labels[df_labels.columns[0]].values,
                    shape=df_labels.shape, dtype=dtypes.int32)

    # no labels  clustering
    else:
        def input_fn():
            return {k: constant_op.constant(df_features[k].values,
                                            shape=[df_features.shape[0], 1],
                                            dtype=dtypes.float32) for k in
                    df_features.columns}, None
    return input_fn


if __name__ == '__main__':
    pass
    from server3.business import staging_data_set_business
    import pandas as pd
    from sklearn.datasets.samples_generator import make_blobs
    import numpy as np

    # 生成测试数据
    X, y = make_blobs(n_samples=20, centers=2,
                      random_state=2, cluster_std=0.60, n_features=2)

    custom_feature = pd.DataFrame(data=np.c_[X],
                                  columns=['f1', 'f2'])
    custom_label = pd.DataFrame(data=y,
                                columns=['target'])

    input = {
        'model_name': 'gmm',
        'df_fetures': custom_feature,
        'df_labels': None,
    }

    params = {
        'estimator': {
            'args': {
                "num_clusters": 2,
                "random_seed": 5,
                "covariance_type": "diag",
                "update_params": "wmc"
            }
        },
        'fit': {
            "args": {
                "steps": 30
            }
        },
        'evaluate': {
            'args': {
                'steps': 1
            }
        }
    }

    sds = staging_data_set_business.get_by_id('595cb76ed123ab59779604c3')
    from server3.lib.models.gmm_cluster import gmm_cluster_model_fn

    result = custom_model(params, gmm_cluster_model_fn, input, result_sds=sds)
    print(result)