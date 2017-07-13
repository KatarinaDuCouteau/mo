# -*- coding: UTF-8 -*-
"""
spark server3.service used to access spark cluster

Author: Bingwei Chen
Date: 2017.07.11
"""
# ------------------------------ system package ------------------------------
import os
import sys

os.environ['PYSPARK_PYTHON'] = '/usr/local/bin/python3.6'
sys.path.append("/usr/local/spark/python")
from pyspark import SparkContext
from pyspark import SparkConf

from keras import layers
from keras.models import Sequential


# ------------------------------ self package ------------------------------
# sys.path.append("/Users/chen/myPoject/gitRepo/goldersgreen/")
# sys.path.append("/root/project/git_repo/goldersgreen/server3")


# ------------------------------ const ------------------------------
SPARK_EXECUTOR_MEMORY = '4g'
MASTER_ADDRESS = "spark://10.52.14.188:7077"

SERVER3_PATH = "/Users/chen/myPoject/gitRepo/goldersgreen/pyserver/lib/server3.zip"
# KERAS_SEQ_PATH = '/Users/chen/myPoject/gitRepo/goldersgreen/server3/lib/models/keras_seq.py'
SPARK_MODELS = \
    '/Users/chen/myPoject/gitRepo/goldersgreen/pyserver/server3/lib/models/spark_models.py'


