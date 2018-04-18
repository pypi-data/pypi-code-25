# -*- coding:utf-8 -*-
# Author：hankcs, Hai Liang Wang<hailiang.hl.wang@gmail.com>
# Date: 2018-03-18 19:49
from __future__ import division
from __future__ import print_function

import os
import sys
import platform

from jpype import JClass, startJVM, getDefaultJVMPath, isThreadAttachedToJVM, attachThreadToJVM

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
if sys.version_info[0] < 3:
    # noinspection PyUnresolvedReferences,PyCompatibility
    reload(sys), sys.setdefaultencoding("utf-8")


def _start_jvm_for_hanlp():
    global STATIC_ROOT, hanlp_installed_data_version, HANLP_JAR_PATH, PATH_CONFIG, HANLP_JAR_VERSION, HANLP_DATA_PATH
    # Get ENV
    ENVIRON = os.environ.copy()
    # Load variables in Environment
    if "HANLP_VERBOSE" in ENVIRON:
        HANLP_VERBOSE = int(ENVIRON["HANLP_VERBOSE"])
    else:
        HANLP_VERBOSE = 0

    if "HANLP_STATIC_ROOT" in ENVIRON:
        STATIC_ROOT = ENVIRON["HANLP_STATIC_ROOT"]
        if HANLP_VERBOSE:
            print('使用环境变量 HANLP_STATIC_ROOT={}'.format(STATIC_ROOT))
        HANLP_DATA_PATH = os.path.join(STATIC_ROOT, 'data')

        def hanlp_installed_data_version():
            return '手动安装'
    else:
        from pyhanlp.static import STATIC_ROOT, hanlp_installed_data_version, HANLP_DATA_PATH
    if "HANLP_JAR_PATH" in ENVIRON:
        HANLP_JAR_PATH = ENVIRON["HANLP_JAR_PATH"]
        if HANLP_VERBOSE:
            print('使用环境变量 HANLP_JAR_PATH={}'.format(HANLP_JAR_PATH))
    else:
        from pyhanlp.static import HANLP_JAR_PATH
    if "HANLP_JVM_XMS" in ENVIRON:
        HANLP_JVM_XMS = ENVIRON["HANLP_JVM_XMS"]
    else:
        HANLP_JVM_XMS = "1g"
    if "HANLP_JVM_XMX" in ENVIRON:
        HANLP_JVM_XMX = ENVIRON["HANLP_JVM_XMX"]
    else:
        HANLP_JVM_XMX = "1g"
    PATH_CONFIG = os.path.join(STATIC_ROOT, 'hanlp.properties')
    if not os.path.exists(HANLP_JAR_PATH):
        raise ValueError(
            "配置错误: HANLP_JAR_PATH=%s 不存在" %
            HANLP_JAR_PATH)
    elif not os.path.isfile(HANLP_JAR_PATH) or not HANLP_JAR_PATH.endswith('.jar'):
        raise ValueError(
            "配置错误: HANLP_JAR_PATH=%s 不是jar文件" %
            HANLP_JAR_PATH)
    elif not os.path.exists(STATIC_ROOT):
        raise ValueError(
            "配置错误: STATIC_ROOT=%s 不存在" %
            STATIC_ROOT)
    elif not os.path.isdir(HANLP_DATA_PATH):
        if HANLP_DATA_PATH.startswith(STATIC_ROOT):
            raise ValueError(
                "配置错误: STATIC_ROOT=%s 目录下没有data文件夹" %
                STATIC_ROOT)
        else:
            raise ValueError(
                "配置错误: 数据包 %s 不存在，请修改配置文件中的root" %
                HANLP_DATA_PATH)
    elif not os.path.isfile(PATH_CONFIG):
        raise ValueError(
            "配置错误: STATIC_ROOT=%s 目录下没有hanlp.properties" %
            STATIC_ROOT)
    else:
        HANLP_JAR_VERSION = os.path.basename(HANLP_JAR_PATH)[len('hanlp-'):-len('.jar')]

        if HANLP_VERBOSE:
            print("加载 HanLP jar [%s] ..." % HANLP_JAR_PATH)
            print("加载 HanLP config [%s/hanlp.properties] ..." % (STATIC_ROOT))
            print("加载 HanLP data [%s/data] ..." % (STATIC_ROOT))
    pathsep = os.pathsep
    if platform.system().startswith('CYGWIN'):
        jvmpath = getDefaultJVMPath()
        if not jvmpath.startswith('/cygdrive'):  # CYGWIN 使用了宿主机器的JVM，必须将路径翻译为真实路径
            pathsep = ';'
            if STATIC_ROOT.startswith('/usr/lib'):
                cygwin_root = os.popen('cygpath -w /').read().strip().replace('\\', '/')
                STATIC_ROOT = cygwin_root + STATIC_ROOT[len('/usr'):]
                HANLP_JAR_PATH = cygwin_root + HANLP_JAR_PATH[len('/usr'):]
                PATH_CONFIG = cygwin_root + PATH_CONFIG[len('/usr'):]
            elif STATIC_ROOT.startswith('/cygdrive'):
                driver = STATIC_ROOT.split('/')
                cygwin_driver = '/'.join(driver[:3])
                win_driver = driver[2].upper() + ':'
                HANLP_JAR_PATH = HANLP_JAR_PATH.replace(cygwin_driver, win_driver)
                STATIC_ROOT = STATIC_ROOT.replace(cygwin_driver, win_driver)
                PATH_CONFIG = PATH_CONFIG.replace(cygwin_driver, win_driver)
    JAVA_JAR_CLASSPATH = "-Djava.class.path=%s%s%s" % (
        HANLP_JAR_PATH, pathsep, STATIC_ROOT)
    if HANLP_VERBOSE: print("设置 JAVA_JAR_CLASSPATH [%s]" % JAVA_JAR_CLASSPATH)
    # 启动JVM
    startJVM(
        getDefaultJVMPath(),
        JAVA_JAR_CLASSPATH,
        "-Xms%s" %
        HANLP_JVM_XMS,
        "-Xmx%s" %
        HANLP_JVM_XMX)


