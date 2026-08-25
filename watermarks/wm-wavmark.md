# wm-wavmark

Applies the WavMark watermarking: https://github.com/wavmark/wavmark

```
usage: wm-wavmark [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [-N LOGGER_NAME] [--disable] -p PAYLOAD [-d DEVICE]
                  [-m MIN_SNR] [-M MAX_SNR]

Applies the WavMark watermarking: https://github.com/wavmark/wavmark

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --disable             Whether to disable the watermarker (default: False)
  -p PAYLOAD, --payload PAYLOAD
                        The 16-bit payload to embed (0 <= x < 65536).
                        (default: 42)
  -d DEVICE, --device DEVICE
                        The torch device to run the model on, e.g., 'cpu' or
                        'cuda:0'. (default: cpu)
  -m MIN_SNR, --min_snr MIN_SNR
                        The minimum signal-to-noise ratio. (default: 20)
  -M MAX_SNR, --max_snr MAX_SNR
                        The maximum signal-to-noise ratio. (default: 38)
```
