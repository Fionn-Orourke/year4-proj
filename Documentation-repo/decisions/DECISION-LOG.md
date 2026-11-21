# Engineering Decision Log

**Status:** Draft and historical decisions only. Accepted status in this log means an evidential direction was recorded, not project-owner approval.

## DEC-001 - Explore LoRa for off-grid emergency communication

- **Date:** Approximate, from initial concept recovery.
- **Context:** The project began by investigating low-power wireless safety communication without full dependence on conventional infrastructure.
- **Options:** conventional cellular only, LoRa, Sigfox, Meshtastic, or hybrid communication.
- **Evidence:** existing broad concept [ideas/Project-Concept.md](../ideas/Project-Concept.md); existing LoRa and network references.
- **Outcome:** LoRa remained an exploratory project direction.
- **Status:** Historical/working direction; unapproved.
- **Consequences:** radio, antenna, range, protocol and regulatory work remain.

## DEC-002 - Investigate Meshtastic compatibility

- **Date:** Initial concept period.
- **Context:** Existing LoRa networks and Meshtastic were identified as potential infrastructure.
- **Options:** custom protocol, Meshtastic integration, or no integration.
- **Outcome:** Meshtastic remained an open investigation.
- **Status:** Awaiting approval and technical verification.
- **Consequences:** cannot assume modules or firmware are compatible.

## DEC-003 - Add LTE/SMS to hiking SOS concept

- **Date:** Approximate from later recovery history; exact week unavailable.
- **Context:** A cellular fallback or alternate delivery path was considered for areas with network coverage.
- **Options:** LoRa only, LTE/SMS only, or hybrid.
- **Outcome:** hybrid LoRa plus LTE concept became the current broad direction.
- **Status:** Working direction; communication priority unresolved; unapproved.

## DEC-004 - Investigate Waveshare ESP32-S3-A7670E-4G

- **Date:** Approximate later project direction; exact date unavailable.
- **Context:** A combined ESP32-S3 and A7670E platform was considered for cellular SMS and controller work.
- **Options:** various LILYGO and Makerfabs boards, custom Nordic route, or the Waveshare board.
- **Evidence:** supplied recovery history only; no hardware datasheet or test evidence in repository.
- **Outcome:** current working cellular/controller direction.
- **Status:** Unverified working direction; no approval.
- **Consequences:** Irish LTE SMS, peak current, GNSS coexistence and GPIO/SPI remain open.

## DEC-005 - Plan Waveshare Core1262-868M for LoRa

- **Date:** Approximate later project direction; exact date unavailable.
- **Context:** The LoRa module needed to support 868 MHz and interface with the selected development platform.
- **Options:** Core1262-868M, E220-900M22S, bare LLCC68, LoRaSoC, RF modules and other historical choices.
- **Outcome:** Core1262-868M became the current planned module.
- **Status:** Working direction; unapproved; E220 remains historical only.
- **Consequences:** electrical interface, antenna, range and Meshtastic compatibility require verification.

## DEC-006 - Keep communication priority unresolved

- **Date:** 19 November 2026 supplied recovery status.
- **Context:** The project does not yet establish whether LoRa or LTE should be attempted first.
- **Outcome:** no priority has been promoted to requirements or Master.
- **Status:** Explicitly awaiting technical and project-owner decision.
- **Consequences:** test plans must cover transport selection and fallback separately.

## DEC-007 - Preserve uncertain and historical records

- **Date:** 19 November 2026 reconstruction.
- **Context:** Available sources conflict or lack exact specifications and dates.
- **Outcome:** contradictions are retained as open uncertainties rather than silently resolved.
- **Status:** Reconstruction policy.
- **Consequences:** higher evidence burden for future approval.
