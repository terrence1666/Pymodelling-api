import flopy.modflow as mf


class GhbAdapter:
    _data = None

    def __init__(self, data):
        self._data = data

    def validate(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return some hints
        pass

    def is_valid(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return true or false
        return True

    def merge(self):
        default = self.default()
        for key in self._data:
            if key.startswith('_'):
                continue
            if key == 'stress_period_data':
                default[key] = self.to_dict(self._data[key])
                continue

            default[key] = self._data[key]
        return default

    def to_dict(self, data):
        if type(data) == list:
            spd_dict = {}
            for stress_period, record in enumerate(data):
                spd_dict[stress_period] = record
            return spd_dict
        return data

    def get_package(self, _mf):
        content = self.merge()
        return mf.ModflowGhb(
            _mf,
            ipakcb=content['ipakcb'],
            stress_period_data=content['stress_period_data'],
            dtype=content['dtype'],
            no_print=content['no_print'],
            options=content['options'],
            extension=content['extension'],
            unitnumber=content['unitnumber']
        )

    @staticmethod
    def default():
        default = {
            "ipakcb": 0,
            "stress_period_data": None,
            "dtype": None,
            "no_print": False,
            "options": None,
            "extension": 'ghb',
            "unitnumber": 23
        }

        return default

    @staticmethod
    def read_package(package):
        content = {
            "ipakcb": package.ipakcb,
            "stress_period_data": package.stress_period_data,
            "dtype": package.dtype,
            "no_print": package.no_print,
            "options": package.options,
            "extension": package.extension,
            "unitnumber": package.unitnumber
        }
        return content
