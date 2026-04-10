# Sony Bravia Pro REST API — Research Document

## Overview

The Sony Bravia Pro displays expose a REST API over HTTP using **JSON-RPC 2.0** protocol. 
The API is organized into services, each accessible at a dedicated endpoint path. 
Authentication is via Pre-Shared Key (PSK) in a custom HTTP header.

---

## Authentication

### Pre-Shared Key (PSK)
- Header: `X-Auth-PSK: <key>`
- Configured on TV: Settings > Network & Internet > Local network setup > IP control > Authentication
- The PSK can be any character string

### Auth Levels
Each API method has one of three auth levels:
- **none** — No authentication required (read-only status queries)
- **generic** — Requires PSK header (control/write operations)  
- **private** — Requires PSK header with elevated access (sensitive data like app lists, network settings)

---

## Request Format (JSON-RPC 2.0)

```json
POST /sony/<service> HTTP/1.1
Host: <TV_IP>
X-Auth-PSK: <PSK>
Content-Type: application/json; charset=UTF-8

{
    "method": "<methodName>",
    "id": 1,
    "params": [{}],
    "version": "1.0"
}
```

- `method`: API method name
- `id`: Integer request identifier (arbitrary, returned in response)
- `params`: Array of parameter objects (often `[{}]` or `[]` for no params)
- `version`: API version string (e.g., "1.0", "1.1", "1.2")

### Response Format
```json
{"result": [<data>], "id": 1}
```

### Error Response
```json
{"error": [<code>, "<message>"], "id": 1}
```

---

## Services & Endpoints

### 1. Guide Service (`/sony/guide`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getSupportedApiInfo | 1.0 | none | Returns all available services and their supported API methods |

**getSupportedApiInfo** — Discovery endpoint. Returns array of service objects:
```json
{
    "service": "system",
    "protocols": ["xhrpost:jsonizer"],
    "apis": [{"name": "getSystemInformation", "versions": ["1.0", "1.7"]}],
    "notifications": [{"name": "notifyPowerStatus", "versions": ["1.0"]}]
}
```
Use this to discover what the specific TV model supports at runtime.

---

### 2. System Service (`/sony/system`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getSystemInformation | 1.0, 1.7 | none | Device info (model, serial, MAC, firmware) |
| getPowerStatus | 1.0 | none | Current power state |
| setPowerStatus | 1.0 | generic | Power on/off |
| getRemoteControllerInfo | 1.0 | none | Available IRCC remote codes |
| getNetworkSettings | 1.0 | private | Network configuration (IP, DNS) |
| getInterfaceInformation | 1.0 | none | Interface info |
| getSystemSupportedFunction | 1.0 | none | Supported features list |
| getLEDIndicatorStatus | 1.0 | none | LED status |
| setLEDIndicatorStatus | 1.0, 1.1 | generic | Control LED indicator |
| getPowerSavingMode | 1.0 | none | Power saving mode status |
| setPowerSavingMode | 1.0 | generic | Set power saving mode |
| getCurrentTime | 1.0, 1.1 | none | Device time |
| getWolMode | 1.0 | none | Wake-on-LAN status |
| setWolMode | 1.0 | generic | Enable/disable WoL |
| getRemoteDeviceSettings | 1.0 | private | Remote device settings |
| requestReboot | 1.0 | generic | Reboot device |
| getScreenshot | 1.0 | generic | Capture screen as PNG |

#### Key Method Details

**getSystemInformation** (v1.0)
```json
// Response: model name, serial, MAC address, firmware version, etc.
{"result": [{"product": "TV", "model": "FW-75BZ35L", "serial": "...", "macAddr": "...", "name": "..."}]}
```

**getPowerStatus** (v1.0)
```json
// Request: {"method": "getPowerStatus", "id": 1, "params": [], "version": "1.0"}
// Response when ON:
{"result": [{"status": "active"}], "id": 1}
// Response when STANDBY:
{"result": [{"status": "standby"}], "id": 1}
```

**setPowerStatus** (v1.0)
```json
// Power ON:
{"method": "setPowerStatus", "id": 1, "params": [{"status": true}], "version": "1.0"}
// Power OFF:
{"method": "setPowerStatus", "id": 1, "params": [{"status": false}], "version": "1.0"}
```

**getRemoteControllerInfo** (v1.0)
Returns array of IRCC button name/code mappings. Response varies by model.
```json
{"result": [[{"name": "PowerOff", "value": "AAAAAQAAAAEAAAAvAw=="}, {"name": "Input", "value": "..."}, ...]]}
```

**setLEDIndicatorStatus**
- v1.0: `{"status": true/false}`
- v1.1: `{"status": "on"/"off"}`

**setPowerSavingMode** (v1.0)
- `{"mode": "off"/"low"/"high"/"pictureOff"}` — values are device-specific

