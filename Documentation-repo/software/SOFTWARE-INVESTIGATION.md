# Software Investigation Record

**Status:** Proposed and investigated areas; no implementation is evidenced by the supplied project history.

## Development environment

No MCU toolchain, IDE, firmware repository or version has been established by available evidence. The ESP32-S3 board suggests Arduino/ESP-IDF compatibility may be investigated, but this is not approved or implemented.

## MCU architecture

A small state-machine approach is proposed:

- Boot and hardware self-check.
- Idle/deep-sleep state.
- SOS wake-up and debounce.
- GNSS acquisition or cached-position fallback.
- Outbound LoRa packet preparation.
- LTE SMS preparation when selected.
- Retry and backoff.
- Local feedback and fault reporting.

This architecture is conceptual. It must be revised once exact hardware interfaces are known.

## LoRa software

Investigated/proposed areas:

- SPI or board-integrated radio API depending on Core1262-868M wiring.
- LoRa packet encoding and acknowledgement semantics.
- Frequency and spreading-factor configuration appropriate to the 868 MHz environment.
- Duty-cycle and regulatory handling.
- RSSI/SNR reporting.
- Meshtastic integration as a possible compatibility feature.

No LoRa library or firmware implementation is evidenced.

## Meshtastic

Meshtastic is a possible integration, not a current confirmed implementation. Remaining questions include:

- Core1262-868M compatibility.
- Firmware and radio interface support.
- Channel/key configuration.
- Message format and delivery semantics.
- Battery impact.
- Whether existing Irish Meshtastic infrastructure is usable for this use case.

## Cellular software

The proposed LTE modem interface is AT-command based. Required areas include:

- modem initialisation and SIM readiness;
- network registration and band/status reporting;
- SMS mode and text/PDU handling;
- GNSS queries or NMEA parsing;
- modem reset and recovery;
- error classification;
- network registration timeout;
- SMS confirmation and retry limits.

No AT command implementation or Irish-network test evidence exists.

## GNSS software

Potential functions:

- NMEA parsing or modem-specific GNSS position access.
- Fix timeout.
- Accuracy and validity checking.
- Last-known-position policy.
- Position inclusion in SMS and LoRa messages.
- GNSS/cellular coexistence testing.

## SOS logic

Proposed behavior:

- physical wake-up from SOS button;
- software debounce and press duration;
- prevent accidental repeat transmission;
- optional cancellation interval;
- collect position and network context;
- attempt configured delivery paths;
- provide local feedback;
- retain state for retry if power permits.

Actual button, latency and delivery behaviour are not implemented or measured.

## Power management

Potential functions:

- deep sleep and interrupt wake-up;
- modem LTE state control;
- periodic GNSS acquisition;
- radio sleep states;
- battery voltage monitoring;
- low-battery emergency policy;
- solar charging status reporting if supported.

No firmware power measurements or sleep profile are evidenced.

## Communication fallback

The communication priority is unresolved. A proposed abstraction should allow a policy layer to select LoRa or LTE independently of each transport implementation. It should not make a silent assumption that LoRa is primary or LTE is primary.

## Error handling and feedback

The following are proposed:

- LED or haptic feedback for initiation, delivery attempt and failure;
- retry limits with bounded time;
- modem reset after fatal or persistent errors;
- separate LoRa, LTE and GNSS fault states;
- serial diagnostics in development mode;
- no false display of “SOS delivered” without transport confirmation.

## Application integration

No mobile application or web recipient system is evidenced. Potential integration includes SMS recipient configuration, Meshtastic display, or a later application interface. These remain ideas until approved.
