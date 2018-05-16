# -*- coding: utf-8 -*-
""" 模組載入支援函式 / Module load routines """

import sys
import imp
from pkgutil import iter_modules
from itertools import chain as iter_chain


def get_module_file_suffixes():
	# type: () -> frozenset
	"""
	取得模組檔案的延伸檔名

	Get the file name extension of modules

	Return:
		存有模組檔案延伸檔名的集合物件 / Set object keeps file name extension of modules
	"""
	return frozenset(map(lambda x: x[0], imp.get_suffixes()))


def get_module(module_ident):
	# type: (str) -> Any
	"""
	取得給定的模組識別字串所指向的模組或套件物件

	Get the module object (or package object) identify by given module identifier

	Args:
		module_ident: 模組識別字串 / Module identifier (ex: "commonutil.moduleimp")
	Return:
		所載入的模組物件 / Loaded module object
	"""
	try:
		return sys.modules[module_ident]
	except KeyError:
		pass
	aux = module_ident.split(".")
	mod_name = aux[-1]
	if len(aux) == 1:
		fp, pathname, description, = imp.find_module(mod_name)
	else:
		pkg_ident = ".".join(aux[:-1])
		pkg_instance = get_module(pkg_ident)
		if not hasattr(pkg_instance, "__path__"):
			raise ValueError("package identifier is not a normal package: %r" % (pkg_ident, ))
		fp, pathname, description, = imp.find_module(mod_name, pkg_instance.__path__)
	try:
		return imp.load_module(mod_name, fp, pathname, description)
	finally:
		if fp:
			fp.close()


def iter_modules_in_package(package_ident, exclude_names=None):
	# type: (str, str) -> iter[Any]
	"""
	取得指定套件 (package) 中的模組物件，這個函式只會取出指定套件中的第一層子模組，並不會遞迴列出所有深度的模組。

	Get immediate module objects in given package. (will not yield recursively)

	Args:
		package_ident: 套件識別字串或是套件物件 / Package identifier string or package object
		exclude_names=None: 要排除的模組名稱 / Names to exclude

	Yield:
		產出 (mod_name, mod_instance,) 型式的 tuple 物件，成員分別表示模組名稱與模組物件

		Generates tuple object in (mod_name, mod_instance,) form. Represents module name and module object respectively.
	"""
	if isinstance(package_ident, basestring):
		pkg_instance = get_module(package_ident)
		if not hasattr(pkg_instance, "__path__"):
			raise ValueError("given package identifier is not ordinary package folder: %r" % (package_ident, ))
	elif hasattr(package_ident, "__path__"):
		pkg_instance = package_ident
		package_ident = package_ident.__name__
	else:
		raise ValueError("require package identifier or package object: package_ident=%r" % (package_ident, ))
	pkg_path = pkg_instance.__path__
	exclude_names = frozenset(iter_chain(exclude_names if exclude_names else (), ("__init__", )))
	found_mod_names = set()
	for _module_loader, mod_name, _ispkg, in iter_modules(pkg_path):
		if mod_name not in exclude_names:
			found_mod_names.add(mod_name)
	for mod_name in found_mod_names:
		try:
			yield (
					mod_name,
					sys.modules[package_ident + "." + mod_name],
			)
		except KeyError:
			pass
		fp, pathname, description, = imp.find_module(mod_name, pkg_path)
		try:
			yield (
					mod_name,
					imp.load_module(mod_name, fp, pathname, description),
			)
		finally:
			if fp:
				fp.close()


# vim: ts=4 sw=4 ai nowrap
