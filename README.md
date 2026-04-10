# Sony Bravia Api

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured Home Assistant custom integration for **Sony Bravia Pro** professional displays, built on top of the [Sony Bravia Pro REST API](https://pro-bravia.sony.net/remote-display-control/rest-api/reference/).

This integration is significantly more capable than the built-in `braviatv` integration, exposing all available API functionality as native Home Assistant entities.

---

## Features

- **Media Player** — Power on/off, volume control (set, step, mute), input source selection, app launching, and media browser for apps and inputs
- **Remote Control** — Send any IRCC remote command by name or raw code (volume, navigation, playback, numbers, etc.)
- **Buttons** — Reboot, terminate apps, picture off (blank screen), picture on
- **Select Entities** — Sound output mode (speaker, HDMI, audio system), screen rotation (0°, 90°, 180°, 270°)
- **Sensors** — Model name, firmware version, serial number, MAC address (diagnostic)
- **Switches** — LED indicator on/off, Wake-on-LAN enable/disable
- **Custom Services** — Send IRCC codes, send text to on-screen keyboard, set picture quality, set scene mode, launch apps
- **Wake-on-LAN** — Automatically sends WoL magic packets to power on the TV from standby
- **Runtime Discovery** — Detects available features and IRCC codes per TV model at setup time
- **Media Browser** — Browse and launch installed Android apps and switch between inputs visually

---

## Prerequisites

1. A **Sony Bravia Pro** display on the same local network as your Home Assistant instance
2. **Pre-Shared Key (PSK)** authentication enabled on the TV:
   - Go to **Settings > Network & Internet > Local network setup > IP control > Authentication**
   - Set a PSK (any string, e.g., `1234`)
3. **Remote control** enabled on the TV:
   - Go to **Settings > Network & Internet > Remote device settings > Control remotely** → Enable
4. **Home Assistant 2024.1** or newer

---

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots menu (top right) → **Custom repositories**
3. Add the repository URL: `https://github.com/cmos486/sony-bravia-api`
4. Select category: **Integration**
5. Click **Add**
6. Search for **Sony Bravia Api** in HACS and click **Install**
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/cmos486/sony-bravia-api/releases) page
2. Copy the `custom_components/sony_bravia_pro/` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

---

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Sony Bravia Pro**
3. Enter the TV's **IP address** and the **Pre-Shared Key** you configured
4. The integration will validate the connection and auto-discover the TV model
5. Click **Submit**

> **Note:** The TV must be turned on (not in standby) during initial setup.

---

## Entities Created

After setup, the integration creates the following entities for your TV:

### Media Player
| Entity | Description |
|--------|-------------|
| `media_player.<tv_name>` | Main TV entity — power, volume, source selection, app launching |

**Source list** combines HDMI inputs and installed Android apps into one unified list.

### Remote
| Entity | Description |
|--------|-------------|
| `remote.<tv_name>_remote` | Send IRCC remote commands to the TV |

### Buttons
| Entity | Description |
|--------|-------------|
| `button.<tv_name>_reboot` | Reboot the TV |
| `button.<tv_name>_terminate_apps` | Close all foreground apps |
| `button.<tv_name>_picture_off` | Turn off the screen (blank) |
| `button.<tv_name>_picture_on` | Turn the screen back on |

### Selects
| Entity | Description |
|--------|-------------|
| `select.<tv_name>_sound_output` | Sound output mode: Speaker, HDMI, Speaker + HDMI, Audio System |
| `select.<tv_name>_screen_rotation` | Screen rotation: 0°, 90°, 180°, 270° |

### Sensors (Diagnostic)
| Entity | Description |
|--------|-------------|
| `sensor.<tv_name>_model` | TV model name |
| `sensor.<tv_name>_firmware` | Firmware version |
| `sensor.<tv_name>_serial_number` | Serial number |
| `sensor.<tv_name>_mac_address` | MAC address |

