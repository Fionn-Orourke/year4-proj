# Hardware Investigation Record

**Status:** Draft evidence and comparison. No component is approved for a Feature Version or Master.

## Comparison fields

For each component: exact name, evidence status, advantages, disadvantages, compatibility, selection history, and remaining questions.

## Controllers and cellular boards

### Nordic nRF9151 with MDBT50Q-U1MV2, custom PCB
- **Status:** Historical option.
- **Use case:** cellular IoT controller and cellular modem route with custom RF and carrier board work.
- **Potential advantages:** purpose-built cellular and GNSS integration, custom PCB control.
- **Potential disadvantages:** added PCB design and RF/antenna/DFM complexity; not evidenced as selected or built.
- **Compatibility:** unknown until exact MDBT module datasheet, antenna interface, and RF routing are reviewed.
- **Reason considered:** investigated as an integrated cellular/GNSS route.
- **Reason not current:** current project direction moved to a combined Waveshare ESP32-S3 board; no supported selection or rejection rationale is preserved for nRF9151.
- **Remaining:** exact model revision, LTE bands, GNSS support, current consumption, Irish network compatibility, PCB requirements.

### LILYGO T-SIM7080G-S3
- **Status:** Historical alternative.
- **Potential advantages:** combined ESP32-S3 and cellular platform.
- **Disadvantages:** exact antenna, power, GNSS, and Irish LTE compatibility are not evidenced.
- **Reason considered:** cellular/SMS board option.
- **Reason not current:** no confirmed evidence of selection or rejection. Replaced or deferred by current working direction in the supplied history.

### LILYGO T-SIM7600X-S3
- **Status:** Historical alternative.
- **Potential advantages:** LTE modem integration.
- **Disadvantages:** board variant, LTE bands, power demand, GNSS coexistence, and availability are not established.
- **Reason considered:** cellular/SMS board option.
- **Reason not current:** no documented selection or rejection reason beyond direction change.

### LILYGO T-SIM7000G-S3
- **Status:** Historical alternative.
- **Potential advantages:** cellular modem and ESP32-S3 integration.
- **Disadvantages:** exact network and band suitability are unknown; LTE/SMS behaviour is not evidenced.
- **Reason considered:** low-power cellular board route.
- **Reason not current:** no confirmed test or selection rationale preserved.

### Waveshare ESP32-S3-A7670E-4G
- **Status:** Current working direction, unapproved and unverified.
- **Potential advantages:** ESP32-S3 development, integrated A7670E cellular platform, direct GNSS and SMS investigation.
- **Disadvantages:** SMS support on Irish networks is unverified; LTE peak current, GNSS coexistence, GPIO/SPI, antenna and battery interface require measurement and datasheet confirmation.
- **Reason considered:** practical combined controller and cellular platform.
- **Reason not evidenced/selected:** no Master or Feature Version approval and no physical test evidence.
- **Remaining:** exact carrier-board revision, LTE bands, SMS process, antenna options, GNSS, supply limits, pinout and peak current.

### Makerfabs ESP32S3 A7670X
- **Status:** Historical alternative.
- **Use:** ESP32-S3 with A7670-series modem.
- **No supported specifications or rejection rationale are retained.**

### Makerfabs ESP32S3 SIM7670G
- **Status:** Historical alternative.
- **Use:** ESP32-S3 with SIM7670G modem.
- **No supported specifications or rejection rationale are retained.**

### Waveshare SIM7670G-4G
- **Status:** Historical alternative.
- **Use:** cellular board/modem option.
- **No evidence of approval, testing or exact rejection rationale is retained.**

### LILYGO T-A7670X-S3
- **Status:** Historical alternative.
- **Use:** ESP32-S3 with A7670X modem.
- **No evidence of approval, testing or exact rejection rationale is retained.**

### T-Internet-COM and T-Beam Supreme
- **Status:** Historical alternatives.
- **T-Internet-COM:** exact hardware variant and comparison evidence are not established.
- **T-Beam Supreme:** combined ESP32, LoRa and GNSS board family investigated as a possible platform; exact result and replacement reason are not evidenced.

## LoRa modules

- **Waveshare Core1262-868M:** current planned LoRa module. Exact interface, antenna connector, power, pin mapping and Meshtastic compatibility remain to be verified. Unapproved.
- **Ebyte E220-900M22S:** historical 900 MHz alternative. It must not be described as current. Reasons for original consideration or replacement are not preserved with evidence.
- **HJ-68LR(68)_P800:** historical LoRa module investigation; exact specification, use and rejection rationale are unverified.
- **Bare LLCC68:** historical low-level radio direction; requires SPI, RF matching, antenna, regulatory and software design. No build evidence retained.
- **MS21SF1-3N68AIR:** historical module investigation; exact manufacturer, radio, antenna and pin details need verification.
- **MS21SF1-3N62AIR:** historical module investigation; exact details need verification.
- **LAMBDA68-8D:** historical module investigation; exact details need verification.
- **RFM95W:** historical SX1276-class radio comparison; 868 MHz suitability and level-shift/interface compatibility are unknown.
- **CC1101:** historical sub-GHz transceiver alternative; not a LoRa modem unless explicitly used with a compatible protocol stack; exact purpose unknown.
- **NRF24L01+:** historical 2.4 GHz alternative, unsuitable for 868 MHz LoRa use by implication but no rejection evidence is preserved.
- **APC220:** historical sub-GHz radio alternative; protocol and module details need confirmation.
- **DX-LR22 and DX-LR32:** historical LoRa radio alternatives; exact frequency and variant require datasheet confirmation.

## Positioning

- **GNSS:** required for planned position reporting but exact antenna, update mode, power profile and coexistence with LTE remain unverified.
- **GNSS antenna:** external or onboard active antenna options are unknown.
- **Cellular antenna:** exact gain, connector and location are unknown for the current board.
- **LoRa antenna:** 868 MHz antenna and matching are required; connector may be U.FL/IPEX or SMA depending on module.

## Power and mechanical components

- **Li-Po 2000 mAh:** considered as candidate. Capacity is potentially suitable but exact size, discharge rate, protection and charging compatibility are unknown.
- **Protected 18650 3000 mAh:** considered. Requires appropriate holder, protection, charger and mechanical current margin; suitability is unverified.
- **Solar panels:** potential extension. Charging regulator, voltage, panel current and worst-case behaviour are unknown; no hardware test evidence exists.
- **IP65 enclosures:** potential requirement for field use. Exact dimensions, RF antenna feedthrough, seals and thermal/power effects remain unknown.
- **SOS tactile switches:** exact force, travel, sealing and guarding remain to be selected.
- **1NCE IoT SIM:** historical/possible cellular access option. Irish network availability, IoT SIM roaming, data/SMS policy and A7670E compatibility remain unverified.

## Interface uncertainty

- Available GPIO and SPI pins are unresolved for the final cellular/LoRa/GNSS combination.
- U.FL/IPEX-to-SMA adapters or pigtails may be needed, but exact radio connector polarity and grounding require datasheet confirmation.
- LTE peak current and transient supply are unresolved; practical test equipment and a robust power stage are required.
- Simultaneous LTE and LoRa operation requires timing, power and RF isolation investigation.

## Hardware evidence needs

- Manufacturer datasheets and carrier-board schematics.
- Pinout tables.
- LTE band and GNSS specifications.
- Antenna requirements and connector drawings.
- Absolute maximum voltage and peak current values.
- Physical interface measurements and photographs.
- Thermal, RF and battery test data.
