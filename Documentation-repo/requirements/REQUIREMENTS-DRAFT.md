# Recovered Requirements Draft

**Status:** Draft recovery only. These requirements have not been approved and are not part of a Feature Version or Master.

## Functional requirements

| ID | Requirement | Evidence/origin | Acceptance criterion | Status |
|---|---|---|---|---|
| REQ-001 | The device shall provide a user-operable SOS activation method. | Recovery history; hiking SOS concept | Press/hold behaviour and false-trigger limits need confirmation. | Draft |
| REQ-002 | The device shall attempt to transmit emergency information through LoRa. | LoRa part of project concept | Exact range and success threshold need testing. | Draft |
| REQ-003 | The device shall investigate LTE cellular SMS delivery. | Current cellular board direction | SMS must be delivered on at least an identified Irish test network or a limitation recorded. | Not verified |
| REQ-004 | The device shall obtain or include GNSS position in an alert where available. | Recovery history | Accuracy, fix timeout and fallback text require confirmation. | Draft |
| REQ-005 | The device shall provide local feedback to indicate activation and communication state. | Proposed user interface | Feedback states and alarm behavior need confirmation. | Draft |
| REQ-006 | The device shall support a fallback or selection policy between LoRa and LTE. | Broad concept | Priority and fallback rules are unresolved. | Draft |
| REQ-007 | The device may support Meshtastic-compatible operation. | Existing concept mentions Meshtastic | Compatibility and feature scope remain unverified. | Idea |
| REQ-008 | The device may support solar charging. | Recovery history | Charging behavior and power benefit require testing. | Idea |

## Hardware requirements

| ID | Requirement | Acceptance/verification need | Status |
|---|---|---|---|
| HWR-001 | The current working LoRa platform shall be the 868 MHz-capable Core1262-868M unless changed by an approved decision. | Datasheet, interface and RF test verification. | Working direction only |
| HWR-002 | The working cellular platform shall be the ESP32-S3-A7670E-4G unless changed by an approved decision. | Irish LTE and SMS verification required. | Working direction only |
| HWR-003 | The device shall use an antenna arrangement compatible with each RF interface. | Connector, impedance and radiation tests. | Draft |
| HWR-004 | The battery system shall supply LTE peak current without reset or brownout. | Oscilloscope/logging and measured peak demand. | Draft |
| HWR-005 | The enclosure shall protect field hardware from environmental exposure. | Target ingress rating and test plan not confirmed. | Draft |

## Non-functional requirements

- **Power:** battery lifetime target is unknown and remains to be agreed.
- **Latency:** maximum SOS delivery latency is unknown.
- **Reliability:** delivery confirmation, retry and failure behaviour need measurable criteria.
- **Range:** LoRa range in Irish terrain is unverified.
- **Portability:** target dimensions and mass are unknown.
- **Environmental:** operating temperature, rain exposure and impact targets are unknown.
- **Safety:** false SOS protection and explicit test-only operation are needed but not approved.
- **Maintainability:** firmware and message formats should be traceable and updateable; criterion is not yet defined.

## Communication requirements

- 868 MHz LoRa operation and antenna compliance remain under investigation.
- LTE operation is limited by network, modem bands and SIM configuration.
- GNSS availability is expected to be variable and must not block emergency transport indefinitely.
- No requirement may assume simultaneous LTE and LoRa operation until measured.

## Requirements requiring confirmation

- exact intended recipients;
- LoRa versus LTE priority;
- maximum alert latency;
- minimum LoRa range;
- minimum battery runtime;
- location accuracy;
- SMS confirmation requirements;
- Meshtastic inclusion;
- solar charging inclusion;
- ingress protection rating;
- acceptable false-activation rate;
- test network and SIM conditions.

## Change history

- Initial concept was generic LoRa/Meshtastic safety communication.
- Specific hiking SOS and LTE/SMS directions were recovered from supplied project history.
- Core1262-868M and ESP32-S3-A7670E-4G are recorded as working directions, not approvals.
- No contradicted original requirement was silently resolved; unresolved items are listed above.