# ------------------------------ spark code ------------------------------
def CreateSparkContext():
    sparkConf = SparkConf() \
        .setAppName("hyperparameter_tuning") \
        .set("spark.ui.showConsoleProgress", "false") \
        .setMaster(MASTER_ADDRESS) \
        .set("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
    sc = SparkContext(conf=sparkConf, pyFiles=[SPARK_MODELS])
    print("master = " + sc.master)
    SetLogger(sc)
    SetPath(sc)
    return (sc)


def SetLogger(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org").setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)
    logger.LogManager.getRootLogger().setLevel(logger.Level.ERROR)


def SetPath(sc):
    global Path
    Path = "file:/usr/local/spark/"


# for hyper parameters tuning
def hyper_parameters_tuning(conf_grid, conf):
    """

    :param conf_grid:
    :param conf: template conf with data
    :param staging_data_set_id:
    :param kwargs:
    :return:
    """
    def model_training(conf_obj, conf_with_data_bc):
        # import logging
        # logger = logging.getLogger('py4j')
        # logger.error("My test info statement")
        # log4jLogger = sc._jvm.org.apache.log4j
        # LOGGER = log4jLogger.LogManager.getLogger(__name__)
        # LOGGER.error("Started")
        # from py file import code (if it has dependency, using zip to access it)
        # from server3.lib.models.keras_seq import keras_seq

        # staging_data_set_id 595cb76ed123ab59779604c3
        # from server3.business.staging_data_set_business import get_by_id

        # get data by broadcast
        conf_obj["fit"]["x_train"] = conf_with_data_bc.value["fit"]["x_train"]
        conf_obj["fit"]["y_train"] = conf_with_data_bc.value["fit"]["y_train"]
        conf_obj["fit"]["x_val"] = conf_with_data_bc.value["fit"]["x_val"]
        conf_obj["fit"]["y_val"] = conf_with_data_bc.value["fit"]["y_val"]
        conf_obj["evaluate"]["x_test"] = conf_with_data_bc.value["evaluate"]["x_test"]
        conf_obj["evaluate"]["y_test"] = conf_with_data_bc.value["evaluate"]["y_test"]
        print("conf_obj_fit_x_train", conf_obj["fit"]["x_train"])

        # LOGGER.warning(conf_obj["fit"]["x_train"])


        result = spark_models.keras_seq(conf, result_sds="11")
        conf_obj["fit"].pop("x_train")
        conf_obj["fit"].pop("y_train")
        conf_obj["fit"].pop("x_val")
        conf_obj["fit"].pop("y_val")
        conf_obj["evaluate"].pop("x_test")
        conf_obj["evaluate"].pop("y_test")
        return {
            "result": result,
            "conf": conf_obj,
        }

    print("begin_hyper_parameters_tuning")
    # create spark context
    sc = CreateSparkContext()
    # temp import with zip package
    import spark_models

    # parallelize parameters_grid to rdd
    print("conf_grid_len", len(conf_grid))
    print("conf_grid", conf_grid)

    # broadcast conf with data
    conf_with_data_bc = sc.broadcast(conf)

    rdd = sc.parallelize(conf_grid, numSlices=len(conf_grid))
    # run models on spark cluster
    results = rdd.map(lambda conf_obj: model_training(conf_obj, conf_with_data_bc))
    res = results.collect()
    sc.stop()
    return res


# ------------------------------ service ------------------------------s
# def get_parameters_grid(conf, hyper_parameters):
#     import itertools
#     import copy
#
#     epochs = conf['fit']['args']['epochs']
#     batch_size = conf['fit']['args']['batch_size']
#
#     all_experiments = list(itertools.product(epochs, batch_size))
#     parameters_grid = []
#     for ex in all_experiments:
#         conf_template = copy.deepcopy(conf)
#         conf_template['fit']['args']['epochs'] = ex[0]
#         conf_template['fit']['args']['batch_size'] = ex[1]
#         parameters_grid.append(conf_template)
#     # print(all_experiments)
#     # for p in parameters_grid:
#     #     print(p)
#     return parameters_grid


def get_conf_grid(conf, hyper_parameters):
    """using template conf and hyper_parameters to generate conf grid

    :param conf: (json) the template of conf
    :param hyper_parameters: (json) the template of hyper_parameters
    :return: conf grid (array) which contains a list of conf generated by hyper parameters
    """
    import copy
    parameters_grid = hyper_parameters_to_grid(hyper_parameters)
    conf_grid = []
    print("transfer grid to conf")
    for e in parameters_grid:
        # get the conf template
        conf_template = copy.deepcopy(conf)
        # put the attributes of hyper parameters to conf
        # epochs
        if e.get('epochs'):
            conf_template['fit']['args']['epochs'] = e.get('epochs')
        # batch_size
        if e.get("batch_size"):
            conf_template['fit']['args']['batch_size'] = e.get('batch_size')
            conf_template['evaluate']['args']['batch_size'] = e.get('batch_size')
        if e.get("optimizer"):
            conf_template['compile']['optimizer']["name"] = e.get('optimizer')
        if e.get("lr"):
            conf_template['compile']['optimizer']['args']['lr'] = e.get('lr')
        if e.get('momentum'):
            conf_template['compile']['optimizer']['args']['momentum'] = e.get('momentum')

        # layer 层
        # 隐含层神经元数量调优
        for layer_index in range(0, len(conf_template['layers'])):
            if e['layers'][layer_index].get("units"):
                conf_template['layers'][layer_index]['args']['units'] = \
                    e['layers'][layer_index].get("units")
            if e['layers'][layer_index].get("activation"):
                conf_template['layers'][layer_index]['args']['activation'] = \
                    e['layers'][layer_index].get("activation")
            if e['layers'][layer_index].get("init"):
                conf_template['layers'][layer_index]['args']['init'] = \
                    e['layers'][layer_index].get("init")
            if e['layers'][layer_index].get("rate"):
                conf_template['layers'][layer_index]['args']['rate'] = \
                    e['layers'][layer_index].get("rate")

        # print("conf_template", conf_template)
        conf_grid.append(conf_template)
    return conf_grid


def hyper_parameters_to_grid(hyper_parameters):
    """transfer the hyper parameters json to grid which contains all possible of conf attributes

    :param hyper_parameters: (json) the template of hyper_parameters
    :return: hyper parameters grid (array) which contains a list of hyper parameters
    """
    import itertools
    # get the hyperparameters if it exist
    args = []
    add_hy_to_array('epochs', hyper_parameters['epochs'], args)
    add_hy_to_array('batch_size', hyper_parameters['batch_size'], args)
    add_hy_to_array('optimizer', hyper_parameters['optimizer'], args)
    add_hy_to_array('lr', hyper_parameters['lr'], args)
    add_hy_to_array('momentum', hyper_parameters['momentum'], args)

    # layer 层
    layers_grid = get_grid_of_layer(hyper_parameters['layers'])
    # add_hy_to_array('init_mode', hyper_parameters['init_mode'], args)
    # add_hy_to_array('activation', hyper_parameters['activation'], args)
    # add_hy_to_array('dropout_rate', hyper_parameters['dropout_rate'], args)
    # add_hy_to_array('weight_constraint', hyper_parameters['weight_constraint'], args)
    # add_hy_to_array('neurons', hyper_parameters['neurons'], args)

    # get all experiment
    grid = list(itertools.product(*args))
    # flat the experiment
    flat_grid = []
    for e in grid:
        obj = {}
        for i in e:
            obj.update(**i)
        # print("obj", obj)
        flat_grid.append(obj)
    # print(flat_grid)

    # conbine flat grid and layer grid
    complete_grid = list(itertools.product(flat_grid, layers_grid))
    flat_complete_grid = []
    for e in complete_grid:
        obj = {}
        for i in e:
            obj.update(**i)
        flat_complete_grid.append(obj)

    # print("layers_grid len", len(layers_grid))
    # print("flat_grid len", len(flat_grid))
    # print("flat_complete_grid len", len(flat_complete_grid))
    # print("flat_complete_grid", flat_complete_grid)
    return flat_complete_grid


def get_grid_of_layer(layers_json):
    """transfer the layer json to grid which contains all possible of layer attributes

    :param layers_json: (json) the template of layers in hyper_parameters
    :return: layer hyper paremeters grid (array) which contains a list of of layers in
    hyper parameters
    """
    import itertools
    # get the hyperparameters if it exist
    layers_args = []
    for layer in layers_json:
        args = []
        add_hy_to_array('units', layer['args'].get('units'), args)
        add_hy_to_array('activation', layer['args'].get('activation'), args)
        add_hy_to_array('init', layer['args'].get('init'), args)
        add_hy_to_array('rate', layer['args'].get('rate'), args)

        grid = list(itertools.product(*args))

        flat_grid = []
        for e in grid:
            obj = {}
            for i in e:
                obj.update(**i)
            # print("obj", obj)
            flat_grid.append(obj)
        # print(flat_grid)
        layers_args.append(flat_grid)
    layers_grid = list(itertools.product(*layers_args))
    new_grid = []
    for e in layers_grid:
        new_grid.append({
            "layers": e
        })
    return new_grid


def transfer(key, value):
    """help function used to convert key-array to key-value
    eg: transfer(a,[1,2]) -> [{a:1},{a:2}]
    :param key: (string) key
    :param value: (array) value
    :return: (array) which may contains several key-value
    """
    new_array = []
    # if the value is not array
    if type(value) == list:
        for i in value:
            new_array.append({
                key: i
            })
        return new_array
    else:
        return [{key: value}]


def add_hy_to_array(key, value, args):
    """add hyper parameters attributes to array before itertools

    :param key: (string) key of hyper parameters
    :param value: (array) value of hyper parameters
    :param args: (array) [[h1:1,h1:2],[h2:1,h2:2]]
    :return:
    """
    # if the attribute not exist
    if value:
        obj_array = transfer(key, value)
        # if empty array
        if obj_array:
            args.append(obj_array)
# ------------------------------ service ------------------------------e


if __name__ == "__main__":
    # 获取数据
    from keras import utils
    import numpy as np

    x_train = np.random.random((1000, 20))
    y_train = utils.to_categorical(np.random.randint(10, size=(1000, 1)), num_classes=10)
    x_test = np.random.random((100, 20))
    y_test = utils.to_categorical(np.random.randint(10, size=(100, 1)), num_classes=10)
    parametersGrid = [
        {'layers': [{'name': 'Dense',
                     'args': {'units': 64, 'activation': 'relu',
                              'input_shape': [
                                  20, ]}},
                    {'name': 'Dropout',
                     'args': {'rate': 0.5}},
                    {'name': 'Dense',
                     'args': {'units': 64, 'activation': 'relu'}},
                    {'name': 'Dropout',
                     'args': {'rate': 0.5}},
                    {'name': 'Dense',
                     'args': {'units': 10, 'activation': 'softmax'}}
                    ],
         'compile': {'loss': 'categorical_crossentropy',
                     'optimizer': 'SGD',
                     'metrics': ['accuracy']
                     },
         'fit': {'x_train': x_train,
                 'y_train': y_train,
                 'x_val': x_test,
                 'y_val': y_test,
                 'args': {
                     'epochs': 20,
                     'batch_size': 128
                 }
                 },
         'evaluate': {'x_test': x_test,
                      'y_test': y_test,
                      'args': {
                          'batch_size': 128
                      }
                      }
         },

        {'layers': [{'name': 'Dense',
                     'args': {'units': 64, 'activation': 'relu',
                              'input_shape': [
                                  20, ]}},
                    {'name': 'Dropout',
                     'args': {'rate': 0.5}},
                    {'name': 'Dense',
                     'args': {'units': 64, 'activation': 'relu'}},
                    {'name': 'Dropout',
                     'args': {'rate': 0.5}},
                    {'name': 'Dense',
                     'args': {'units': 10, 'activation': 'softmax'}}
                    ],
         'compile': {'loss': 'categorical_crossentropy',
                     'optimizer': 'SGD',
                     'metrics': ['accuracy']
                     },
         'fit': {'x_train': x_train,
                 'y_train': y_train,
                 'x_val': x_test,
                 'y_val': y_test,
                 'args': {
                     'epochs': 20,
                     'batch_size': 128
                 }
                 },
         'evaluate': {'x_test': x_test,
                      'y_test': y_test,
                      'args': {
                          'batch_size': 128
                      }
                      }
         }
    ]
    hyper_parameters_tuning(parametersGrid)
    pass


