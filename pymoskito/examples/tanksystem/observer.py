# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import numpy as np

import pymoskito as pm
from . import settings as st


class CppHighGainObserver(pm.CppBase, pm.Observer):
    """
    High Gain Observer implemented in cpp with pybind11
    """
    public_settings = OrderedDict([
        ("initial state", st.initialStates),
        ("poles", st.polesObs),
        ("AT", st.AT),
        ("hT", st.hT),
        ("AS1", st.AS1),
        ("AS2", st.AS2),
        ("g", st.g),
        ("K", st.K),
        ("dt [s]", 0.1),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        settings.update(output_dim=2)

        m_path = os.path.dirname(__file__)
        if 'tanksystem' not in m_path:
            m_path += '/pymoskito/examples/tanksystem/src/'
        else:
            m_path += '/src/'

        pm.Observer.__init__(self, settings)
        pm.CppBase.__init__(self,
                            module_path=m_path,
                            module_name='Observer',
                            binding_class_name="binding_Observer")

        self.obs = self.get_class_from_module().HighGainObserver(self._settings["AT"],
                                                                 self._settings["AS1"],
                                                                 self._settings["AS2"],
                                                                 self._settings["K"],
                                                                 self._settings['dt [s]'])
        self.obs.setInitialState(np.array(self._settings["initial state"]))
        self.obs.setGain(np.array(self._settings["poles"]))

    def _observe(self, time, system_input, system_output):
        if system_input is None:
            return np.array(self._settings["initial state"])

        y = system_output[1]
        uA = system_input[0]
        res = self.obs.compute(y, uA)

        return np.array(res)


pm.register_simulation_module(pm.Observer, CppHighGainObserver)
