import os
import flopy.utils.binaryfile as bf


class ReadConcentration:
    _filename = None

    def __init__(self, workspace):
        for file in os.listdir(workspace):
            if file.upper() == "MT3D001.UCN":
                self._filename = os.path.join(workspace, file)
        pass

    def read_times(self):
        try:
            ucn_obj = bf.UcnFile(filename=self._filename, precision='single')
            return ucn_obj.get_times()
        except:
            return []

    def read_number_of_layers(self):
        try:
            ucn_obj = bf.UcnFile(filename=self._filename, precision='single')
            number_of_layers = ucn_obj.get_data().shape[0]
            return number_of_layers
        except:
            return 0

    def read_layer(self, totim, layer):
        try:
            ucn_obj = bf.UcnFile(filename=self._filename, precision='single')
            data = ucn_obj.get_data(totim=totim, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] < -999:
                        data[i][j] = None
            return data
        except:
            return []

    def read_ts(self, layer, row, column):
        try:
            ucn_obj = bf.UcnFile(filename=self._filename, precision='single')
            return ucn_obj.get_ts(idx=(layer, row, column)).tolist()
        except:
            return []
