from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "adc.api.Watermarker": [
            "adc_wavmark.watermarks",
        ],
        "adc.api.WatermarkDetector": [
            "adc_wavmark.watermarks",
        ],
    }
