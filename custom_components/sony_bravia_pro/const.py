"""Constants for the Sony Bravia Pro integration."""

from typing import Final

DOMAIN: Final = "sony_bravia_pro"

CONF_PSK: Final = "psk"
CONF_MAC: Final = "mac"

DEFAULT_PORT: Final = 80
DEFAULT_SCAN_INTERVAL: Final = 15  # seconds
REQUEST_TIMEOUT: Final = 5  # seconds

PLATFORMS: Final = [
    "media_player",
    "remote",
    "button",
    "select",
    "sensor",
    "switch",
]

# Sony Bravia REST API service paths
SERVICE_SYSTEM: Final = "system"
SERVICE_AUDIO: Final = "audio"
SERVICE_AV_CONTENT: Final = "avContent"
SERVICE_APP_CONTROL: Final = "appControl"
SERVICE_VIDEO: Final = "video"
SERVICE_VIDEO_SCREEN: Final = "videoScreen"
SERVICE_ENCRYPTION: Final = "encryption"
SERVICE_GUIDE: Final = "guide"

# IRCC SOAP envelope
IRCC_SOAP_BODY: Final = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
    's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    "<s:Body>"
    '<u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">'
    "<IRCCCode>{ircc_code}</IRCCCode>"
    "</u:X_SendIRCC>"
    "</s:Body>"
    "</s:Envelope>"
)

IRCC_SOAP_ACTION: Final = '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"'

# Power states from API
POWER_STATUS_ACTIVE: Final = "active"
POWER_STATUS_STANDBY: Final = "standby"

# Power saving modes
POWER_SAVING_OFF: Final = "off"
POWER_SAVING_LOW: Final = "low"
POWER_SAVING_HIGH: Final = "high"
POWER_SAVING_PICTURE_OFF: Final = "pictureOff"

# Sound output targets
SOUND_OUTPUT_SPEAKER: Final = "speaker"
SOUND_OUTPUT_HDMI: Final = "hdmi"
SOUND_OUTPUT_SPEAKER_HDMI: Final = "speaker_hdmi"
SOUND_OUTPUT_AUDIO_SYSTEM: Final = "audioSystem"

SOUND_OUTPUT_OPTIONS: Final = {
    SOUND_OUTPUT_SPEAKER: "Speaker",
    SOUND_OUTPUT_HDMI: "HDMI",
    SOUND_OUTPUT_SPEAKER_HDMI: "Speaker + HDMI",
    SOUND_OUTPUT_AUDIO_SYSTEM: "Audio System",
}

# Screen rotation options
SCREEN_ROTATION_OPTIONS: Final = {
    0: "0\u00b0",
    90: "90\u00b0",
    180: "180\u00b0",
    270: "270\u00b0",
}

# WoL
WOL_PORT: Final = 9
