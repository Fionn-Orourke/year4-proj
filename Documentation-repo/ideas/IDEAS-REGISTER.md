# Ideas and Proposals Register

**Status:** Unapproved ideas only. Nothing in this register is promoted to a Feature Version or Master.

## Communication concepts

- **LoRa emergency relay:** send a compact SOS packet through nearby LoRa nodes.
- **Meshtastic-compatible mode:** investigate integration with existing Meshtastic infrastructure.
- **Custom LoRa protocol:** implement a small SOS-focused protocol instead of relying on Meshtastic.
- **LTE SMS fallback:** use LTE to send an SMS after a local or LoRa path fails or is unavailable.
- **Hybrid LoRa-first policy:** attempt LoRa and then LTE if delivery or coverage requirements justify it.
- **LTE-first policy:** attempt LTE first when sufficient coverage and battery conditions exist.
- **Dual-transport acknowledgement:** indicate locally whether LoRa or SMS delivery is confirmed.
- **Store-and-forward:** retain unsent alerts and retry after link recovery.
- **Periodic location/status beacon:** send position and battery state at a configurable interval.
- **Check-in mode:** distinguish a normal check-in from SOS activation.

## Safety and user interface ideas

- Protected SOS button requiring press-and-hold or a multi-action sequence.
- Single short press for status and held press for SOS.
- Two-stage SOS indication with cancellation before transmission.
- LED states for GNSS, LoRa, LTE, battery, and transmission state.
- Audible feedback for successful SOS initiation and network failure.
- Tactile switch protected against accidental activation in a pocket or rucksack.
- Physical test mode that does not send real emergency alerts.

## Hardware ideas

- Waveshare Core1262-868M as the current LoRa working direction.
- Waveshare ESP32-S3-A7670E-4G as the current cellular/controller working direction.
- External GNSS antenna and LTE antenna with appropriate connectors.
- External 868 MHz LoRa antenna for range and regulatory suitability.
- Protected Li-Po battery pack.
- Protected 18650 3000 mAh battery with suitable charging and protection circuitry.
- 2000 mAh Li-Po battery.
- Solar charging with a panel sized against actual battery and sleep current measurements.
- IP65 enclosure with cable glands or sealed connectors.
- U.FL/IPEX internal links and SMA external antenna connectors.
- Low-power buck/boost supply and appropriate bulk capacitance for LTE peak current.

## Software ideas

- ESP32-S3 firmware architecture with state-machine-based SOS handling.
- Deep-sleep state with an interrupt-based SOS wake-up.
- GNSS acquisition with timeout and cached last-known position.
- LTE modem AT command abstraction.
- SMS message formatting and recipient configuration.
- LoRa packet encoding abstraction.
- Meshtastic library or service integration if compatibility is proven.
- Error logging and local status history.
- Boot-time hardware and radio self-test.
- Automatic retry and backoff policy.
- Data connection disabled unless required to reduce power.

## Deferred or rejected-history ideas

- The nRF9151/MDBT50Q-U1MV2/custom-PCB route remains historical until evidence and feasibility are revisited.
- Multiple LILYGO and Makerfabs cellular boards remain unapproved alternatives.
- Ebyte E220-900M22S is a historical LoRa alternative and not the current plan.
- Bare LLCC68 and LoRaSoC modules remain possible radio implementations but require interface and antenna work.
- RFM95W, CC1101, NRF24L01+, APC220, DX-LR22, and DX-LR32 are historical comparisons or alternative radios, not selected components.
- Sigfox and other LPWAN approaches remain general research areas without approval as project features.

## Dependencies and concerns

- Component documentation and exact datasheets.
- Irish LTE band support for A7670E and network availability.
- 868 MHz regulations and antenna performance.
- GNSS cold-start performance and cellular interference.
- GPIO/SPI availability on the chosen board.
- Peak modem current and battery-voltage stability.
- Device ingress protection and field usability.
- SOS latency and credible delivery semantics.
- 1NCE IoT SIM availability and suitability for Irish use.

## Outstanding idea decisions

- Whether Meshtastic is a required feature or only a research path.
- Whether the final alert should be an SMS, LoRa packet, both, or selected dynamically.
- Whether position is mandatory for every SOS or whether a simple text alert is sufficient.
- Whether solar charging is included in the build or limited to a power analysis.
