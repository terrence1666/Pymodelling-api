import json
import numpy as np
import os
from scipy import stats
from sklearn.metrics import r2_score


class HobStatistics:

    def __init__(self, model_ws, name):
        self._model_ws = model_ws
        self._name = name
        self._input_file = os.path.join(model_ws, name) + '.hob.out'
        self._output_file = os.path.join(model_ws, name) + '.hob.stat'

    def write_to_file(self):
        with open(self._output_file, 'w') as outfile:
            json.dump(self.calculate(), outfile)

    @staticmethod
    def calculate_npf(x, n):
        a = 0.5
        if x < 11:
            a = 3 / 8

        return stats.norm.ppf((x - a) / (n + 1 - 2 * a))

    def calculate(self):
        if not os.path.isfile(self._input_file):
            return {"error": 'File ' + self._input_file + ' not found.'}

        f = open(self._input_file)

        header = False

        names = []
        observed = []
        simulated = []

        for line in f:
            if line.startswith('#'):
                continue

            if not header:
                header = line.split('"')[1::2]
                continue

            values = line.split()
            simulated.append(float(values[0]))
            observed.append(float(values[1]))
            names.append('_'.join(values[2].split('_')[:-1]))

        simulated = np.array(simulated)
        observed = np.array(observed)

        # Write to statistics object
        statistics = dict(
            observed=list(observed),
            simulated=list(simulated),
            n=len(observed),
            rMax=np.max(np.abs(simulated - observed)),
            rMin=np.min(np.abs(simulated - observed)),
            rMean=np.mean(simulated - observed),
            absRMean=np.mean(np.abs(simulated-observed)),
            sse=stats.sem(simulated - observed),
            rmse=np.sqrt(((simulated - observed) ** 2).mean()),
            R=stats.pearsonr(observed, simulated)[0],
            R2=r2_score(observed, simulated)
        )

        statistics["nrmse"] = statistics["rmse"] / (np.max(observed) - np.min(observed))

        # Plot simulated vs. observed values
        statistics["Z"] = 1.96
        statistics["stdObserved"] = np.std(observed)
        statistics["deltaStd"] = statistics["Z"] * statistics["stdObserved"] / np.sqrt(statistics["n"])

        # Plot (weighted) residuals vs. simulated heads
        statistics["weightedResiduals"] = list(simulated - observed)
        statistics["linRegressSW"] = stats.linregress(simulated, statistics["weightedResiduals"])

        # Check for Normal Distribution¶
        statistics["rankedResiduals"] = list(np.sort(simulated - observed))

        n = statistics["n"]
        npf = np.linspace(1, n, num=n)
        npf = list(map(lambda x, n: self.calculate_npf(x, n), npf, np.ones(n) * n))

        statistics["npf"] = npf
        statistics["linRegressRN"] = stats.linregress(statistics["rankedResiduals"], statistics["npf"])

        return statistics
