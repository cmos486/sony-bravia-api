# IRCC Remote Commands Reference

Complete list of predefined IRCC (Infrared Remote Control Code) commands for Sony Bravia Pro displays.

> **Note:** The actual available commands depend on your specific TV model. The integration auto-discovers supported commands at setup time. Check the `available_commands` attribute on the `remote` entity for your TV's specific list.

## Usage

```yaml
service: remote.send_command
target:
  entity_id: remote.bravia_api
data:
  command: VolumeUp
```

Multiple commands:
```yaml
service: remote.send_command
target:
  entity_id: remote.bravia_api
data:
  command:
    - Home
    - Down
    - Down
    - Confirm
```

With repeat and delay:
```yaml
service: remote.send_command
target:
  entity_id: remote.bravia_api
data:
  command: VolumeUp
  num_repeats: 5
  delay_secs: 0.3
```

Using the custom service:
```yaml
service: sony_bravia_pro.send_ircc
target:
  entity_id: remote.bravia_api
data:
  command: Netflix
```

Raw IRCC code (base64):
```yaml
service: sony_bravia_pro.send_ircc
target:
  entity_id: remote.bravia_api
data:
  command: AAAAAQAAAAEAAAASAw==
```

---

## Command List

### Power
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `PowerOff` | `AAAAAQAAAAEAAAAvAw==` | Power off / Standby |
| `Sleep` | `AAAAAQAAAAEAAAAvAw==` | Sleep timer toggle |

### Input Selection
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Input` | `AAAAAQAAAAEAAAAlAw==` | Cycle through inputs |
| `HDMI1` | `AAAAAgAAABoAAABaAw==` | Switch to HDMI 1 |
| `HDMI2` | `AAAAAgAAABoAAABbAw==` | Switch to HDMI 2 |
| `HDMI3` | `AAAAAgAAABoAAABcAw==` | Switch to HDMI 3 |
| `HDMI4` | `AAAAAgAAABoAAABdAw==` | Switch to HDMI 4 |
| `ChangeMediaAudio` | `AAAAAQAAAAEAAAAXAw==` | Change media audio |

### Number Keys
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Num0` | `AAAAAQAAAAEAAAAJAw==` | Number 0 |
| `Num1` | `AAAAAQAAAAEAAAAAAw==` | Number 1 |
| `Num2` | `AAAAAQAAAAEAAAABAw==` | Number 2 |
| `Num3` | `AAAAAQAAAAEAAAACAw==` | Number 3 |
| `Num4` | `AAAAAQAAAAEAAAADAw==` | Number 4 |
| `Num5` | `AAAAAQAAAAEAAAAEAw==` | Number 5 |
| `Num6` | `AAAAAQAAAAEAAAAFAw==` | Number 6 |
| `Num7` | `AAAAAQAAAAEAAAAGAw==` | Number 7 |
| `Num8` | `AAAAAQAAAAEAAAAHAw==` | Number 8 |
| `Num9` | `AAAAAQAAAAEAAAAIAw==` | Number 9 |
| `DOT` | `AAAAAgAAAJcAAAAdAw==` | Decimal dot |

### Volume & Channel
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `VolumeUp` | `AAAAAQAAAAEAAAASAw==` | Volume up |
| `VolumeDown` | `AAAAAQAAAAEAAAATAw==` | Volume down |
| `Mute` | `AAAAAQAAAAEAAAAUAw==` | Toggle mute |
| `ChannelUp` | `AAAAAQAAAAEAAAAQAw==` | Channel up |
| `ChannelDown` | `AAAAAQAAAAEAAAARAw==` | Channel down |

