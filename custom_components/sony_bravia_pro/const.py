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

# Predefined IRCC command codes
# These are common across most Sony Bravia models.
# The actual available codes are discovered at runtime via getRemoteControllerInfo,
# but these serve as a fallback and reference.
IRCC_CODES: Final[dict[str, str]] = {
    # Power
    "PowerOff": "AAAAAQAAAAEAAAAvAw==",
    "Sleep": "AAAAAQAAAAEAAAAvAw==",
    # Input
    "Input": "AAAAAQAAAAEAAAAlAw==",
    "ChangeMediaAudio": "AAAAAQAAAAEAAAAXAw==",
    "HDMI1": "AAAAAgAAABoAAABaAw==",
    "HDMI2": "AAAAAgAAABoAAABbAw==",
    "HDMI3": "AAAAAgAAABoAAABcAw==",
    "HDMI4": "AAAAAgAAABoAAABdAw==",
    # Numbers
    "Num0": "AAAAAQAAAAEAAAAJAw==",
    "Num1": "AAAAAQAAAAEAAAAAAw==",
    "Num2": "AAAAAQAAAAEAAAABAw==",
    "Num3": "AAAAAQAAAAEAAAACAw==",
    "Num4": "AAAAAQAAAAEAAAADAw==",
    "Num5": "AAAAAQAAAAEAAAAEAw==",
    "Num6": "AAAAAQAAAAEAAAAFAw==",
    "Num7": "AAAAAQAAAAEAAAAGAw==",
    "Num8": "AAAAAQAAAAEAAAAHAw==",
    "Num9": "AAAAAQAAAAEAAAAIAw==",
    "DOT": "AAAAAgAAAJcAAAAdAw==",
    # Volume & Channel
    "VolumeUp": "AAAAAQAAAAEAAAASAw==",
    "VolumeDown": "AAAAAQAAAAEAAAATAw==",
    "Mute": "AAAAAQAAAAEAAAAUAw==",
    "ChannelUp": "AAAAAQAAAAEAAAAQAw==",
    "ChannelDown": "AAAAAQAAAAEAAAARAw==",
    # Navigation
    "Up": "AAAAAQAAAAEAAAB0Aw==",
    "Down": "AAAAAQAAAAEAAAB1Aw==",
    "Left": "AAAAAQAAAAEAAAB2Aw==",
    "Right": "AAAAAQAAAAEAAAB3Aw==",
    "Confirm": "AAAAAQAAAAEAAABlAw==",
    "Home": "AAAAAQAAAAEAAABgAw==",
    "Return": "AAAAAgAAAJcAAAAjAw==",
    "Exit": "AAAAAQAAAAEAAABjAw==",
    "Options": "AAAAAgAAAJcAAAA2Aw==",
    "Menu": "AAAAAgAAAJcAAAA2Aw==",
    # Playback
    "Play": "AAAAAgAAAJcAAAAaAw==",
    "Pause": "AAAAAgAAAJcAAAAZAw==",
    "Stop": "AAAAAgAAAJcAAAAYAw==",
    "Next": "AAAAAgAAAJcAAAA8Aw==",
    "Prev": "AAAAAgAAAJcAAAA7Aw==",
    "Forward": "AAAAAgAAAJcAAAAcAw==",
    "Rewind": "AAAAAgAAAJcAAAAbAw==",
    "Replay": "AAAAAgAAAJcAAAB2Aw==",
    "Advance": "AAAAAgAAAJcAAAB3Aw==",
    # Color buttons
    "Red": "AAAAAgAAAJcAAAAlAw==",
    "Green": "AAAAAgAAAJcAAAAmAw==",
    "Yellow": "AAAAAgAAAJcAAAAnAw==",
    "Blue": "AAAAAgAAAJcAAAAkAw==",
    # Display & Info
    "Display": "AAAAAQAAAAEAAAA+Aw==",
    "EPG": "AAAAAgAAAKQAAABbAw==",
    "Guide": "AAAAAgAAAKQAAABbAw==",
    "Info": "AAAAAQAAAAEAAAA6Aw==",
    "ClosedCaption": "AAAAAgAAAKQAAAAQAw==",
    "Subtitle": "AAAAAgAAAJcAAAAoAw==",
    "SubTitle": "AAAAAgAAAJcAAAAoAw==",
    "Teletext": "AAAAAQAAAAEAAAA/Aw==",
    # Audio
    "Audio": "AAAAAQAAAAEAAAAXAw==",
    "SpeakerVolume": "AAAAAQAAAAEAAAASAw==",
    # Apps & Services
    "Netflix": "AAAAAgAAABoAAAB8Aw==",
    "ActionMenu": "AAAAAgAAAMQAAABLAw==",
    "ApplicationLauncher": "AAAAAgAAAMQAAAAqAw==",
    "Help": "AAAAAgAAAMQAAABNAw==",
    "SEN": "AAAAAgAAABoAAAB9Aw==",
    "InternetWidgets": "AAAAAgAAABoAAAB6Aw==",
    "InternetVideo": "AAAAAgAAABoAAAB5Aw==",
    # TV functions
    "TV": "AAAAAQAAAAEAAAAkAw==",
    "Digital": "AAAAAgAAAJcAAAAyAw==",
    "Analog": "AAAAAgAAAHcAAAANAw==",
    "BS": "AAAAAgAAAJcAAAAsAw==",
    "CS": "AAAAAgAAAJcAAAArAw==",
    "BSCS": "AAAAAgAAAJcAAAAQAw==",
    "Ddata": "AAAAAgAAAJcAAAAVAw==",
    "PicOff": "AAAAAQAAAAEAAAA+Aw==",
    "DemoMode": "AAAAAgAAAJcAAABLAw==",
    "Wide": "AAAAAgAAAKQAAAA9Aw==",
    "Jump": "AAAAAQAAAAEAAAA7Aw==",
    "PAP": "AAAAAgAAAKQAAAB3Aw==",
    "TopMenu": "AAAAAgAAABoAAABgAw==",
    "PopUpMenu": "AAAAAgAAABoAAABhAw==",
    "Rec": "AAAAAgAAAJcAAAAgAw==",
    "RecList": "AAAAAgAAAJcAAAAlAw==",
    # Picture
    "PictureMode": "AAAAAgAAAJcAAABiAw==",
    "PictureMute": "AAAAAQAAAAEAAAA+Aw==",
    # Misc
    "GGuide": "AAAAAQAAAAEAAAAOAw==",
    "CC": "AAAAAgAAAKQAAAAQAw==",
    "Favorite": "AAAAAgAAAHcAAABqAw==",
    "iManual": "AAAAAgAAABoAAAB7Aw==",
    "MIX": "AAAAAgAAAJcAAAArAw==",
    "FlashPlus": "AAAAAgAAAJcAAAB4Aw==",
    "FlashMinus": "AAAAAgAAAJcAAAB5Aw==",
    "TVPause": "AAAAAgAAAJcAAAAZAw==",
    "FootballMode": "AAAAAgAAABoAAAB2Aw==",
    "Social": "AAAAAgAAABoAAAB0Aw==",
}
