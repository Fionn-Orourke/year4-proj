# Test Plan

**Status:** Planned/incomplete. No unperformed test is marked passed.

## TEST-001 - A7670E Irish LTE and SMS test

- **Status:** Planned
- **Objective:** determine whether the A7670E board registers and sends SMS on an identified Irish network/SIM configuration.
- **Hardware:** ESP32-S3-A7670E-4G, suitable PSU or battery, LTE antenna, SIM.
- **Equipment:** serial interface, logging, PSU, current probe, and test SMS recipient.
- **Method:** configure SIM; record registration; send text SMS; record modem responses and timing; repeat in multiple coverage conditions.
- **Expected:** document registration bands and successful SMS delivery or specific failure mode.
- **Acceptance:** to be approved; no pass result until evidence exists.
- **Actual:** not performed.

## TEST-002 - LTE peak current and brownout test

- **Status:** Planned
- **Objective:** measure modem/network peak current and power-stage behaviour.
- **Method:** instrument supply during boot, registration, signal acquisition and SMS transmission.
- **Equipment:** programmable PSU, oscilloscope/current probe or high-speed measurement setup.
- **Acceptance:** voltage and reset-free operation within approved limits; limits not yet established.
- **Actual:** not performed.

## TEST-003 - LoRa range test

- **Status:** Planned
- **Objective:** characterize Core1262-868M range and reliability in Irish terrain.
- **Method:** fixed transmitting and receiving setup; vary separation and terrain; record RSSI, SNR, success and test configuration.
- **Equipment:** two radios, GNSS/position log, battery, map or survey record.
- **Expected:** packet success envelope under recorded conditions.
- **Acceptance:** target distance and success threshold are unresolved.
- **Actual:** not performed.

## TEST-004 - GNSS/cellular coexistence

- **Status:** Planned
- **Objective:** determine whether LTE activity degrades GNSS acquisition or position accuracy.
- **Method:** GNSS-only baseline, LTE-only baseline, then simultaneous operation; compare fix time and NMEA validity.
- **Actual:** not performed.

## TEST-005 - SOS end-to-end latency

- **Status:** Planned
- **Objective:** measure time from activation to LoRa or SMS recipient confirmation.
- **Method:** instrument activation and recipient event; repeat for LoRa and LTE under selected conditions.
- **Acceptance:** target latency requires project-owner confirmation.
- **Actual:** not performed.

## TEST-006 - Battery runtime

- **Status:** Planned
- **Objective:** measure sleep and active-mode runtime for each candidate battery configuration.
- **Equipment:** battery monitor, test load, controlled temperature where practical.
- **Acceptance:** runtime target unresolved.
- **Actual:** not performed.

## TEST-007 - Antenna/interface verification

- **Status:** Planned
- **Objective:** verify connectors, pin mapping and RF continuity for LoRa, LTE and GNSS.
- **Actual:** not performed.

## TEST-008 - Solar charging characterization

- **Status:** Planned
- **Objective:** verify charging voltage/current and battery behaviour if solar is included.
- **Actual:** not performed.

## TEST-009 - False SOS activation

- **Status:** Planned
- **Objective:** determine button guarding and press/hold behavior.
- **Acceptance:** false-activation threshold requires approval.
- **Actual:** not performed.

## Test evidence policy

A test may only be marked Passed or Failed after actual evidence is linked. Existing repository tests are software tests of documentation processors, not hardware or firmware tests for the SOS tracker.
