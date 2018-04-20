import unittest

from canonical_args import structure



class TestObj(object):
	pass

class TestCase_CheckArgs(unittest.TestCase):

	def test_check_args(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": int,
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": float,
					"values": None
				}
			}
		}

		structure.checkspec(spec, [1], {"kwarg1": 33.1})

	def test_check_args_fail(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": int,
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": float,
					"values": None
				}
			}
		}

		try:
			structure.checkspec(spec, [1], {"kwarg1": "string"})  # bad type
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_check_args_with_eval(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": "int",
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": "one([int, NoneType])",
					"values": {
						"int": ">0",
						"NoneType": None
					},
					"required": True
				}
			}
		}

		structure.checkspec(spec, [1], {"kwarg1": None})


	def test_check_complex_args(self):
		from canonical_args.check import one, cls, NoneType, TypeType
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": "one([int, float, str])",
					"values": {
						"int": ">0&&!=5",
						"float": "<5.3||>7.8",
						"str": ["A", "B", "C", "X"]
					}
				},
				{
					"name": "arg2",
					"type": dict,
					"values": {
						"subkey1": {
							"type": cls('test_structure.TestObj'),
							"values": None,
							"required": True
						},
						"subkey2": {
							"type": TypeType,
							"values": [int, float],
							"required": False
						}
					}
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": one([int, float, dict, NoneType]),
					"values": {
						"int": "!=100",
						"float": "range(0, 99)",
						"dict": {
							"subkey1": {
								"type": int,
								"values": ">=0&&!=10",
								"required": True
							},
							"subkey2": {
								"type": float,
								"values": None,
								"required": True
							}
						},
						"NoneType": None
					}
				},
				"kwarg2": {
					"type": one([int, NoneType]),
					"values": {
						"int": "(>10||<10)&&!=5",
						"NoneType": None
					}
				}
			}
		}

		structure.checkspec(
			argspec,
			[0.113, {"subkey1": TestObj(), "subkey2": int}],
			{
				"kwarg1": {
					"subkey1": 5,
					"subkey2": 459.132
				},
				"kwarg2": None
			})

class TestCase_NestedOnes(unittest.TestCase):

	def test_nested_choice_of_one(self):
		argspec = {
			"args": [
				{
					"name": 'arg1',
					"type": "one([int, dict])",
					"values": {
						"int": None,
						"dict": {
							"subkey1": {
								"type": "one([str, int])",
								"values": {
									"str": None,
									"int": None
								}
							}
						}
					}
				}
			]
		}

		structure.checkspec(
			argspec,
			[{"subkey1": 1}])
		structure.checkspec(argspec, [1])
		structure.checkspec(argspec, [{"subkey1": "xyz"}])

	def test_nested_list_choice_of_one(self):
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": "one([int, float, list([int, int])])",
					"values": {
						"int": None,
						"float": None,
						"list": [None, None]
					}
				}
			]
		}

		structure.checkspec(argspec, [[1, 1]])

class TestCase_BadLength(unittest.TestCase):

	def test_args_too_short(self):
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": str,
					"values": None
				},
				{
					"name": "arg2",
					"type": str,
					"values": None
				}
			]
		}

		try:
			structure.checkspec(argspec, ["A"])
		except TypeError:
			pass
		else:
			self.fail("should have thrown TypeError, too short")

	def test_args_too_many(self):
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": str,
					"values": None
				}
			]
		}

		try:
			structure.checkspec(argspec, ["A", "B"])
		except TypeError:
			pass
		else:
			self.fail("should have thrown TypeError, too many")

	def test_kwargs_extra_arg(self):
		argspec = {
			"args": [],
			"kwargs": {
				"kwarg1": {
					"type": int,
					"values": None
				}
			}
		}

		try:
			structure.checkspec(argspec, [], {"badkwarg": 15})
		except TypeError:
			pass
		else:
			self.fail("should have thrown TypeError, unrecognized kwarg")

	def test_missing_dict_subkey(self):
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": dict,
					"values": {
						"subkey1": {
							"type": int,
							"values": None,
							"required": True  # explicitly required
						},
						"subkey2": {
							"type": int,
							"values": None    # implicitly required
						},
						"subkey3": {
							"type": int,
							"values": None,
							"required": False  # not required
						}
					}
				}
			],
			"kwargs": {}
		}

		try:
			structure.checkspec(argspec, [{"subkey1": 15}])  #missing subkey2
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError, missing subkey2")

	def test_missing_optional_subkey(self):
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": dict,
					"values": {
						"subkey1": {
							"type": int,
							"values": None,
							"required": True  # explicitly required
						},
						"subkey2": {
							"type": int,
							"values": None    # implicitly required
						},
						"subkey3": {
							"type": int,
							"values": None,
							"required": False  # not required
						}
					}
				}
			],
			"kwargs": {}
		}

		structure.checkspec(argspec, [{"subkey1": 15, "subkey2": 15}])