---

### 3. Audio Service (`/sony/audio`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getVolumeInformation | 1.0 | none | Volume levels, mute state |
| setAudioVolume | 1.0, 1.2 | generic | Set volume (absolute or relative) |
| setAudioMute | 1.0 | generic | Mute/unmute |
| getSpeakerSettings | 1.0 | none | Speaker configuration |
| setSpeakerSettings | 1.0 | generic | Configure speakers |
| setSoundSettings | 1.1 | generic | Audio output settings |

#### Key Method Details

**getVolumeInformation** (v1.0)
```json
{"result": [[
    {"target": "speaker", "volume": 25, "mute": false, "maxVolume": 100, "minVolume": 0},
    {"target": "headphone", "volume": 15, "mute": false, "maxVolume": 100, "minVolume": 0}
]]}
```

**setAudioVolume**
- v1.0: `{"target": "", "volume": "25"}` — target: "" (all), "speaker", "headphone"
  - Absolute: `"25"`, Relative: `"+5"` or `"-5"`
- v1.2: Adds `"ui": "on"/"off"` to show/hide volume OSD

**setAudioMute** (v1.0)
```json
{"method": "setAudioMute", "params": [{"status": true}], ...}  // mute
{"method": "setAudioMute", "params": [{"status": false}], ...} // unmute
```

**getSpeakerSettings** (v1.0)
- Targets: "tvPosition", "subwooferLevel", "subwooferFreq", "subwooferPhase", "subwooferPower"

**setSoundSettings** (v1.1)
- Output terminal: `{"settings": [{"target": "outputTerminal", "value": "speaker"}]}`
- Values: "speaker", "speaker_hdmi", "hdmi", "audioSystem"

---

### 4. AV Content Service (`/sony/avContent`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getPlayingContentInfo | 1.0 | private | Currently playing content |
| setPlayContent | 1.0 | generic | Switch input/play content |
| getCurrentExternalInputsStatus | 1.0, 1.1 | none | HDMI/input port status |
| getSchemeList | 1.0 | private | Available URI schemes |
| getSourceList | 1.0 | private | Sources for a scheme |
| getContentList | 1.5 | private | Browse content |
| getContentCount | 1.0, 1.1 | private | Content count |

#### Key Method Details

**getPlayingContentInfo** (v1.0)
```json
{"result": [{"uri": "extInput:hdmi?port=1", "source": "extInput:hdmi", "title": "HDMI 1"}]}
```
**Limitation:** Returns null/empty for native apps (Netflix, YouTube). Only reliable for TV inputs.

**setPlayContent** (v1.0)
```json
// Switch to HDMI 2:
{"method": "setPlayContent", "params": [{"uri": "extInput:hdmi?port=2"}], ...}
// Switch to HDMI 1:
{"method": "setPlayContent", "params": [{"uri": "extInput:hdmi?port=1"}], ...}
```

**getCurrentExternalInputsStatus**
- v1.0: Returns `uri`, `title`, `connection` (boolean), `label`, `icon`
- v1.1: Adds `status` field ("true"/"false"/null for signal detection)

**URI Formats for Inputs:**
- HDMI: `extInput:hdmi?port=N` (N=1-4)
- Component: `extInput:component?port=N`
- Composite: `extInput:composite?port=N`
- SCART: `extInput:scart?port=N`
- CEC: `extInput:cec?type=player&port=N`

**getSchemeList** (v1.0)
```json
{"result": [["extInput", "tv", "dlna", "storage"]]}
```

**getSourceList** (v1.0)
```json
// Request: {"params": [{"scheme": "extInput"}]}
// Response: [{"source": "extInput:hdmi"}, {"source": "extInput:component"}, ...]
```

**getContentList** (v1.5)
```json
// Request: {"params": [{"uri": "extInput:hdmi", "stIdx": 0, "cnt": 50}]}
// Response: [{"uri": "extInput:hdmi?port=1", "title": "HDMI 1", "index": 0}, ...]
```

---

### 5. App Control Service (`/sony/appControl`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getApplicationList | 1.0 | private | List installed apps |
| setActiveApp | 1.0 | generic | Launch an app |
| getApplicationStatusList | 1.0 | none | App status (textInput, cursor, webBrowse) |
| getWebAppStatus | 1.0 | private | Web app status |
| terminateApps | 1.0 | generic | Kill all foreground apps |
| setTextForm | 1.0, 1.1 | generic | Input text to keyboard |
| getTextForm | 1.1 | private | Read text from keyboard |
| prepareAppUpload | 1.0 | generic | Prepare for sideload (BZ series only) |
| installApp | 1.0 | generic | Install sideloaded app (BZ series only) |
| uninstallApp | 1.0 | generic | Uninstall app (BZ series only) |

