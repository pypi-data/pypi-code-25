

from __future__ import division
from __future__ import absolute_import
import numpy as np
from rllab2.misc import special
from rllab2.misc import tensor_utils
from rllab2.algos import util
import rllab2.misc.logger as logger


class Sampler(object):
    def start_worker(self):
        u"""
        Initialize the sampler, e.g. launching parallel workers if necessary.
        """
        raise NotImplementedError

    def obtain_samples(self, itr):
        u"""
        Collect samples for the given iteration number.
        :param itr: Iteration number.
        :return: A list of paths.
        """
        raise NotImplementedError

    def process_samples(self, itr, paths):
        u"""
        Return processed sample data (typically a dictionary of concatenated tensors) based on the collected paths.
        :param itr: Iteration number.
        :param paths: A list of collected paths.
        :return: Processed sample data.
        """
        raise NotImplementedError

    def shutdown_worker(self):
        u"""
        Terminate workers if necessary.
        """
        raise NotImplementedError


class BaseSampler(Sampler):
    def __init__(self, algo):
        u"""
        :type algo: BatchPolopt
        """
        self.algo = algo

    def process_samples(self, itr, paths):
        baselines = []
        returns = []

        if hasattr(self.algo.baseline, u"predict_n"):
            all_path_baselines = self.algo.baseline.predict_n(paths)
        else:
            all_path_baselines = [self.algo.baseline.predict(path) for path in paths]

        for idx, path in enumerate(paths):
            path_baselines = np.append(all_path_baselines[idx], 0)
            deltas = path[u"rewards"] + \
                     self.algo.discount * path_baselines[1:] - \
                     path_baselines[:-1]
            path[u"advantages"] = special.discount_cumsum(
                deltas, self.algo.discount * self.algo.gae_lambda)
            path[u"returns"] = special.discount_cumsum(path[u"rewards"], self.algo.discount)
            baselines.append(path_baselines[:-1])
            returns.append(path[u"returns"])

        ev = special.explained_variance_1d(
            np.concatenate(baselines),
            np.concatenate(returns)
        )

        if not self.algo.policy.recurrent:
            observations = tensor_utils.concat_tensor_list([path[u"observations"] for path in paths])
            actions = tensor_utils.concat_tensor_list([path[u"actions"] for path in paths])
            rewards = tensor_utils.concat_tensor_list([path[u"rewards"] for path in paths])
            returns = tensor_utils.concat_tensor_list([path[u"returns"] for path in paths])
            advantages = tensor_utils.concat_tensor_list([path[u"advantages"] for path in paths])
            env_infos = tensor_utils.concat_tensor_dict_list([path[u"env_infos"] for path in paths])
            agent_infos = tensor_utils.concat_tensor_dict_list([path[u"agent_infos"] for path in paths])

            if self.algo.center_adv:
                advantages = util.center_advantages(advantages)

            if self.algo.positive_adv:
                advantages = util.shift_advantages_to_positive(advantages)

            average_discounted_return = \
                np.mean([path[u"returns"][0] for path in paths])

            undiscounted_returns = [sum(path[u"rewards"]) for path in paths]

            ent = np.mean(self.algo.policy.distribution.entropy(agent_infos))

            samples_data = dict(
                observations=observations,
                actions=actions,
                rewards=rewards,
                returns=returns,
                advantages=advantages,
                env_infos=env_infos,
                agent_infos=agent_infos,
                paths=paths,
            )
        else:
            max_path_length = max([len(path[u"advantages"]) for path in paths])

            # make all paths the same length (pad extra advantages with 0)
            obs = [path[u"observations"] for path in paths]
            obs = tensor_utils.pad_tensor_n(obs, max_path_length)

            if self.algo.center_adv:
                raw_adv = np.concatenate([path[u"advantages"] for path in paths])
                adv_mean = np.mean(raw_adv)
                adv_std = np.std(raw_adv) + 1e-8
                adv = [(path[u"advantages"] - adv_mean) / adv_std for path in paths]
            else:
                adv = [path[u"advantages"] for path in paths]

            adv = np.asarray([tensor_utils.pad_tensor(a, max_path_length) for a in adv])

            actions = [path[u"actions"] for path in paths]
            actions = tensor_utils.pad_tensor_n(actions, max_path_length)

            rewards = [path[u"rewards"] for path in paths]
            rewards = tensor_utils.pad_tensor_n(rewards, max_path_length)

            returns = [path[u"returns"] for path in paths]
            returns = tensor_utils.pad_tensor_n(returns, max_path_length)

            agent_infos = [path[u"agent_infos"] for path in paths]
            agent_infos = tensor_utils.stack_tensor_dict_list(
                [tensor_utils.pad_tensor_dict(p, max_path_length) for p in agent_infos]
            )

            env_infos = [path[u"env_infos"] for path in paths]
            env_infos = tensor_utils.stack_tensor_dict_list(
                [tensor_utils.pad_tensor_dict(p, max_path_length) for p in env_infos]
            )

            valids = [np.ones_like(path[u"returns"]) for path in paths]
            valids = tensor_utils.pad_tensor_n(valids, max_path_length)

            average_discounted_return = \
                np.mean([path[u"returns"][0] for path in paths])

            undiscounted_returns = [sum(path[u"rewards"]) for path in paths]

            ent = np.sum(self.algo.policy.distribution.entropy(agent_infos) * valids) / np.sum(valids)

            samples_data = dict(
                observations=obs,
                actions=actions,
                advantages=adv,
                rewards=rewards,
                returns=returns,
                valids=valids,
                agent_infos=agent_infos,
                env_infos=env_infos,
                paths=paths,
            )

        logger.log(u"fitting baseline...")
        if hasattr(self.algo.baseline, u'fit_with_samples'):
            self.algo.baseline.fit_with_samples(paths, samples_data)
        else:
            self.algo.baseline.fit(paths)
        logger.log(u"fitted")

        logger.record_tabular(u'Iteration', itr)
        logger.record_tabular(u'AverageDiscountedReturn',
                              average_discounted_return)
        logger.record_tabular(u'AverageReturn', np.mean(undiscounted_returns))
        logger.record_tabular(u'ExplainedVariance', ev)
        logger.record_tabular(u'NumTrajs', len(paths))
        logger.record_tabular(u'Entropy', ent)
        logger.record_tabular(u'Perplexity', np.exp(ent))
        logger.record_tabular(u'StdReturn', np.std(undiscounted_returns))
        logger.record_tabular(u'MaxReturn', np.max(undiscounted_returns))
        logger.record_tabular(u'MinReturn', np.min(undiscounted_returns))

        return samples_data
