# Sony Bravia Pro — Home Assistant Custom Integration

## Objetivo
Construir una integración personalizada para Home Assistant que exponga 
toda la funcionalidad disponible en la Sony Bravia Pro REST API, muy 
superior a la integración oficial `sony_bravia` que existe actualmente.

## Contexto técnico
- Home Assistant corriendo en /config (accesible desde este LXC via NFS en /mnt/ha-config)
- TV Sony Bravia Pro en red local
- Ya existen scripts .sh manuales que usan esta API — ver /root/bravia-ha/examples/

## Documentación oficial — PRIORIDAD MÁXIMA
1. https://pro-bravia.sony.net/remote-display-control/rest-api/reference/
2. https://pro-bravia.sony.net/remote-display-control/rest-api/guide/

## Documentación secundaria (referencia, puede estar desactualizada)
- https://gist.github.com/kalleth/e10e8f3b8b7cb1bac21463b0073a65fb
- https://community.home-assistant.io/t/sony-bravia-tv-component-with-pre-shared-key/30698/164
- https://www.postman.com/niwtnt/sony-bravia-rest-api/documentation/yfax7bl/bravia-rest-api

## API Sony Bravia Pro — lo que sabemos
La TV expone una REST API HTTP en varios endpoints:
- /sony/appControl    — gestión de apps Android
- /sony/IRCC          — envío de códigos infrarrojos (SOAP)
- /sony/system        — info del sistema, power, etc.
- /sony/avContent     — fuentes de vídeo, contenido
- /sony/audio         — volumen, audio settings
- /sony/videoScreen   — gestión de pantalla (blank screen, picture mode...)
- /sony/accessControl — autenticación PSK

Autenticación: X-Auth-PSK header con la clave configurada en la TV

## Ejemplos de scripts actuales
Ver /root/bravia-ha/examples/ — muestran cómo se usan IRCC y appControl

## Estructura esperada de la integración HA
custom_components/sony_bravia_pro/
├── __init__.py
├── manifest.json
├── config_flow.py        ← wizard de configuración (IP, PSK, nombre)
├── coordinator.py        ← DataUpdateCoordinator, polling de estado
├── media_player.py       ← entidad principal
├── remote.py             ← envío de códigos IRCC
├── button.py             ← acciones puntuales (blank screen, etc.)
├── select.py             ← selección de fuente, app activa
├── sensor.py             ← info del sistema, versión FW, etc.
├── services.yaml         ← servicios personalizados
├── strings.json
└── translations/
    └── es.json

## Requisitos del config_flow
- Pedir IP de la TV
- Pedir PSK (Pre-Shared Key)
- Validar conexión antes de confirmar
- Descubrir nombre del modelo automáticamente
- Opción de discovery via SSDP/UPnP si la TV lo soporta

## Principios de desarrollo
1. SIEMPRE consultar la documentación oficial primero
2. Cada endpoint debe tener su wrapper en un cliente API separado (bravia_client.py)
3. Manejar correctamente TVs apagadas (WoL, connection refused)
4. Loggear errores con contexto útil para debugging
5. No hardcodear funcionalidades — descubrir capabilities de cada TV en runtime
6. Seguir exactamente los patrones de HA custom components 2024+