### Switches
| Entity | Description |
|--------|-------------|
| `switch.<tv_name>_led_indicator` | Toggle the front LED indicator |
| `switch.<tv_name>_wake_on_lan` | Enable/disable Wake-on-LAN |

---

## Services

### `sony_bravia_pro.send_ircc`
Send an IRCC remote control command.

```yaml
service: remote.send_command
target:
  entity_id: remote.bravia_tv_remote
data:
  command: VolumeUp
```

You can also send multiple commands:

```yaml
service: remote.send_command
target:
  entity_id: remote.bravia_tv_remote
data:
  command:
    - Home
    - Down
    - Down
    - Confirm
  num_repeats: 1
```

### `sony_bravia_pro.launch_app`
Launch an Android app by URI.

```yaml
service: media_player.play_media
target:
  entity_id: media_player.bravia_tv
data:
  media_content_type: app
  media_content_id: "com.sony.dtv.com.netflix.ninja.com.netflix.ninja.MainActivity"
```

### `sony_bravia_pro.set_picture_quality`
Adjust picture settings.

```yaml
service: sony_bravia_pro.set_picture_quality
target:
  entity_id: media_player.bravia_tv
data:
  target: brightness
  value: "50"
```

### `sony_bravia_pro.set_scene`
Set the scene/picture mode.

```yaml
service: sony_bravia_pro.set_scene
target:
  entity_id: media_player.bravia_tv
data:
  scene: auto
```

### `sony_bravia_pro.send_text`
Send text to the on-screen keyboard.

```yaml
service: sony_bravia_pro.send_text
target:
  entity_id: remote.bravia_tv_remote
data:
  text: "Hello World"
```

---

## Known IRCC Codes

These are common IRCC command names. The actual available commands depend on your TV model and are auto-discovered at setup time. Check the `available_commands` attribute on the remote entity for the full list.

| Command | Description |
|---------|-------------|
| `PowerOff` | Power off |
| `Input` | Input selector |
| `Num0` - `Num9` | Number keys |
| `VolumeUp` / `VolumeDown` | Volume |
| `Mute` | Toggle mute |
| `ChannelUp` / `ChannelDown` | Channel navigation |
| `Up` / `Down` / `Left` / `Right` | D-pad navigation |
| `Confirm` | Enter/OK |
| `Home` | Home screen |
| `Return` | Back/return |
| `Options` | Options menu |
| `Play` / `Pause` / `Stop` | Playback controls |
| `Next` / `Prev` | Track skip |
| `Display` | Show/hide OSD info |

---

## Troubleshooting

### TV not responding / cannot connect
- Ensure the TV is **powered on** (not in standby) for initial setup
- Verify the IP address is correct and the TV is on the same network
- Check that **IP Control** and **Remote control** are enabled in TV settings

### TV in standby — limited functionality
- When the TV is in **standby**, most API calls fail (this is a Sony limitation)
- The integration handles this gracefully — entities go to "off" / "unavailable"
- Enable **Wake-on-LAN** on the TV and in the integration to power on from standby

### TV in suspend — completely unreachable
- In **suspend mode**, the TV's HTTP server stops entirely
- You must use Wake-on-LAN to wake the TV, then the API becomes available again

### Netflix / YouTube not showing as current source
- `getPlayingContentInfo` returns empty data for native Android apps — this is a **known Sony API limitation**
- The integration will show the last known input or "Unknown" for streaming apps

### IRCC commands not working
- Check the `available_commands` attribute on the remote entity to see which commands your TV supports
- Not all TVs support all IRCC codes — the integration auto-discovers available codes at setup

### Sound output / screen rotation not applying
- Some settings are model-specific. If a setting fails, it may not be supported on your TV model

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push to the branch and open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## References

- [Sony Bravia Pro REST API Reference](https://pro-bravia.sony.net/remote-display-control/rest-api/reference/)
- [Sony Bravia Pro REST API Guide](https://pro-bravia.sony.net/remote-display-control/rest-api/guide/)
- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
