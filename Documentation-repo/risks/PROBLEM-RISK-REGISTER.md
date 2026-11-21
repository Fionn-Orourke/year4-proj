# Problems and Risk Register

**Status:** Recovered risks and known unknowns. Resolutions are only recorded when supported by evidence.

| ID | Area | Risk/problem | Evidence | Consequence | Status/response |
|---|---|---|---|---|---|
| PR-001 | Cellular | A7670E LTE SMS on Irish networks is unverified | Supplied recovery history | SOS SMS may fail or be unavailable | Test with identified network/SIM; no resolution |
| PR-002 | Cellular | 1NCE/SIM configuration and coverage uncertain | Historical SIM consideration | SMS and LTE registration may differ by carrier | Verify SIM terms and test registration |
| PR-003 | GNSS | GNSS and cellular coexistence is untested | Supplied recovery history | RF or firmware interference may degrade position | Measure separately and combined |
| PR-004 | Latency | SOS delivery latency is unknown | No physical tests | Safety claims cannot be quantified | Define target and time end-to-end |
| PR-005 | GPIO | Available GPIO/SPI pins are unknown | Board pinout not retained | Radio integration may conflict with cellular/GNSS | Verify schematic and pinout |
| PR-006 | Electrical | LTE peak current may exceed supply or battery capability | Cellular modules generally draw high pulses, exact board profile unknown | Brownouts/reset or battery damage | Measure supply during network activity |
| PR-007 | Battery | Candidate Li-Po/18650 suitability is unresolved | Candidate capacities only | Poor runtime or unsafe operation | Confirm protection, charger and discharge rating |
| PR-008 | Antenna | Cellular, GNSS and LoRa antenna compatibility is unresolved | Connector/interface uncertainty | Range and network performance may be poor | Verify connectors, impedance and placements |
| PR-009 | RF | LoRa range in Irish terrain is unverified | No field tests | Emergency communication may be unreliable | Terrain range tests and coverage model |
| PR-010 | RF | Simultaneous LTE and LoRa operation is unverified | No implementation evidence | EMI or current overload | Bench test transport combinations |
| PR-011 | Software | Meshtastic compatibility is unknown | Existing concept only | Integration may require different firmware or hardware | Research exact Core1262 and Meshtastic support |
| PR-012 | Power | Solar charging behavior is unknown | Solar is a possibility only | Charging may be insufficient or unsafe | Characterize panel/regulator/battery |
| PR-013 | Environmental | Enclosure sealing and RF feedthrough are unresolved | IP65 is a concept | Damage or antenna degradation | Require enclosure and ingress tests |
| PR-014 | UI | SOS false activation | Tactile button idea | Accidental alerts | Press-and-hold or guarded mechanism to investigate |
| PR-015 | Timeline | Component availability and lead times | Not evidenced historically | Build cannot start or may substitute hardware | Check supplier availability and pin-compatible alternates |
| PR-016 | Evidence | Repository metadata uses approximate dates/weeks inconsistently | Git/activity and supplied recovery conflict | False chronology could distort history | Preserve approximate order and source |
| PR-017 | Scope | Hardware/software claims may be mistaken for approval | Draft governance exists | Unapproved choices could be built or documented as final | Keep Ideas/Drafts labels and approval prompts |
| PR-018 | Testing | No physical hardware tests have been completed | Supplied recovery history | No pass status can be claimed | Keep all plans unperformed |

## Problem resolutions

No project technical resolution is recorded as verified in the available evidence. Documentation reconstruction itself resolved the immediate governance and traceability gap for generated records by separating historical automation commits from project activity.
