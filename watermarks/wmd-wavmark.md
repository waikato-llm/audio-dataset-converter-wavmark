# wmd-wavmark

For detecting WavMark watermarks: https://github.com/wavmark/wavmark

```
usage: wmd-wavmark [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [-N LOGGER_NAME] [--disable] [-p PAYLOAD] [-d DEVICE]

For detecting WavMark watermarks: https://github.com/wavmark/wavmark

options:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  --disable             Whether to disable the watermark detector (default:
                        False)
  -p PAYLOAD, --payload PAYLOAD
                        The 16-bit payload to check against (0 <= x < 65536).
                        (default: 42)
  -d DEVICE, --device DEVICE
                        The torch device to run the model on, e.g., 'cpu' or
                        'cuda:0'. (default: cpu)
```