#### Key Method Details

**getApplicationList** (v1.0)
```json
{"result": [[
    {"title": "Netflix", "uri": "com.sony.dtv.com.netflix.ninja.com.netflix.ninja.MainActivity", "icon": "http://..."},
    {"title": "YouTube", "uri": "com.sony.dtv.com.google.android.youtube.tv.com.google.android.apps.youtube.tv.MainActivity", "icon": "http://..."}
]]}
```

**setActiveApp** (v1.0)
```json
// Launch Netflix:
{"method": "setActiveApp", "params": [{"uri": "com.sony.dtv.com.netflix.ninja.com.netflix.ninja.MainActivity"}]}
// Launch web app:
{"method": "setActiveApp", "params": [{"uri": "localapp://webappruntime?url=https://example.com"}]}
```

**getApplicationStatusList** (v1.0)
```json
{"result": [[
    {"name": "textInput", "status": "off"},
    {"name": "cursorDisplay", "status": "off"},
    {"name": "webBrowse", "status": "off"}
]]}
```

**terminateApps** (v1.0) — Terminates all foreground apps. Some system apps may not terminate (error 41403).

---

### 6. Video Service (`/sony/video`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getPictureQualitySettings | 1.0 | none | Picture quality settings |
| setPictureQualitySettings | 1.0 | generic | Adjust picture quality |
| getScreenRotation | 1.0 | none | Screen rotation angle |
| setScreenRotation | 1.0 | generic | Rotate screen |

#### Key Method Details

**setPictureQualitySettings** (v1.0)
```json
{"method": "setPictureQualitySettings", "params": [{"settings": [
    {"target": "brightness", "value": "50"},
    {"target": "contrast", "value": "50"}
]}]}
```

**setScreenRotation** (v1.0)
```json
{"method": "setScreenRotation", "params": [{"angle": 0}]}  // 0, 90, 180, 270
```

---

### 7. VideoScreen Service (`/sony/videoScreen`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| setSceneSetting | 1.0 | generic | Set scene/picture mode |

**Note:** The official Bravia Pro documentation only lists `setSceneSetting`. Other methods 
like blank screen may be handled via IRCC codes or power saving mode (`setPowerSavingMode` 
with mode `"pictureOff"`).

---

### 8. Encryption Service (`/sony/encryption`)

| Method | Version | Auth | Description |
|--------|---------|------|-------------|
| getPublicKey | 1.0 | none | RSA public key for text encryption |

Used with `setTextForm` v1.1 for encrypted keyboard input.

---

### 9. IRCC Service (`/sony/IRCC`)

The IRCC endpoint uses **SOAP/XML** format, not JSON-RPC.

#### Request Format
```xml
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" 
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">
            <IRCCCode>BASE64_CODE_HERE</IRCCCode>
        </u:X_SendIRCC>
    </s:Body>
</s:Envelope>
```

#### Headers
```
Content-Type: text/xml; charset=UTF-8
X-Auth-PSK: <PSK>
SOAPACTION: "urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"
```

#### Known IRCC Codes
Codes are obtained at runtime via `getRemoteControllerInfo`. Common codes include:

| Button | Code |
|--------|------|
| PowerOff | AAAAAQAAAAEAAAAvAw== |
| Display/BlankScreen | AAAAAQAAAAEAAAA+Aw== |
| Input | AAAAAQAAAAEAAAAlAw== |
| Num1 | AAAAAQAAAAEAAAAAAw== |
| Num2 | AAAAAQAAAAEAAAABAw== |
| Num3 | AAAAAQAAAAEAAAACAw== |
| Num4 | AAAAAQAAAAEAAAADAw== |
| Num5 | AAAAAQAAAAEAAAAEAw== |
| Num6 | AAAAAQAAAAEAAAAFAw== |
| Num7 | AAAAAQAAAAEAAAAGAw== |
| Num8 | AAAAAQAAAAEAAAAHAw== |
| Num9 | AAAAAQAAAAEAAAAIAw== |
| Num0 | AAAAAQAAAAEAAAAJAw== |
| VolumeUp | AAAAAQAAAAEAAAASAw== |
| VolumeDown | AAAAAQAAAAEAAAATAw== |
| Mute | AAAAAQAAAAEAAAAUAw== |
| ChannelUp | AAAAAQAAAAEAAAAQAw== |
| ChannelDown | AAAAAQAAAAEAAAARAw== |
| Up | AAAAAQAAAAEAAAB0Aw== |
| Down | AAAAAQAAAAEAAAB1Aw== |
| Left | AAAAAQAAAAEAAAB2Aw== |
| Right | AAAAAQAAAAEAAAB3Aw== |
| Confirm/Enter | AAAAAQAAAAEAAABlAw== |
| Home | AAAAAQAAAAEAAABgAw== |
| Return/Back | AAAAAgAAAJcAAAAjAw== |
| Options | AAAAAgAAAJcAAAA2Aw== |
| Play | AAAAAgAAAJcAAAAaAw== |
| Pause | AAAAAgAAAJcAAAAZAw== |
| Stop | AAAAAgAAAJcAAAAYAw== |
| Next | AAAAAgAAAJcAAAA8Aw== |
| Prev | AAAAAgAAAJcAAAA7Aw== |