_start_jvm_for_hanlp()


def _attach_jvm_to_thread():
    """
    use attachThreadToJVM to fix multi-thread issues: https://github.com/hankcs/pyhanlp/issues/7
    """
    if not isThreadAttachedToJVM():
        attachThreadToJVM()


class SafeJClass(object):
    def __init__(self, proxy):
        """
        JClass的线程安全版
        :param proxy: Java类的完整路径，或者一个Java对象
        """
        self._proxy = JClass(proxy) if type(proxy) is str else proxy

    def __getattr__(self, attr):
        _attach_jvm_to_thread()
        return getattr(self._proxy, attr)

    def __call__(self, *args):
        if args:
            proxy = self._proxy(*args)
        else:
            proxy = self._proxy()
        return SafeJClass(proxy)


class LazyLoadingJClass(object):
    def __init__(self, proxy):
        """
        惰性加载Class。仅在实际发生调用时才触发加载，适用于包含资源文件的静态class
        :param proxy:
        """
        self._proxy = proxy

    def __getattr__(self, attr):
        _attach_jvm_to_thread()
        self._lazy_load_jclass()
        return getattr(self._proxy, attr)

    def _lazy_load_jclass(self):
        if type(self._proxy) is str:
            self._proxy = JClass(self._proxy)

    def __call__(self, *args):
        self._lazy_load_jclass()
        if args:
            proxy = self._proxy(*args)
        else:
            proxy = self._proxy()
        return SafeJClass(proxy)


# API列表
CustomDictionary = LazyLoadingJClass('com.hankcs.hanlp.dictionary.CustomDictionary')
HanLP = SafeJClass('com.hankcs.hanlp.HanLP')
PerceptronLexicalAnalyzer = SafeJClass('com.hankcs.hanlp.model.perceptron.PerceptronLexicalAnalyzer')