### Navigation
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Up` | `AAAAAQAAAAEAAAB0Aw==` | D-pad up |
| `Down` | `AAAAAQAAAAEAAAB1Aw==` | D-pad down |
| `Left` | `AAAAAQAAAAEAAAB2Aw==` | D-pad left |
| `Right` | `AAAAAQAAAAEAAAB3Aw==` | D-pad right |
| `Confirm` | `AAAAAQAAAAEAAABlAw==` | Enter / OK |
| `Home` | `AAAAAQAAAAEAAABgAw==` | Home screen |
| `Return` | `AAAAAgAAAJcAAAAjAw==` | Back / Return |
| `Exit` | `AAAAAQAAAAEAAABjAw==` | Exit |
| `Options` | `AAAAAgAAAJcAAAA2Aw==` | Options menu |
| `Menu` | `AAAAAgAAAJcAAAA2Aw==` | Menu (alias for Options) |
| `TopMenu` | `AAAAAgAAABoAAABgAw==` | Top menu (disc) |
| `PopUpMenu` | `AAAAAgAAABoAAABhAw==` | Pop-up menu (disc) |

### Playback Controls
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Play` | `AAAAAgAAAJcAAAAaAw==` | Play |
| `Pause` | `AAAAAgAAAJcAAAAZAw==` | Pause |
| `Stop` | `AAAAAgAAAJcAAAAYAw==` | Stop |
| `Next` | `AAAAAgAAAJcAAAA8Aw==` | Next track / chapter |
| `Prev` | `AAAAAgAAAJcAAAA7Aw==` | Previous track / chapter |
| `Forward` | `AAAAAgAAAJcAAAAcAw==` | Fast forward |
| `Rewind` | `AAAAAgAAAJcAAAAbAw==` | Rewind |
| `Replay` | `AAAAAgAAAJcAAAB2Aw==` | Replay / Instant replay |
| `Advance` | `AAAAAgAAAJcAAAB3Aw==` | Advance |
| `Rec` | `AAAAAgAAAJcAAAAgAw==` | Record |
| `TVPause` | `AAAAAgAAAJcAAAAZAw==` | TV Pause |

### Color Buttons
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Red` | `AAAAAgAAAJcAAAAlAw==` | Red button |
| `Green` | `AAAAAgAAAJcAAAAmAw==` | Green button |
| `Yellow` | `AAAAAgAAAJcAAAAnAw==` | Yellow button |
| `Blue` | `AAAAAgAAAJcAAAAkAw==` | Blue button |

### Display & Information
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Display` | `AAAAAQAAAAEAAAA+Aw==` | Display info / Picture off |
| `EPG` | `AAAAAgAAAKQAAABbAw==` | Electronic Program Guide |
| `Guide` | `AAAAAgAAAKQAAABbAw==` | Guide (alias for EPG) |
| `Info` | `AAAAAQAAAAEAAAA6Aw==` | Info overlay |
| `Subtitle` | `AAAAAgAAAJcAAAAoAw==` | Toggle subtitles |
| `ClosedCaption` | `AAAAAgAAAKQAAAAQAw==` | Closed captions |
| `Teletext` | `AAAAAQAAAAEAAAA/Aw==` | Teletext |

### Apps & Services
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `Netflix` | `AAAAAgAAABoAAAB8Aw==` | Launch Netflix |
| `ActionMenu` | `AAAAAgAAAMQAAABLAw==` | Action menu |
| `ApplicationLauncher` | `AAAAAgAAAMQAAAAqAw==` | Application launcher |
| `Help` | `AAAAAgAAAMQAAABNAw==` | Help screen |
| `SEN` | `AAAAAgAAABoAAAB9Aw==` | Sony Entertainment Network |
| `InternetWidgets` | `AAAAAgAAABoAAAB6Aw==` | Internet widgets |
| `InternetVideo` | `AAAAAgAAABoAAAB5Aw==` | Internet video |

### TV Functions
| Command | IRCC Code | Description |
|---------|-----------|-------------|
| `TV` | `AAAAAQAAAAEAAAAkAw==` | Switch to TV |
| `Digital` | `AAAAAgAAAJcAAAAyAw==` | Digital TV |
| `Analog` | `AAAAAgAAAHcAAAANAw==` | Analog TV |
| `Wide` | `AAAAAgAAAKQAAAA9Aw==` | Wide mode / Aspect ratio |
| `Jump` | `AAAAAQAAAAEAAAA7Aw==` | Jump (previous channel) |
| `PicOff` | `AAAAAQAAAAEAAAA+Aw==` | Picture off (blank screen) |
| `PictureMode` | `AAAAAgAAAJcAAABiAw==` | Cycle picture modes |
| `DemoMode` | `AAAAAgAAAJcAAABLAw==` | Demo mode |
| `Favorite` | `AAAAAgAAAHcAAABqAw==` | Favorites |
| `iManual` | `AAAAAgAAABoAAAB7Aw==` | i-Manual |
| `FootballMode` | `AAAAAgAAABoAAAB2Aw==` | Football/Sports mode |
| `Social` | `AAAAAgAAABoAAAB0Aw==` | Social features |