**Important:** The actual available codes vary by TV model. Always use `getRemoteControllerInfo` to discover them at runtime.

---

## Power Management & Wake-on-LAN

### States
- **active** — TV is on, API fully available
- **standby** — TV is in standby, limited API available (getPowerStatus works, most others fail)
- **suspend** — HTTP server stops completely, no API access at all

### Wake-on-LAN Process
1. Get MAC address via `getSystemInformation` (while TV is active)
2. Create magic packet: `FF FF FF FF FF FF` + MAC address repeated 16 times
3. Send UDP to broadcast address on port 9 or 7
4. Wait for TV to boot (can take 10-30 seconds)
5. Call `setPowerStatus(true)` if in Normal Mode (Pro Mode auto-enables display)

### TV Setup Requirements
1. Enable remote control: Settings > Network & Internet > Remote device settings > Control remotely
2. Enable Wake-on-LAN for standby recovery
3. Set PSK: Settings > Network & Internet > Local network setup > IP control > Authentication

---

## Quirks & Edge Cases

### API Availability by Model
- Not all endpoints exist on all models — check with `getSupportedApiInfo`
- FW-BZxxx series has exclusive app sideloading (prepareAppUpload, installApp, uninstallApp)
- Newer models may drop older API versions
- Some endpoints return HTTP 404 on unsupported models

### getPlayingContentInfo Limitations
- Only returns data when source information is in the TV's OSD
- Returns null/empty for native Android apps (Netflix, YouTube, etc.)
- HDMI inputs may return incomplete data on some models

### Suspend vs Standby
- **Standby**: Network stack running, can respond to some API calls
- **Suspend**: Network stack stopped, no HTTP response at all — need WoL
- Integration must handle both `ConnectionRefused` (suspend) and error responses (standby)

### Volume Control
- Volume range varies by model (typically 0-100)
- Supports relative volume changes: "+5", "-5"
- Some models have separate speaker and headphone volumes

### App URIs
- Format: `com.sony.dtv.<package>.<activity>`
- Not standardized across models — must discover via `getApplicationList`
- Web apps: `localapp://webappruntime?url=<encoded_url>`

### Error Code 7
Returned by many methods when the TV is powered off or in a state that doesn't support the operation.

### Polling Recommendations
- No WebSocket/push notification support documented for HTTP API
- Poll at reasonable intervals (10-30 seconds) to avoid overwhelming the TV
- `getPowerStatus` is lightweight and suitable for frequent polling
- Batch multiple status queries when TV is active

---

## Discovery

### Runtime Capability Discovery
```json
// Discover all supported APIs:
POST /sony/guide
{"method": "getSupportedApiInfo", "id": 1, "params": [{"services": []}], "version": "1.0"}
```

### Per-Service Method Discovery
```json
// Discover methods for a specific service:
POST /sony/<service>
{"method": "getMethodTypes", "id": 1, "params": [""], "version": "1.0"}
```

### UPnP Discovery
TV may expose UPnP descriptor at `http://<TV_IP>:52323/dmr.xml` with capability listing.

---

## Summary: Endpoint → HA Entity Mapping

| API Endpoint | HA Platform | Purpose |
|-------------|-------------|---------|
| system.getPowerStatus / setPowerStatus | media_player | Power on/off |
| audio.getVolumeInformation / setAudioVolume / setAudioMute | media_player | Volume control |
| avContent.getPlayingContentInfo / setPlayContent | media_player | Source selection |
| avContent.getCurrentExternalInputsStatus | media_player | Source list |
| appControl.getApplicationList / setActiveApp | media_player + select | App launching |
| system.getRemoteControllerInfo + IRCC | remote | Remote control |
| system.requestReboot | button | Reboot button |
| appControl.terminateApps | button | Kill apps button |
| system.setPowerSavingMode("pictureOff") | button | Blank screen |
| video.setPictureQualitySettings | select/number | Picture settings |
| video.setScreenRotation | select | Screen rotation |
| system.setLEDIndicatorStatus | switch/button | LED control |
| system.setWolMode | switch | WoL enable/disable |
| system.getSystemInformation | sensor | Model, firmware, serial |
| system.getCurrentTime | sensor | Device time |
| audio.getSpeakerSettings | sensor | Speaker info |
