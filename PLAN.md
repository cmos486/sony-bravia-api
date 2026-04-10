# Sony Bravia Pro HA Integration — Architecture Plan

## Integration Identity
- **Domain:** `sony_bravia_pro`
- **Integration type:** `device` (single TV per config entry)
- **Min HA version:** 2024.1.0

---

## File Structure

```
custom_components/sony_bravia_pro/
├── __init__.py           # Integration setup, forward platforms
├── manifest.json         # Integration metadata
├── const.py              # Constants, domain, default values
├── bravia_client.py      # Sony Bravia REST API client
├── config_flow.py        # Config wizard (IP + PSK + validation)
├── coordinator.py        # DataUpdateCoordinator
├── entity.py             # Base entity class
├── media_player.py       # Main media player entity
├── remote.py             # IRCC remote entity
├── button.py             # Action buttons (reboot, blank screen, etc.)
├── select.py             # Picture mode, sound output, screen rotation
├── sensor.py             # System info sensors
├── switch.py             # LED indicator, WoL mode toggles
├── services.yaml         # Custom service definitions
├── strings.json          # English UI strings
└── translations/
    └── es.json           # Spanish translations
```

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Config Flow  │────>│   BraviaClient   │────>│  Sony Bravia TV │
│ (validate)   │     │  (REST + IRCC)   │     │  (HTTP API)     │
└──────┬───────┘     └────────┬─────────┘     └─────────────────┘
       │                      │
       v                      v
┌──────────────┐     ┌──────────────────┐
│ Config Entry │────>│  Coordinator     │
│ (IP, PSK)    │     │  (polls state)   │
└──────────────┘     └────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          v                   v                   v
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
   │ MediaPlayer │   │   Remote     │   │ Button/Sel.  │
   │ Entity      │   │   Entity     │   │ /Sensor/Sw.  │
   └─────────────┘   └──────────────┘   └──────────────┘
```

---

## Component Details

### 1. `const.py` — Constants

```python
DOMAIN = "sony_bravia_pro"
DEFAULT_PORT = 80
CONF_PSK = "psk"
SCAN_INTERVAL = 15  # seconds

# Platforms to load
PLATFORMS = ["media_player", "remote", "button", "select", "sensor", "switch"]
```

### 2. `bravia_client.py` — API Client

Async HTTP client using `aiohttp`. Single class `BraviaClient` with:

**Constructor:** `BraviaClient(host, psk, session)`

**Core method:** `async _request(service, method, params, version)` — JSON-RPC call

**Service wrappers organized by group:**

| Group | Methods |
|-------|---------|
| System | `get_system_info()`, `get_power_status()`, `set_power_status(on)`, `get_wol_mode()`, `set_wol_mode(on)`, `get_led_status()`, `set_led_status(on)`, `get_remote_controller_info()`, `get_supported_api_info()`, `get_power_saving_mode()`, `set_power_saving_mode(mode)`, `request_reboot()`, `get_current_time()`, `get_network_settings()`, `get_interface_info()` |
| Audio | `get_volume_info()`, `set_volume(level, target)`, `set_mute(on)`, `get_speaker_settings()`, `set_sound_settings(settings)` |
| AV Content | `get_playing_content()`, `set_play_content(uri)`, `get_external_inputs()`, `get_scheme_list()`, `get_source_list(scheme)`, `get_content_list(uri, start, count)` |
| App Control | `get_app_list()`, `set_active_app(uri)`, `get_app_status_list()`, `terminate_apps()` |
| Video | `get_picture_quality()`, `set_picture_quality(settings)`, `get_screen_rotation()`, `set_screen_rotation(angle)` |
| IRCC | `send_ircc(code)` — SOAP request |

**Error handling:**
- `BraviaError` — base exception
- `BraviaConnectionError` — TV unreachable (standby/suspend)
- `BraviaAuthError` — invalid PSK
- `BraviaTurnedOffError` — TV powered off (error code 7)
- Timeout: 5 seconds for all requests

### 3. `config_flow.py` — Configuration Wizard

**Step 1: User Input**
- Fields: host (IP address), psk (Pre-Shared Key)
- Validate by calling `get_system_info()` and `get_power_status()`
- On success: auto-discover model name and serial
- Use serial number as unique_id to prevent duplicate entries

**Error handling:**
- Connection timeout → "Cannot connect"
- Auth error → "Invalid PSK"
- TV must be ON during setup

### 4. `coordinator.py` — DataUpdateCoordinator

**Update interval:** 15 seconds

**Data fetched per poll:**
1. `get_power_status()` — always (lightweight)
2. If TV is active:
   - `get_volume_info()` — volume + mute state
   - `get_playing_content()` — current source/app
   - `get_external_inputs()` — connected inputs
   - `get_app_status_list()` — keyboard/cursor state

**Stored data structure:**
```python
@dataclass
class BraviaState:
    power: str  # "active" | "standby"
    volume: int | None
    is_muted: bool | None
    max_volume: int
    playing_content: dict | None  # uri, title, source
    external_inputs: list[dict]
    app_status: list[dict]
