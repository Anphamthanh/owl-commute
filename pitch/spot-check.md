# Spot check of the vision model on Friday morning frames

Labeler: the AI assistant that built the app, by eye, on a contact sheet. This is a first pass, not an independent human
label. A human pass with `/label` replaces it when there is time. Sample: 20 camera frames from Fri Nov 20, 2026,
6:44 to 8:00 AM: the model flagged 48 frames as heavy, stopped, or incident out of 595 reads; 10 of those flagged frames
and 10 unflagged frames were drawn at random (seed 7).

| # | Time | Camera | Model said | By eye | Slow vs not slow | Incident call held up |
|---|---|---|---|---|---|---|
| 1 | 7:35 | Frey Rd at Skip Spann | moderate, emergency vehicle (0.7) | fog, a few cars at the light, no emergency lights visible | agree | no |
| 2 | 7:25 | I-75 S past Roswell | heavy, none (0.9) | packed main lanes, express lanes clear | agree | n/a |
| 3 | 6:46 | Busbee Pkwy at Frey | free flow, debris (0.8) | empty intersection, a light patch on the pavement, not clearly debris | agree | no |
| 4 | 6:46 | I-75 S at Chastain | heavy, emergency vehicle (0.85) | dense tail lights, heavy plausible, no flashing lights visible | agree | no |
| 5 | 6:44 | Busbee Pkwy at Frey | free flow, debris (0.8) | same as 3 | agree | no |
| 6 | 8:00 | Frey Rd at Skip Spann | moderate, emergency vehicle (0.6) | fog, one SUV turning, nothing else visible | agree | no |
| 7 | 6:44 | I-75 N past Chastain | heavy, emergency vehicle (0.7) | glare, many tail lights, heavy plausible, no emergency lights visible | agree | no |
| 8 | 6:48 | Busbee Pkwy at Frey | free flow, debris (0.8) | same as 3 | agree | no |
| 9 | 7:23 | Frey Rd at Skip Spann | moderate, emergency vehicle (0.7) | fog, cars at the light, no emergency lights visible | agree | no |
| 10 | 7:29 | I-75 S past Roswell | heavy, none (0.9) | packed main lanes | agree | n/a |
| 11 | 8:00 | Frey Rd at Campus Loop | free flow, none (0.9) | a few cars, moving | agree | n/a |
| 12 | 6:46 | Chastain Rd at Busbee | free flow, none (0.8) | dark, little traffic | agree | n/a |
| 13 | 6:53 | I-75 S past Frey | free flow, none (0.9) | fog, few cars | agree | n/a |
| 14 | 7:23 | I-75 N before Chastain | free flow, none (0.95) | moderate traffic, moving | agree | n/a |
| 15 | 6:44 | I-75 S past Frey | free flow, none (0.7) | dark and glare, little visible | agree | n/a |
| 16 | 7:43 | I-75 N past Chastain | free flow, none (0.95) | light traffic | agree | n/a |
| 17 | 7:13 | Busbee Pkwy at Frey | free flow, none (0.95) | empty | agree | n/a |
| 18 | 7:45 | I-75 S at Chastain | free flow, none (0.9) | light traffic | agree | n/a |
| 19 | 6:46 | I-75 N before Chastain | moderate, none (0.8) | dense headlights, moderate to heavy | agree | n/a |
| 20 | 7:31 | Chastain Rd at Big Shanty | free flow, none (0.95) | one SUV | agree | n/a |

## Counts

- Slow vs not slow (heavy or stopped vs free flow or moderate): 20 of 20 agree.
- Exact congestion level: 18 of 20 (frames 1 and 6 look like free flow rather than moderate in fog).
- Incident calls: the model called an incident in 8 of the 20 frames. 0 of 8 were clearly visible by eye. In the 12 frames
  with no incident call, none was visible either, so yes/no agreement is 12 of 20.
- The Frey Rd "crash" the model reported from 7:37 to 7:50 AM (7 consecutive frames, confidence 0.8 to 0.85) is not
  verifiable in the fog. Two-frame confirmation did not catch it because the misread persisted. This is a known limit.

## What this means for the app

Road delay from congestion is trustworthy enough to add minutes. Incident calls at night or in fog are not, so the next
version should either require daylight and confidence above 0.85 for incidents, or treat an incident call as a note
("watch for an incident") rather than minutes.
