# LoRa + LTE Hiking SOS Tracker

**Documentation status:** Recovered historical record and proposed specification  
**Governance status:** No content is approved as a Feature Version or Master item

## Purpose and motivation

The project investigates a portable emergency communication device for hikers in remote areas of Ireland. The broad motivation is to improve the chance of sending an SOS or location when conventional mobile coverage is unavailable or unreliable.

The original concept explored a low-power wireless safety system using embedded electronics, LoRa-based communication, and possible Meshtastic infrastructure. It has since developed into a more specific hiking SOS tracker combining LoRa and LTE communication, GNSS position reporting, battery power, an SOS control, and possible solar charging.

## Intended users and use cases

- A hiker using the device alone or with a group.
- A person needing to send an emergency alert from an area with weak or no cellular coverage.
- A recipient able to receive a LoRa message, Meshtastic message, or cellular SMS.
- A development team validating hardware, range, power, and fallback behaviour.

Potential scenarios include activation while off-grid, SMS delivery where LTE is available, position reporting, and relay or network-assisted delivery where LoRa or Meshtastic connectivity exists.

## Current working direction

The current working direction, not an approval, is:

- Main LoRa direction: Waveshare Core1262-868M.
- Working cellular/controller direction: Waveshare ESP32-S3-A7670E-4G.
- GNSS position reporting as part of the tracker concept.
- LTE cellular SMS where supported and available.
- An SOS tactile interface.
- Battery operation, with protected Li-Po or 18650 approaches still under investigation.
- Optional solar charging still under investigation.
- Meshtastic compatibility still under investigation.

The Ebyte E220-900M22S is historical alternative information only. It must not be presented as the current LoRa plan.

## Evolution

1. **Initial concept:** generic wireless safety system with LoRa and possible Meshtastic use.
2. **Application focus:** portable emergency communication for hikers in remote Irish terrain.
3. **Communication expansion:** investigation of LoRa off-grid transport plus LTE/SMS delivery.
4. **Hardware consolidation:** historical comparison of many controllers and radio modules, with the Core1262-868M and ESP32-S3-A7670E-4G as the current working directions.
5. **Documentation reconstruction:** this record separates evidence, proposed directions, historical options, and unresolved decisions.

This chronology is approximate. Existing repository metadata contains inconsistent week/date information and was not used to assign false precision.

## Architecture under investigation

The intended research architecture has three primary communication paths:

- LoRa over 868 MHz to a nearby relay or compatible network.
- LTE cellular SMS for a networked emergency or status message.
- GNSS for position acquisition and inclusion in alerts.

The priority between LoRa and LTE is unresolved. The exact fallback sequence, messaging protocol, acknowledgement behaviour, and recipient workflow require confirmation.

## Historical vs current

- **Historical:** Nordic nRF9151, LILYGO and Makerfabs cellular boards, Ebyte LoRa modules, RF modules, and other options listed in the hardware record.
- **Current working direction:** Waveshare Core1262-868M and Waveshare ESP32-S3-A7670E-4G.
- **Implemented:** repository documentation automation and existing project documentation; no physical hardware implementation is evidenced.
- **Approved:** no project Feature Version or Master configuration is evidenced in the repository.

## Major open decisions

- Communication priority and fallback policy.
- Whether SMS can operate reliably on Irish LTE networks using the A7670E board.
- Whether Meshtastic or a custom LoRa protocol is appropriate.
- Whether simultaneous LTE and LoRa operation is electrically and logically viable.
- Battery chemistry, capacity, protection, and charging architecture.
- Antenna types and interface compatibility.
- Enclosure, ingress protection, and mechanical mounting.
- Acceptance criteria for SOS latency and message delivery.

## Traceability

- Existing concept: [ideas/Project-Concept.md](ideas/Project-Concept.md)
- Idea register: [ideas/IDEAS-REGISTER.md](ideas/IDEAS-REGISTER.md)
- Requirements: [requirements/REQUIREMENTS-DRAFT.md](requirements/REQUIREMENTS-DRAFT.md)
- Hardware: [hardware/HARDWARE-INVESTIGATION.md](hardware/HARDWARE-INVESTIGATION.md)
- Software: [software/SOFTWARE-INVESTIGATION.md](software/SOFTWARE-INVESTIGATION.md)
- Decisions: [decisions/DECISION-LOG.md](decisions/DECISION-LOG.md)
- Risks: [risks/PROBLEM-RISK-REGISTER.md](risks/PROBLEM-RISK-REGISTER.md)
- Tests: [testing/TEST-PLAN.md](testing/TEST-PLAN.md)
- Timeline: [progress/PROJECT-TIMELINE.md](progress/PROJECT-TIMELINE.md)
