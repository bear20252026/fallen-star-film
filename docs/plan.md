# Film 2 — The Fallen Star (exactly 60:00)

Same world, same painted watercolor look, same characters as *The Sheep in the Box*. Subtitles in English and Chinese, no voices.

## The one idea
**Light grows when it is shared.** The little star only shines when someone near it laughs or is kind.
Every scene must give the star a little more light, or take some away.

## Characters
- **The Sheep** (whole now, gold-stitched). Brave in small ways. The hero again.
- **The Boy** (the little prince). Kind, a bit stubborn.
- **Pip, the fallen star.** A small star the size of a lemon. It cannot talk, only chime. When it is happy it glows gold; when it is sad it goes grey.
- **The Pilot.** Far away on Earth, every night he looks up at "his" star and laughs. Pip *is* that star.
- **The Rose**, proud and loving, stays home.
- **Moth.** A big, soft, lonely night-moth who lives on a dark planet and is always cold. He takes Pip, then becomes a friend.
- **New planets:** the Clockmaker (never has time), the Cloud (rains because she is lonely; thinks the sheep is a baby cloud).

## ACT ONE — The star falls (0:00 – 15:00)

| # | Scene | Time | Length | What happens |
|---|---|---|---|---|
| 1 | Morning on B612 | 0:00–5:00 | 5:00 | A happy day: watering the rose, sweeping volcanoes, the sheep pulling baobab sprouts. At dusk the boy points out one star: "A friend on Earth looks at that one and laughs." **TITLE.** |
| 2 | The star falls | 5:00–10:00 | 5:00 | That star hiccups, wobbles and falls, landing in the rose's garden. It is Pip, tiny and scared. The sheep makes friends with it. |
| 3 | Grey by tomorrow | 10:00–15:00 | 5:00 | Pip is getting greyer. Through the telescope: the pilot looks up, his star is gone, he stops smiling. They must carry Pip home to its place before it goes out. The box becomes a lantern. Away with the birds. |

## ACT TWO — The journey (15:00 – 45:00)

| # | Scene | Time | Length | What happens |
|---|---|---|---|---|
| 4 | The Quiet | 15:00–20:00 | 5:00 | Flying through deep dark space. Pip fades. The sheep does a silly dance to cheer the boy, Pip giggles and glows. **They discover laughter feeds its light.** |
| 5 | The Clockmaker | 20:00–25:00 | 5:00 | A tiny old man winds a hundred clocks and never stops. The sheep jams one with its tail and he gets one free minute. He watches a sunset and laughs for the first time in years. Pip brightens. |
| 6 | The Cloud | 25:00–30:00 | 5:00 | A planet where it always rains. The lonely Cloud thinks the sheep is a baby cloud. They play, the rain stops, a rainbow. Pip is bright gold. |
| 7 | Moth takes Pip | 30:00–35:00 | 5:00 | In the dark between planets, a huge soft shape swoops and steals the lantern. The birds scatter. The boy and the sheep are alone. |
| 8 | The dark planet | 35:00–40:00 | 5:00 | The sheep goes in alone. Moth is hugging Pip to stay warm, but Moth is sad so Pip is fading. The sheep is not angry: it snuggles Moth in its wool. Moth laughs (it tickles). Moth gives Pip back and joins them. |
| 9 | The meteor storm | 40:00–45:00 | 5:00 | A storm of rocks. They protect Pip, but Pip goes completely dark. In the silence they tell each other their happiest memories, laughing through tears. A flicker. Pip is alive. |

## ACT THREE — Home (45:00 – 60:00)

| # | Scene | Time | Length | What happens |
|---|---|---|---|---|
| 10 | The star stairs | 45:00–50:00 | 5:00 | Moth carries them up a staircase of stars to the empty place in the sky. They put Pip back. It is still faint. |
| 11 | The pilot laughs | 50:00–54:30 | 4:30 | On Earth, the pilot looks up and sees his star, faint but there. He laughs out loud. The laugh rises all the way up; Pip blazes, and all the stars laugh with him. |
| 12 | Home | 54:30–58:40 | 4:10 | Dawn on B612. Moth now lives nearby as a night lamp, warm at last. The rose, the boy, the sheep asleep. Pip winks from the sky. **The End.** |
| 13 | Credits | 58:40–60:00 | 1:20 | Painted moments, pencil to watercolor, like film 1. |

**Total: 60:00.** Each scene's code uses a fixed length (DURATION) so the final film really is 60 minutes. Lesson from film 1: it was planned for 60 and came out 45.

## How it is made
- Remotion + GSAP, 24 fps, 1920×804, the same project and planetkit as film 1.
- Every background is a painted plate (watercolor, paper grain). New planets get new painted plates made from the film-1 art, never flat code colors.
- Fast render: swiftshader + 3 workers, 30-second chunks that survive restarts.
- Delivered in parts under 450 MB (bigger files don't sync), plus one smaller whole-film file.
