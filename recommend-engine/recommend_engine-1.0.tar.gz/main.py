import argparse
import numpy as np
import matplotlib.pyplot as plt
import random

parser = argparse.ArgumentParser('movie recommend engine trained by MovieLens')
parser.add_argument('mode', type=str, choices=['recommend', 'evaluate'],
                    help='action mode of this script')
parser.add_argument('algorithm', type=str, choices=['sgd', 'als'],
                    help='algorithm to solve Matrix Factorization')
parser.add_argument('feature', type=int,
                    help='# of latent features of MF')
parser.add_argument('--epoch', '-e', type=int, default=100,
                    help='# of training epochs')
args = parser.parse_args()


class MFBase(object):
    def __init__(self, user, item, k, epoch, lam_u, lam_i):
        self.user = user
        self.item = item
        self.k = k
        self.epoch = epoch
        self.lam_u = lam_u
        self.lam_i = lam_i
        self.U = np.random.random((user, k))
        self.I = np.random.random((item, k))

    def evaluate(self, filename, threshold=4):
        Ns = [1,] + list(range(100, 20000, 100))  # Top N
        Ps = []  # Precision
        Rs = []  # Recall

        data = self.read_test_data(filename)

        TP = 0
        FP = 0
        AUC = 0
        true = len([d for d in data if d[2] >= threshold])  # 実際にレコメンドされる数(スコアがthreshold以上のmovie)
        for i in range(20000):
            if data[i][2] >= threshold:
                TP += 1
            if (i+1) in Ns:
                Ps.append(TP / (i+1))
                Rs.append(TP / true)
                if i != 0:
                    AUC += (Ps[-1] + Ps[-2]) * (Rs[-1] - Rs[-2]) / 2

        # plt.plot(Rs, Ps)
        # plt.xlabel('Recall')
        # plt.ylabel('Precision')
        # plt.xlim(0, 1)
        # plt.ylim(0, 1)
        # plt.show()
        # print('AUC = {}'.format(AUC))
        return AUC

    def predict(self, uid, num):
        pred = self.U[uid] @ self.I.T
        print('recommendation rank | movie ID | predicted rating (recommendation score)')
        for i, iid in enumerate(np.argsort(pred)[:-num:-1]):
            print('{:>19} | {:>8} | {:>39}'.format(i+1, iid+1, pred[iid]))

    def read_test_data(self, filename):
        data = []
        pred = self.U @ self.I.T
        with open(filename) as f:
            for line in f:
                uid, iid, rate, _ = map(int, line.split())
                data.append((uid-1, iid-1, rate, pred[uid-1, iid-1]))
        data.sort(key=lambda x: x[3], reverse=True)
        return data


class MF_SGD(MFBase):
    def __init__(self, user, item, k, epoch, lam_u=1e-1, lam_i=1e-1, alpha=1e-2):
        super(MF_SGD, self).__init__(user, item, k, epoch, lam_u, lam_i)
        self.alpha = alpha
    
    def fit(self, filename):
        data, R = self.read_training_data(filename)

        for i in range(self.epoch):
            random.shuffle(data)
            for uid, iid, rate in data:
                error = rate - self.U[uid] @ self.I[iid]
                delta_U = self.alpha * (error * self.I[iid] - self.lam_u * self.U[uid])
                delta_I = self.alpha * (error * self.U[uid] - self.lam_i * self.I[iid])
                self.U[uid] += delta_U
                self.I[iid] += delta_I

            E = R - self.U @ self.I.T
            rmse = np.sqrt(np.mean(E[R>0]**2))
            # print(i+1, rmse)

    def read_training_data(self, filename):
        data = []
        R = np.zeros((self.user, self.item), dtype=np.int8)
        with open(filename) as f:
            for line in f:
                uid, iid, rate, _ = map(int, line.split())
                data.append((uid-1, iid-1, rate))
                R[uid-1, iid-1] = rate
        return data, R


class MF_ALS(MFBase):
    def __init__(self, user, item, k, epoch, lam_u=1e+1, lam_i=1e+1):
        super(MF_ALS, self).__init__(user, item, k, epoch, lam_u, lam_i)

    def fit(self, filename):
        R, CU, CI = self.read_training_data(filename)
        lambdaU = self.lam_u * np.eye(self.k)
        lambdaI = self.lam_i * np.eye(self.k)

        for i in range(self.epoch):
            # optimize U, fixing I
            for uid in range(self.user):
                self.U[uid] = R[uid] @ self.I @ np.linalg.inv(self.I.T @ CU[uid] @ self.I + lambdaU)

            # optimize I, fixing U
            for iid in range(item):
                self.I[iid] = R[:, iid] @ self.U @ np.linalg.inv(self.U.T @ CI[iid] @ self.U + lambdaI)
            
            E = R - self.U @ self.I.T
            rmse = np.sqrt(np.mean(E[R>0]**2))
            # print(i+1, rmse)

    def read_training_data(self, filename):
        R = np.zeros((self.user, self.item), dtype=np.int8)
        CU = np.zeros((self.user, self.item, self.item), dtype=np.int8)
        CI = np.zeros((self.item, self.user, self.user), dtype=np.int8)
        with open(filename) as f:
            for line in f:
                uid, iid, rate, _ = map(int, line.split())
                R[uid-1, iid-1] = rate
                CU[uid-1, iid-1, iid-1] = 1
                CI[iid-1, uid-1, uid-1] = 1
        return R, CU, CI


if __name__ == '__main__':
    with open('ml-100k/u.info') as f:
        user = int(f.readline().split()[0])
        item = int(f.readline().split()[0])

    if args.mode == 'recommend':
        if args.algorithm == 'sgd':
            mf = MF_SGD(user, item, args.feature, args.epoch)
        elif args.algorithm == 'als':
            mf = MF_ALS(user, item, args.feature, args.epoch)
        mf.fit('ml-100k/u.data')

        while True:
            print('Who do you recommend to? (User ID: 1~{})'.format(user))
            uid = int(input()) - 1
            print('How many recommendations do you want?')
            num = int(input())
            if uid in list(range(user)):
                mf.predict(uid, num)
            else:
                print('Invalid value. Please retry.')

    elif args.mode == 'evaluate':
        sum = 0
        for i in range(5):
            if args.algorithm == 'sgd':
                mf = MF_SGD(user, item, args.feature, args.epoch)
            elif args.algorithm == 'als':
                mf = MF_ALS(user, item, args.feature, args.epoch)

            mf.fit('ml-100k/u{}.base'.format(i+1))
            AUC = mf.evaluate('ml-100k/u{}.test'.format(i+1))
            sum += AUC
        print('AUC average: {}'.format(sum / 5))
