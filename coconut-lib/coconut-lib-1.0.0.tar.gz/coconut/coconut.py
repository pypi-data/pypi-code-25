""" Coconut threshold credentials scheme """
from bplib.bp import BpGroup, G2Elem
from utils import *
from proofs import *


def setup(q=1):
	""" generate all public parameters """
	assert q > 0
	G = BpGroup()
	g1, g2 = G.gen1(), G.gen2()
	hs = [G.hashG1(("h%s" % i).encode("utf8")) for i in range(q)]
	e, o = G.pair, G.order()
	return (G, o, g1, hs, g2, e)


def ttp_keygen(params, t, n, q):
	""" generate keys for threshold signature (executed by a TTP) """
	(G, o, g1, hs, g2, e) = params
	# generate polynomials
	v = [o.random() for _ in range(0,t)]
	w = [[o.random() for _ in range(0,t)] for __ in range(q)]
	# generate shares
	x = [poly_eval(v,i) % o for i in range(1,n+1)]
	y = [[poly_eval(wj,i) % o for wj in w] for i in range(1,n+1)]
	# set keys
	sk = list(zip(x, y))
	vk = [(g2, x[i]*g2, [y[i][j]*g2 for j in range(len(y[i]))]) for i in range(len(sk))]
	aggr_vk = (g2, poly_eval(v,0)*g2, [poly_eval(wi,0)*g2 for wi in w])
	return (sk, vk, aggr_vk)


def prepare_blind_sign(params, clear_m, hidden_m, gamma):
	""" build elements for blind sign """
	(G, o, g1, hs, g2, e) = params
	attributes = hidden_m + clear_m
	assert len(attributes) <= len(hs)
	# build commitment
	r = o.random()
	cm = r*g1 + ec_sum([attributes[i]*hs[i] for i in range(len(attributes))])
	# build El Gamal encryption
	h = G.hashG1(cm.export()) 
	enc = [elgamal_enc(params, gamma, m, h) for m in hidden_m]
	(a, b, k) = zip(*enc)
	c = list(zip(a, b))
	# build proofs
	pi_s = make_pi_s(params, gamma, c, cm, k, r, clear_m, hidden_m)
	return (cm, c, pi_s)


def blind_sign(params, sk, cm, c, gamma, pi_s, clear_m):
	""" blindly sign messages in c, and sign messages in m """
	(G, o, g1, hs, g2, e) = params
	(x, y) = sk
	(a, b) = zip(*c) 
	assert (len(c)+len(clear_m)) <= len(hs)
	# verify proof of correctness
	assert verify_pi_s(params, gamma, c, cm, pi_s)
	# issue signature
	h = G.hashG1(cm.export())
	t1 = [mi*h for mi in clear_m]
	t2 = ec_sum([yi*ai for yi,ai in zip(y,a)])
	t3 = x*h + ec_sum([yi*bi for yi,bi in zip(y,list(b)+t1)])
	sigma_tilde = (h, (t2, t3))
	return sigma_tilde


def unblind(params, sigma_tilde, d):
	""" unblind the credential sigma_tilde """
	(h, c_tilde) = sigma_tilde
	sigma = (h, elgamal_dec(params, d, c_tilde))
	return sigma


def aggregate_cred(params, sigs):
	""" aggregate threshold signatures """
	(G, o, g1, hs, g2, e) = params
	t = len(sigs)
	# evaluate all lagrange basis polynomial li(0)
	l = [lagrange_basis(t, o, i, 0) for i in range(1,t+1)]
	# aggregate sigature
	(h, s) = zip(*sigs)
	aggr_s = ec_sum([l[i]*s[i] for i in range(t)])
	return (h[0], aggr_s)


def randomize(params, sig):
	""" randomize signature (after aggregation) """
	(G, o, g1, hs, g2, e) = params
	(h , s) = sig
	r = o.random()
	return ( r*h , r*s )


def show_blind_sign(params, aggr_vk, sigma, hidden_m):
	""" build elements for mix verify """
	(G, o, g1, hs, g2, e) = params
	(g2, alpha, beta) = aggr_vk
	(h, s) = sigma
	assert len(hidden_m) <= len(beta)
	t = o.random()
	kappa = t*g2 + alpha + ec_sum([hidden_m[i]*beta[i] for i in range(len(hidden_m))])
	nu = t*h
	pi_v = make_pi_v(params, aggr_vk, sigma, hidden_m, t)
	return (kappa, nu, pi_v)


def blind_verify(params, aggr_vk, sigma, kappa, nu, pi_v, clear_m):
	""" verify a signature on a mixed clear and hidden message """
	(G, o, g1, h1, g2, e) = params
	(g2, _, beta) = aggr_vk
	(h, s) = sigma
	hidden_m_len = len(pi_v[1])
	assert len(clear_m)+hidden_m_len <= len(beta)
	# verify proof of correctness
	assert verify_pi_v(params, aggr_vk, sigma, kappa, nu, pi_v)
	# add clear text messages
	aggr = G2Elem.inf(G) 
	if len(clear_m) != 0:
		aggr = ec_sum([clear_m[i]*beta[i+hidden_m_len] for i in range(len(clear_m))])
	# verify
	return not h.isinf() and e(h, kappa+aggr) == e(s+nu, g2)


