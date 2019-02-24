import flopy.modflow as mf


class HobAdapter:
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
            if not key.startswith('_'):
                default[key] = self._data[key]
        return default

    def get_package(self, _mf):
        content = self.merge()
        # noinspection PyTypeChecker
        content["obs_data"] = self.map_obs_data(_mf, content["obs_data"])
        return mf.ModflowHob(
            _mf,
            **content
        )

    @staticmethod
    def map_obs_data(model, observations):
        obs = []

        for o in observations:
            print(o)
            obs.append(mf.HeadObservation(
                model,
                layer=o['layer'],
                row=o['row'],
                column=o['column'],
                time_series_data=o['time_series_data']
            ))

        return obs

    @staticmethod
    def default():
        default = {
            "iuhobsv": None,
            "hobdry": 0,
            "tomulth": 1.0,
            "obs_data": None,
            "hobname": None,
            "extension": 'hob',
            "unitnumber": None,
            "filenames": None
        }
        return default

    @staticmethod
    def read_package(package):
        content = {
            "iuhobsv": package.iuhobsv,
            "hobdry": package.hobdry,
            "tomulth": package.tomulth,
            "obs_data": package.obs_data,
            "hobname": package.hobname,
            "extension": package.extension[0],
            "unitnumber": package.unit_number[0],
            "filenames": package.filenames
        }
        return content
