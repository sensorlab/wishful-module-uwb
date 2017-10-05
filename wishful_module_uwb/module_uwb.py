import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions

import serial
from vesna import alh
from vesna.alh.uwbnode import UWBNode, RadioSettings

__author__ = "Matevz Vucnik"
__copyright__ = "Copyright (c) 2017, Jozef Stefan Instiute"
__version__ = "0.1.0"
__email__ = "matevz.vucnik@ijs.si"


@wishful_module.build_module
class UwbModule(wishful_module.AgentModule):
    settings = None
    uwbnode = None

    def __init__(self, dev):
        super(UwbModule, self).__init__()
        self.log = logging.getLogger('UwbModule')
        ser = serial.Serial(dev, 921600)
        node = alh.ALHTerminal(ser)
        self.uwbnode = UWBNode(node)
        self.settings = RadioSettings()

    @wishful_module.bind_function(upis.radio.get_radio_info)
    def get_radio_info(self, platform_id):
        self.settings = self.uwbnode.get_radio_settings()
        return self.settings.get_dict()

    @wishful_module.bind_function(upis.radio.set_parameters)
    def set_parameters(self, params):
        self.settings.channel = params['ch']
        self.settings.channel_code = params['ch_code']
        self.settings.prf = params['prf']
        self.settings.datarate = params['dr']
        self.settings.preamble_length = params['plen']
        self.settings.pac_size = params['pac']
        self.settings.nssfd = params['nssfd']
        self.settings.sfd_timeout = params['sfdto']
        
        self.uwbnode.setup_radio(self.settings)
        return {'ch_code': 0, 'pac': 0, 'nssfd': 0, 'prf': 0, 'ch': 0, 'plen': 0, 'sfdto': 0, 'dr': 0}

    @wishful_module.bind_function(upis.radio.get_measurements)
    def get_measurements(self, params):
        for i in range(100):
            if(self.uwbnode.check_pending_measurement()):
                res = self.uwbnode.get_last_range_data()
                measurements = {"Range": res['range'],
                "NodeID": self.uwbnode.get_sensor_id(),
                "DestID": res['dest_id'],
                "RSS": res['rss'],
                "RSS_FP": res['rss_fp'],
                "Noise_STDEV": res['noise_stdev'],
                "Max_noise": res['max_noise'],
                "RXPACC": res['rxpacc'],
                "FP_index": res['fp_index'],
                "Raw": res['cir']}
                
                return measurements
