import warnings
from data_table import score_table
from constants import MAX_GRE, MIN_GRE, BAD_INPUT_RETURN, MIN_GMAT, MAX_GMAT


def _validate_score_input(v,q):
	try:
		verbal = int(v)
	except:
		warnings.warn("Was not able to parse verbal score: {}\nReturning {}".format(v,BAD_INPUT_RETURN))
		return BAD_INPUT_RETURN,BAD_INPUT_RETURN
	try:
		quant = int(q)
	except:
		warnings.warn("Was not able to parse quant score: {}\nReturning {}".format(q,BAD_INPUT_RETURN))
		return BAD_INPUT_RETURN, BAD_INPUT_RETURN

	if verbal > MAX_GRE or verbal < MIN_GRE:
		warnings.warn("Verbal score: {} is not between {} and {}\nReturning {}".format(verbal,MIN_GRE,MAX_GRE,BAD_INPUT_RETURN))
		return BAD_INPUT_RETURN, BAD_INPUT_RETURN

	if quant > MAX_GRE or quant < MIN_GRE:
		warnings.warn("Quant score: {} is not between {} and {}\nReturning {}".format(quant,MIN_GRE,MAX_GRE,BAD_INPUT_RETURN))
		return BAD_INPUT_RETURN, BAD_INPUT_RETURN

	return verbal, quant

def gre2gmat(gre_verbal,gre_quant):
	"""
	:param gre_verbal: Numeric representation of verbal GRE score
	:type verbal: int

	:param gre_quant: Numeric representation of quantitative GRE score
	:type quant: int

	:return: Predicted GMAT score
	:rtype: int
	"""
	v,q = _validate_score_input(gre_verbal,gre_quant)
	if v == BAD_INPUT_RETURN or q == BAD_INPUT_RETURN:
		gmat = BAD_INPUT_RETURN
	else:
		try:
			gmat = score_table.loc[q,v]
		except KeyError:
			gmat = rough_gre2gmat(gre_verbal=v,gre_quant=q)

	return gmat


def rough_gre2gmat(gre_verbal,gre_quant):
	"""
	An equation for computing GMAT equivalent taken from:
	https://www.mbacrystalball.com/blog/2014/01/23/gre-to-gmat-score-conversion/

	:param gre_verbal: Numeric representation of verbal GRE score
	:type verbal: int

	:param gre_quant: Numeric representation of quantitative GRE score
	:type quant: int

	:return: Predicted GMAT score
	:rtype: int
	"""

	v,q = _validate_score_input(gre_verbal,gre_quant)
	if v == BAD_INPUT_RETURN or q == BAD_INPUT_RETURN:
		gmat = BAD_INPUT_RETURN
	else:
		gmat = -2080.75 + (6.38 * v) + (10.62 * q)
		if gmat >= MAX_GMAT:
			gmat = MAX_GMAT
		elif gmat <= MIN_GMAT:
			gmat = MIN_GMAT

	return int(gmat - gmat%10)
def rougher_gre2gmat(gre_verbal,gre_quant):
	"""
	A terrible approximation for gmat score. Derived with love by yours truly
	:param gre_verbal: Numeric representation of verbal GRE score
	:type verbal: int

	:param gre_quant: Numeric representation of quantitative GRE score
	:type quant: int

	:return: Predicted GMAT score
	:rtype: int
	"""
	warnings.warn("\nThis function is inappropriately inaccurate.")
	v,q = _validate_score_input(gre_verbal,gre_quant)
	if v == BAD_INPUT_RETURN or q == BAD_INPUT_RETURN:
		gmat = BAD_INPUT_RETURN
	else:
		gmat = (v+q)*2.019

		if gmat >= MAX_GMAT:
			gmat = MAX_GMAT
		elif gmat <= MIN_GMAT:
			gmat = MIN_GMAT

	return int(gmat - gmat%10)





