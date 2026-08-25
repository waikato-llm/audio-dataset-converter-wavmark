import argparse
import logging

import numpy as np
import torch
import wavmark
from kasperl.api import safe_deepcopy
from wai.logging import LOGGING_WARNING

from adc.api import Watermarker, WatermarkDetector


class WavMarkMarker(Watermarker):
    """
    Applies the WavMark watermarking.
    """

    def __init__(self, payload: int = None, device: str = None, min_snr: int = None, max_snr: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param payload: the 16-bit payload to embed
        :type payload: int
        :param device: the device to use for the model (eg: cpu, cuda:0)
        :type device: str
        :param min_snr: the minimum signal-to-noise ratio
        :type min_snr: int
        :param max_snr: the maximum signal-to-noise ratio
        :type max_snr: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.payload = payload
        self.device = device
        self.min_snr = min_snr
        self.max_snr = max_snr
        self._payload = None
        self._device = None
        self._model = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "wm-wavmark"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Applies the WavMark watermarking: https://github.com/wavmark/wavmark"

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-p", "--payload", type=int, help="The 16-bit payload to embed (0 <= x < 65536).", default=42, required=True)
        parser.add_argument("-d", "--device", type=str, help="The torch device to run the model on, e.g., 'cpu' or 'cuda:0'.", default="cpu", required=False)
        parser.add_argument("-m", "--min_snr", type=int, help="The minimum signal-to-noise ratio.", default=20, required=False)
        parser.add_argument("-M", "--max_snr", type=int, help="The maximum signal-to-noise ratio.", default=38, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.payload = ns.payload
        self.device = ns.device
        self.min_snr = ns.min_snr
        self.max_snr = ns.max_snr

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.payload is None:
            raise Exception("No payload specified!")
        if self.payload < 0:
            raise Exception("No negative numbers!")
        if self.payload >= 2**16:
            raise Exception("Number must be < %d!" % 2**16)
        self._payload = np.array([int(i) for i in bin(self.payload)[2:].zfill(16)])
        self.logger().info("Payload bits: %s" % str(self._payload))

        if self.device is None:
            self.device = "cpu"
        self.logger().info("Initializing device: %s" % self.device)
        self._device = torch.device(self.device)
        self.logger().info("Loading model...")
        self._model = wavmark.load_model().to(self._device)

        if self.min_snr is None:
            self.min_snr = 20
        if self.max_snr is None:
            self.max_snr = 38
        if self.min_snr >= self.max_snr:
            raise Exception("min_snr must be less than max_snr, but: min_snr=%d and max_snr=%d" % (self.min_snr, self.max_snr))

    def _do_watermark(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        signal = data.audio
        watermarked_signal, info = wavmark.encode_watermark(self._model, signal, self._payload,
                                                            min_snr=self.min_snr, max_snr=self.max_snr,
                                                            show_progress=self.logger().isEnabledFor(logging.INFO))
        if self.logger().isEnabledFor(logging.DEBUG):
            self.logger().debug("Watermark info: %s" % str(info))
        data_new = type(data)(audio_name=data.audio_name, audio=watermarked_signal, sample_rate=data.sample_rate,
                              audio_format=data.audio_format, metadata=safe_deepcopy(data.get_metadata()))
        if not data_new.has_metadata():
            data_new.set_metadata(dict())
        data_new.get_metadata()["wavmark-info"] = info
        return data_new


class WavMarkDetector(WatermarkDetector):
    """
    For detecting WavMark watermarks.
    """

    def __init__(self, device: str = None, payload: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param payload: the 16-bit payload to embed
        :type payload: int
        :param device: the device to use for the model (eg: cpu, cuda:0)
        :type device: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.payload = payload
        self.device = device
        self._payload = None
        self._device = None
        self._model = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "wmd-wavmark"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "For detecting WavMark watermarks: https://github.com/wavmark/wavmark\nStores the 'wavmark-BER' field in the metadata when supplying a payload to match against, with 0=perfect match and 100=no match all."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-p", "--payload", type=int, help="The 16-bit payload to check against (0 <= x < 65536).", default=42, required=False)
        parser.add_argument("-d", "--device", type=str, help="The torch device to run the model on, e.g., 'cpu' or 'cuda:0'.", default="cpu", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.payload = ns.payload
        self.device = ns.device

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.payload is not None:
            if self.payload < 0:
                raise Exception("No negative numbers!")
            if self.payload >= 2**16:
                raise Exception("Number must be < %d!" % 2**16)
            self._payload = np.array([int(i) for i in bin(self.payload)[2:].zfill(16)])
            self.logger().info("Payload bits: %s" % str(self._payload))

        if self.device is None:
            self.device = "cpu"
        self.logger().info("Initializing device: %s" % self.device)
        self._device = torch.device(self.device)
        self.logger().info("Loading model...")
        self._model = wavmark.load_model().to(self._device)

    def _do_detect(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        watermarked_signal = data.audio
        payload_decoded, info = wavmark.decode_watermark(self._model, watermarked_signal, show_progress=self.logger().isEnabledFor(logging.INFO))
        data_new = data.duplicate()
        if not data_new.has_metadata():
            data_new.set_metadata(dict())
        data_new.get_metadata()["wavmark-info"] = info
        if self.logger().isEnabledFor(logging.DEBUG):
            self.logger().debug("Watermark info: %s" % str(info))
        if self._payload is not None:
            BER = (self._payload != payload_decoded).mean() * 100
            data_new.get_metadata()["wavmark-BER"] = BER
            self.logger().info("BER: %s" % str(BER))
        return data_new