```

**Error handling in coordinator:**
- `ConnectionError` / timeout → set power to "off", mark unavailable
- Successive failures → exponential backoff (built into HA coordinator)

### 5. `entity.py` — Base Entity

```python
class BraviaEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=entry.data.get("model", "Sony Bravia Pro"),
            manufacturer="Sony",
            model=entry.data.get("model"),
            sw_version=entry.data.get("firmware"),
        )
```

All entities inherit from this, sharing a single HA device.

---

## Entity Mapping

### 6. `media_player.py` — Main Entity

**Features:**
- `TURN_ON`, `TURN_OFF` — via setPowerStatus + WoL
- `VOLUME_SET`, `VOLUME_STEP`, `VOLUME_MUTE` — via audio service
- `SELECT_SOURCE` — via setPlayContent (HDMI inputs) + setActiveApp (apps)
- `PLAY_MEDIA` — via setActiveApp for app URIs
- `BROWSE_MEDIA` — browse apps and inputs

**State mapping:**
| TV State | HA State |
|----------|----------|
| active + playing | STATE_ON |
| active + idle | STATE_IDLE |
| standby | STATE_OFF |
| unreachable | STATE_OFF |

**Source list:** Combines external inputs (HDMI 1, HDMI 2, etc.) + installed apps (Netflix, YouTube, etc.)

**Attributes:**
- `media_title` — from getPlayingContentInfo
- `source` — current input label or app name
- `source_list` — merged inputs + apps

### 7. `remote.py` — IRCC Remote

**Features:**
- `TURN_ON`, `TURN_OFF`
- Send command via `remote.send_command` service

**Implementation:**
- On setup: fetch IRCC codes via `getRemoteControllerInfo`, cache them
- `send_command(command)`: look up command name → IRCC code → send SOAP
- Support both command names ("VolumeUp") and raw IRCC codes

**Activity list:** Not applicable, but expose available commands as attribute.

### 8. `button.py` — Action Buttons

| Button | API Call | Icon |
|--------|----------|------|
| Reboot | system.requestReboot | mdi:restart |
| Terminate Apps | appControl.terminateApps | mdi:close-box-multiple |
| Picture Off | system.setPowerSavingMode("pictureOff") | mdi:monitor-off |
| Picture On | system.setPowerSavingMode("off") | mdi:monitor |

### 9. `select.py` — Selection Entities

| Select | API | Options |
|--------|-----|---------|
| Picture Mode | video.setPictureQualitySettings | Discovered from TV |
| Sound Output | audio.setSoundSettings | speaker, hdmi, speaker_hdmi, audioSystem |
| Screen Rotation | video.setScreenRotation | 0, 90, 180, 270 |

### 10. `sensor.py` — Information Sensors

| Sensor | API | Value |
|--------|-----|-------|
| Model | system.getSystemInformation | e.g., "FW-75BZ35L" |
| Firmware | system.getSystemInformation | Firmware version |
| Serial | system.getSystemInformation | Serial number |
| MAC Address | system.getSystemInformation | MAC address |

These are fetched once during setup and stored in config entry data. They're diagnostic sensors.

### 11. `switch.py` — Toggle Switches

| Switch | API Get/Set | Description |
|--------|------------|-------------|
| LED Indicator | getLEDIndicatorStatus / setLEDIndicatorStatus | Control front LED |
| Wake-on-LAN | getWolMode / setWolMode | Enable/disable WoL |

---

## Implementation Order

1. **Phase 1 — Foundation**
   - `const.py` — constants
   - `bravia_client.py` — full API client
   - `manifest.json` — integration metadata

2. **Phase 2 — Config & Coordinator**
   - `config_flow.py` — setup wizard
   - `strings.json` — UI strings
   - `coordinator.py` — state polling
   - `entity.py` — base entity
   - `__init__.py` — integration setup

3. **Phase 3 — Entities**
   - `media_player.py` — primary entity
   - `remote.py` — IRCC commands
   - `button.py` — action buttons
   - `select.py` — settings selectors
   - `sensor.py` — system info
   - `switch.py` — toggles

4. **Phase 4 — Polish**
   - `services.yaml` — custom services
   - `translations/es.json` — Spanish translation

---

## Key Design Decisions

1. **Single coordinator** — One polling loop for all entities, reduces API calls
2. **Runtime discovery** — Use `getSupportedApiInfo` to discover available features per TV
3. **Graceful degradation** — If TV is off/unreachable, entities go unavailable without errors
4. **Source merging** — External inputs + apps in one source list for media_player
5. **IRCC cache** — Fetch remote codes once, cache for session lifetime
6. **No PyPI dependency** — Client code lives inside the integration (custom component)
7. **WoL for power on** — Store MAC address, send magic packet when user turns on TV from standby
