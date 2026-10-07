# Seedance 2.5 Prompt Playbook: 20 fixes, each with a before and after prompt

Twenty techniques for Seedance 2.5 prompts that do what you meant. Each play names a symptom, shows a weak prompt and its rewrite, says what changed, and gives the settings and cost to A/B-test both versions yourself.

[The plays](#the-plays) · [A/B test a play](#ab-test-a-play) · [What testing costs](#what-testing-costs) · [plays.json](./plays.json) · [FAQ](#faq)

<sub>Last checked: 2026-10-07 against the Seedance 2.5 model page, the API docs and BytePlus's Seedance 2.5 prompt guide.</sub>

The rewrites follow the structure in BytePlus's official Seedance 2.5 prompt guide and the request rules of the `/v1/videos` API. Where a play comes straight from that guide, its **Source** line says which section. The prompts themselves are written for this repo.

## The shape a good prompt ends up with

```text
[Who] [does what] [where], [style].                   <- one sentence, first
[0-4s] [shot size], [camera move]: [action]            <- a timeline once there is more than one beat
[4-8s] ...
Name (emotion): "line"                                 <- each line quoted once
Sound: [ambience], [effects], [voices]; no [what you don't want]
Keep [what must not change]. No subtitles.
```

BytePlus's guide describes the same order: a one-sentence summary (subject, location, event, style, camera), then the detailed plot by timestamp or shot, then notes on what stays consistent, with negative wording kept for subtitles and audio. Each play below repairs one part of it, or of the request around it.

## The plays

| # | Play | Symptom it fixes | Test both versions |
|---:|---|---|---:|
| 1 | [Lead with who does what](#1-lead-with-who-does-what) | The clip looks generic and the main subject is vague or missing. | $1.05 |
| 2 | [One camera move per shot](#2-one-camera-move-per-shot) | The camera wanders, jitters or ends up somewhere you did not plan. | $0.87 |
| 3 | [Name the light: source, side and color](#3-name-the-light-source-side-and-color) | Flat, evenly lit footage with no mood. | $1.05 |
| 4 | [Show feelings through actions](#4-show-feelings-through-actions) | Faces are over-acted, or nothing visible happens at all. | $1.40 |
| 5 | [Keep strong emotion from turning into glowing eyes](#5-keep-strong-emotion-from-turning-into-glowing-eyes) | Eyes glow blue or red when a character is angry, shocked or ecstatic. | $0.87 |
| 6 | [Timestamps in whole seconds, with no gaps](#6-timestamps-in-whole-seconds-with-no-gaps) | Events happen in the wrong order, or one of them is skipped. | $1.75 |
| 7 | [Budget the story to the seconds you have](#7-budget-the-story-to-the-seconds-you-have) | A long story in a short clip comes out as a blur of cuts, or half of it is missing. | $0.87 |
| 8 | [Write dialogue as Name (emotion): "line"](#8-write-dialogue-as-name-emotion-line) | Lines come out garbled or doubled, or subtitles get burned in. | $1.40 |
| 9 | [Name the sound you want, and every sound you don't](#9-name-the-sound-you-want-and-every-sound-you-dont) | Background music shows up even though the prompt said 'no music'. | $1.05 |
| 10 | [Spell on-screen text letter by letter](#10-spell-on-screen-text-letter-by-letter) | Signs and titles come out misspelled. | $0.87 |
| 11 | [Give every reference a role](#11-give-every-reference-a-role) | Assets get mixed up: the wrong face, the wrong pet, or a song used as a voice. | $1.40 |
| 12 | [Upload characters in the order they appear](#12-upload-characters-in-the-order-they-appear) | Two characters swap faces, or the first person on screen gets the wrong identity. | $1.40 |
| 13 | [Take only the part of a reference you need](#13-take-only-the-part-of-a-reference-you-need) | People, places or sound from a reference clip leak into the new video. | $1.92 |
| 14 | [Edits: say what changes and what stays](#14-edits-say-what-changes-and-what-stays) | A vague edit changes too much, or nothing at all. | $2.10 |
| 15 | [Edits: confine the change to a time range](#15-edits-confine-the-change-to-a-time-range) | An edit meant for one moment alters the whole clip. | $2.80 |
| 16 | [First frame: describe the motion, not the picture](#16-first-frame-describe-the-motion-not-the-picture) | The first frame gets reinterpreted instead of animated. | $0.87 |
| 17 | [First and last frame: give the transition a path](#17-first-and-last-frame-give-the-transition-a-path) | The two frames melt into each other with no sense of how one became the other. | $1.40 |
| 18 | [Declare keyframes when the order must hold](#18-declare-keyframes-when-the-order-must-hold) | Storyboard images are used out of order, or only loosely. | $2.10 |
| 19 | [Stage in depth for vertical 9:16](#19-stage-in-depth-for-vertical-916) | In a tall frame, subjects are cut off at the sides or shrink to dots. | $1.05 |
| 20 | [Make a clip that loops](#20-make-a-clip-that-loops) | A clip meant to loop jumps at the seam. | $0.87 |

### 1. Lead with who does what

**Symptom:** The clip looks generic and the main subject is vague or missing.

**Before**

```text
Cinematic, breathtaking, ultra-detailed, award-winning, dramatic lighting, 8K, masterpiece: a lighthouse in a storm.
```

**After**

```text
A lighthouse keeper in a yellow oilskin climbs the iron stairs on the outside of a lighthouse while storm waves explode on the rocks below. Wide shot from the sea, the camera rising and falling with the swell. Gray dusk light, the lamp's beam sweeping overhead. Sound: howling wind, crashing surf, boots on metal steps.
```

**What changed**

- The first sentence says who, where and what happens.
- The quality words (cinematic, 8K, masterpiece) are gone: there is nothing in them to render.
- Camera, light and sound each get one concrete line.

**Test it:** `python ab.py run 1` · text-to-video · 6 s · 480p · 16:9 · $1.05 for both versions

**Source:** BytePlus prompt guide, basic techniques: a one-sentence summary of subject, location, event, style and camera movement.

### 2. One camera move per shot

**Symptom:** The camera wanders, jitters or ends up somewhere you did not plan.

**Before**

```text
A pastry chef plates a dessert while the camera zooms in, pans left, orbits around her, tilts up to the ceiling and cranes back down with a dolly zoom.
```

**After**

```text
A pastry chef sets a single raspberry on a chocolate tart with tweezers. Slow push-in from a medium shot to a close-up of her hands; nothing else in the shot moves. Warm light from the kitchen pass. Sound: a soft clink and quiet kitchen ambience.
```

**What changed**

- Five competing moves become one: a slow push-in.
- When a shot really needs two moves, give each its own time range (play 6).

**Test it:** `python ab.py run 2` · text-to-video · 5 s · 480p · 16:9 · $0.87 for both versions

### 3. Name the light: source, side and color

**Symptom:** Flat, evenly lit footage with no mood.

**Before**

```text
A woman reading a book in a cozy room with nice lighting and a good atmosphere.
```

**After**

```text
A woman reads in an armchair beside a rain-streaked window at dusk. The only light is a brass floor lamp on her left, throwing warm yellow light across the pages and leaving the room behind her in deep blue shadow. Static medium shot. Sound: rain on the glass and a page turning.
```

**What changed**

- 'Nice lighting' becomes a source (a floor lamp), a side (her left) and a color (warm yellow against blue).
- The shadow side is described too; the contrast between the two is the mood.

**Test it:** `python ab.py run 3` · text-to-video · 6 s · 480p · 16:9 · $1.05 for both versions

### 4. Show feelings through actions

**Symptom:** Faces are over-acted, or nothing visible happens at all.

**Before**

```text
A very sad, lonely old man feeling nostalgic and heartbroken about the past.
```

**After**

```text
An old man sitting alone at a kitchen table turns a wedding ring slowly between his fingers, sets it down beside a cold cup of tea and looks at the empty chair across from him. Close-up on his hands, then a medium shot. Gray morning light from the window. Sound: a ticking clock.
```

**What changed**

- Four feeling words become three small actions the camera can see.
- The setting (a cold cup, an empty chair) carries the rest of the story.

**Test it:** `python ab.py run 4` · text-to-video · 8 s · 480p · 16:9 · $1.40 for both versions

**Source:** BytePlus prompt guide, advanced techniques: describe expressions in plain descriptive sentences rather than idioms.

### 5. Keep strong emotion from turning into glowing eyes

**Symptom:** Eyes glow blue or red when a character is angry, shocked or ecstatic.

**Before**

```text
An extremely furious, fanatical football coach screams at the referee with burning, demonic eyes.
```

**After**

```text
A football coach in a rain-soaked jacket shouts at the referee from the touchline, jaw clenched, pointing at the pitch. Normal human eyes, no glowing eyes. Medium close-up, floodlights behind him and rain in the light. Sound: his hoarse shouting and the roar of the crowd.
```

**What changed**

- The extreme words (furious, fanatical, demonic, burning) are replaced by visible behavior.
- 'Normal human eyes, no glowing eyes' is stated as a constraint.

**Test it:** `python ab.py run 5` · text-to-video · 5 s · 480p · 16:9 · $0.87 for both versions

**Source:** BytePlus prompt guide, FAQ 'Overreaction to emotional cues: Glowing eyes'.

### 6. Timestamps in whole seconds, with no gaps

**Symptom:** Events happen in the wrong order, or one of them is skipped.

**Before**

```text
First the kettle boils, then she pours the tea, later she drinks it by the window and smiles, and finally the sun comes up.
```

**After**

```text
[0-3s] Close-up: a copper kettle on a gas flame starts to whistle.
[3-6s] Medium shot: she pours the water over loose tea in a glass pot, and the leaves unfurl.
[6-10s] She sits by the window with the cup, takes a sip and smiles as the sunrise reaches her face.
Sound: the whistle, pouring water, birds outside.
```

**What changed**

- Each event gets a range in whole seconds, and the ranges run from 0 to 10 with no gap or overlap, matching duration 10.
- Seedance 2.5 follows integer-second timestamps; Seedance 2.0 follows shot numbers only.

**Test it:** `python ab.py run 6` · text-to-video · 10 s · 480p · 16:9 · $1.75 for both versions

**Source:** BytePlus prompt guide, 'Timestamps' and 'Differences from Seedance 2.0'.

### 7. Budget the story to the seconds you have

**Symptom:** A long story in a short clip comes out as a blur of cuts, or half of it is missing.

**Before**

```text
A knight saddles his horse, rides through a dark forest, fights a dragon, rescues a princess from a tower and rides home at sunset.
```

**After**

```text
A knight in dented armor swings up into the saddle of a gray horse in a misty courtyard at dawn, gathers the reins and looks toward the open gate. Medium shot, slow push-in. Sound: armor clanking and the horse snorting.
```

**What changed**

- Five scenes in five seconds become one beat that fits.
- For the whole story, use up to 30 seconds with a timeline (play 6), or render it as several clips.

**Test it:** `python ab.py run 7` · text-to-video · 5 s · 480p · 16:9 · $0.87 for both versions

**Source:** BytePlus prompt guide, 'Timestamps': too much content in one range can cause excessive cuts or omitted plot.

### 8. Write dialogue as Name (emotion): "line"

**Symptom:** Lines come out garbled or doubled, or subtitles get burned in.

**Before**

```text
The girl nervously says hi and then she says that she missed him so much, she is crying with tears, very emotional, I missed you so much.
```

**After**

```text
At an airport arrivals gate, a girl sees her brother and walks up to him.
Girl (nervous, quiet): "Hi."
She hugs him.
Girl (tearful, laughing): "I missed you so much."
Medium two-shot, handheld. Sound: terminal announcements and rolling suitcases. No subtitles.
```

**What changed**

- Each line is quoted once, with its delivery in parentheses.
- No words of a line are repeated in the stage directions.

**Test it:** `python ab.py run 8` · text-to-video · 8 s · 480p · 9:16 · $1.40 for both versions

**Source:** BytePlus prompt guide, FAQ 'Subtitles generated despite prompt constraints'.

### 9. Name the sound you want, and every sound you don't

**Symptom:** Background music shows up even though the prompt said 'no music'.

**Before**

```text
A blacksmith works in his forge. No music.
```

**After**

```text
No music, no background score, no melody, no instrumental of any kind. A blacksmith hammers a glowing horseshoe on an anvil, sparks flying, then plunges it into a bucket of water in a burst of steam. Close-up, firelight. Sound: ringing hammer strikes, the roar of the bellows, a sharp hiss of steam. Again: no music, BGM or score.
```

**What changed**

- The sounds you do want are listed one by one.
- Every word for music is excluded, at the start and again at the end.

**Test it:** `python ab.py run 9` · text-to-video · 6 s · 480p · 16:9 · $1.05 for both versions

**Source:** BytePlus prompt guide, FAQ 'Background music generated despite "no BGM"'.

### 10. Spell on-screen text letter by letter

**Symptom:** Signs and titles come out misspelled.

**Before**

```text
A neon sign that says OPEN LATE flickers on in a diner window.
```

**After**

```text
A neon sign in a diner window flickers on. The red neon letters light up one at a time in this order: O, P, E, N, then L, A, T, E, spelling "OPEN LATE". Static shot from the street through rain on the glass. Sound: neon buzz and rain.
```

**What changed**

- The words are broken into letters that appear in sequence.
- For longer text, the other fix is to supply the exact text as a reference image and point to it.

**Test it:** `python ab.py run 10` · text-to-video · 5 s · 480p · 16:9 · $0.87 for both versions

**Source:** BytePlus prompt guide, FAQ 'Text spelling errors'.

### 11. Give every reference a role

**Symptom:** Assets get mixed up: the wrong face, the wrong pet, or a song used as a voice.

**Before**

```text
Make a video with these pictures and this song: a man and a dog on a beach.
```

**After**

```text
@Image 1 is the man and @Image 2 is his dog. Follow the tempo and mood of @Audio 1 for the music. The man throws a stick into the surf and the dog sprints after it, splashing through the waves; the man laughs and jogs after them. Wide tracking shot along the waterline, late-afternoon sun. Sound: waves, barking, and music in the style of @Audio 1.
```

**What changed**

- Each asset is named by its number and bound to one role in the first two sentences.
- Every reference is used either way; naming tells the model which one is which.

**Test it:** `python ab.py run 11` · reference · 8 s · 480p · 16:9 · $1.40 for both versions

**Source:** BytePlus prompt guide, 'Reference tasks (multi-asset mapping)'.

### 12. Upload characters in the order they appear

**Symptom:** Two characters swap faces, or the first person on screen gets the wrong identity.

**Before**

```text
Marcus walks into the dark office first and switches on the desk lamp. Vera steps out of the shadow behind him and says: "You're late." He freezes.
```

**After**

```text
@Image 1 is Marcus, who appears first. @Image 2 is Vera. Marcus walks into the dark office and switches on the desk lamp. Vera steps out of the shadow behind him; he freezes.
Vera (cold, quiet): "You're late."
Medium shot, then a close-up of Marcus. Sound: footsteps and the click of the lamp. No subtitles.
```

**What changed**

- The images are reordered so @Image 1 is the first person on screen.
- Each name is tied to an image number; the before prompt never says which image is whom.

**Test it:** `python ab.py run 12` · reference · 8 s · 480p · 16:9 · $1.40 for both versions

**Source:** BytePlus prompt guide, FAQ 'Incorrect character-to-reference mapping'.

### 13. Take only the part of a reference you need

**Symptom:** People, places or sound from a reference clip leak into the new video.

**Before**

```text
Make a video like @Video 1 but with a ginger cat.
```

**After**

```text
Refer only to the camera path in @Video 1, a slow low orbit; ignore its people, setting and sound. A ginger cat sits on a sunny windowsill watching birds outside while the camera orbits it. Soft morning light, potted herbs on the sill. Sound: birdsong and a quiet purr.
```

**What changed**

- The prompt says which part of @Video 1 to take (the camera path) and which parts to ignore.
- Reference video seconds are billed, so trim the clip to the move itself.

**Test it:** `python ab.py run 13` · reference · 6 s + 5 s reference video each · 480p · 16:9 · $1.92 for both versions

**Source:** BytePlus prompt guide, 'Reference tasks': state which part of an asset to reference.

### 14. Edits: say what changes and what stays

**Symptom:** A vague edit changes too much, or nothing at all.

**Before**

```text
Make it look better and more cinematic.
```

**After**

```text
Change only the color grade: warm teal-and-orange film tones with slightly deeper blacks. Keep every person, object, movement, camera move and sound exactly as they are.
```

**What changed**

- The change is one specific thing, the grade, described as a target look.
- Everything that must stay is listed, which gives the edit a boundary.

**Test it:** `python ab.py run 14` · video edit · 6 s source, billed twice · 480p · source ratio · $2.10 for both versions

**Source:** BytePlus prompt guide, 'Editing tasks': state the scope and the content to change.

### 15. Edits: confine the change to a time range

**Symptom:** An edit meant for one moment alters the whole clip.

**Before**

```text
Make him do a thumbs-up instead.
```

**After**

```text
From 5 to 8 seconds, change the man's gesture from waving to giving a thumbs-up toward the camera. Keep the first 5 seconds, his face, his clothes, the background and the audio unchanged.
```

**What changed**

- A time range limits the change to three seconds.
- 'From waving to a thumbs-up' names both the old action and the new one.

**Test it:** `python ab.py run 15` · video edit · 8 s source, billed twice · 480p · source ratio · $2.80 for both versions

**Source:** BytePlus prompt guide, 'Editing tasks': use timestamps for partial edits and describe the change from A to B.

### 16. First frame: describe the motion, not the picture

**Symptom:** The first frame gets reinterpreted instead of animated.

**Before**

```text
A beautiful photo of a mountain lake with pine trees, a wooden rowboat, blue sky, white clouds and perfect reflections, 4K.
```

**After**

```text
The water ripples gently as the rowboat drifts toward the shore; clouds move slowly over the peaks and their reflections shimmer. The camera stays still. Sound: lapping water and a distant bird call.
```

**What changed**

- The image already shows the scene, so the rewrite only says what moves.
- On Seedance 2.5 a frame request takes aspect_ratio adaptive or none; a fixed ratio is rejected.

**Test it:** `python ab.py run 16` · first frame · 5 s · 480p · adaptive · $0.87 for both versions

### 17. First and last frame: give the transition a path

**Symptom:** The two frames melt into each other with no sense of how one became the other.

**Before**

```text
Transform the first image into the second image.
```

**After**

```text
The camera pulls straight back from the close-up of the seedling in the first frame while the seasons pass: the sprout grows into a sapling, its leaves turn gold and fall, and snow settles, ending on the wide winter view of the full-grown tree in the last frame. One continuous pull-back, no cuts. Sound: wind that changes with the seasons.
```

**What changed**

- The rewrite gives a camera path (a pull-back) and the order of the changes.
- 'Transform A into B' leaves the path between the frames unspecified.

**Test it:** `python ab.py run 17` · first + last frame · 8 s · 480p · adaptive · $1.40 for both versions

### 18. Declare keyframes when the order must hold

**Symptom:** Storyboard images are used out of order, or only loosely.

**Before**

```text
Make a story with these pictures of a balloon flight.
```

**After**

```text
Use @Image 1 to @Image 4 in order as keyframes. A hot-air balloon is inflated in a field at dawn (@Image 1), lifts off over the treetops (@Image 2), drifts above a river valley (@Image 3) and lands softly in a meadow at sunset (@Image 4). The camera follows the basket in one continuous take. Sound: the burner's roar, wind and birds.
```

**What changed**

- The first sentence declares the images as keyframes in order.
- Each beat of the story names its keyframe.

**Test it:** `python ab.py run 18` · reference · 12 s · 480p · 16:9 · $2.10 for both versions

**Source:** BytePlus prompt guide, 'Keyframe reference'.

### 19. Stage in depth for vertical 9:16

**Symptom:** In a tall frame, subjects are cut off at the sides or shrink to dots.

**Before**

```text
Two gunslingers face each other across a wide dusty street in a western town, standing far apart at the left and right edges.
```

**After**

```text
Vertical framing. One gunslinger stands in the foreground with his back to the camera, filling the lower third of the frame; his opponent stands small and centered further down the dusty street, framed between two rows of wooden buildings. Low angle, hot noon sun, dust blowing between them. Sound: wind and a creaking sign.
```

**What changed**

- Side-by-side staging is rearranged front to back, which fits a tall frame.
- The prompt says where in the frame each subject sits.

**Test it:** `python ab.py run 19` · text-to-video · 6 s · 480p · 9:16 · $1.05 for both versions

### 20. Make a clip that loops

**Symptom:** A clip meant to loop jumps at the seam.

**Before**

```text
A loop of a lava lamp.
```

**After**

```text
A lava lamp on a dark shelf: wax blobs rise, merge and sink in slow, steady motion. Locked-off camera, no cuts, no change in the light. The last frame matches the first frame so the clip loops seamlessly. Sound: a soft electrical hum.
```

**What changed**

- Camera and light are locked, so the only thing that changes is the wax.
- The loop is stated as a condition: the last frame matches the first. Trim a few frames in your editor if the seam still shows.

**Test it:** `python ab.py run 20` · text-to-video · 5 s · 480p · 1:1 · $0.87 for both versions

## A/B test a play

[`ab.py`](./ab.py) renders both versions of a play with the same settings, polls them together and saves `play-NN-before.mp4` and `play-NN-after.mp4`. Standard library only, Python 3.9 or newer; `--side-by-side` also writes a comparison clip if `ffmpeg` is installed.

```bash
git clone https://github.com/percivaldunmore9/seedance-2-5-prompt-playbook
cd seedance-2-5-prompt-playbook
export SEEDANCE_API_KEY=your-key       # an ArgoLink key; SEEDANCE_BASE_URL switches the endpoint

python ab.py list                      # every play and the cost of testing it
python ab.py run 6 --side-by-side      # timestamps play: two 10 s clips at 480p, $1.75
python ab.py run 12 --asset marcus=marcus.png --asset vera=vera.png
python ab.py run 14 --asset source=my-clip.mp4 --dry-run
```

- **Your media.** Plays 11–18 use your own images, clips or audio. Each placeholder in [`plays.json`](./plays.json) has a name (`https://example.com/marcus.png` is `marcus`), and `--asset name=FILE_OR_URL` fills it in both versions. Local JPEG, PNG, MP4, MOV, MP3 and WAV files are uploaded once through `POST /v1/media/uploads`; `https://` URLs are passed through. `ab.py` lists any missing names before it sends anything.
- **Settings.** Both versions run at 480p, the cheapest tier, so you compare prompts and not resolutions. `--resolution 720p` or `1080p` re-runs a play at a higher tier.
- **Local checks.** Before submitting, `ab.py` checks each body against the documented Seedance 2.5 rules (durations, ratios per mode, reference limits, `@` mentions, edit fields), so a typo fails on your machine instead of as an API error.
- **Polling.** Jobs are polled every 12 seconds, within the 10–15 seconds the API docs suggest, until each one is `done`, `failed` or `expired`. A failed version is reported with its `error.code`, and the other one is still downloaded.
- **Endpoint.** Requests go to `https://argolink.io/v1` unless `SEEDANCE_BASE_URL` says otherwise.

One A/B pair is a sample of two. Seedance 2.5 has no seed parameter, so the same prompt gives a different take every time; run a pair two or three times before you decide that a rewrite works.

## What testing costs

Seedance 2.5 is billed per second of output, at the rate of the resolution:

| Provider | 480p | 720p | 1080p | One A/B pair, 2 × 5 s at 480p |
|---|---:|---:|---:|---:|
| [ArgoLink](https://argolink.io/gh-seedance-2-5-prompt-playbook) | $0.0874 | $0.196 | $0.483 | $0.87 |
| [BytePlus ModelArk](https://docs.byteplus.com/en/docs/modelark/model-pricing) (official) | $0.1028 | $0.2311 | $0.5686 | $1.03 |
| [fal.ai](https://fal.ai/models/bytedance/seedance-2.5/text-to-video) | $0.2205 | $0.473 | $1.164 | $2.21 |

<sub>Read on 2026-10-07 from each provider's page. BytePlus prices Seedance 2.5 at $10.70 per million tokens for 480p/720p and $11.70 for 1080p, tokens = width × height × 24 × seconds / 1024; at 854×480, 1280×720 and 1920×1080 that is the per-second rate above. fal's per-second figures are its 16:9 approximations.</sub>

- Testing all 20 plays once at 480p costs $27.09; at 720p, $60.76.
- Reference videos add their own seconds to each version (play 13 assumes a 5-second clip). Reference images and audio are free.
- An edit bills its source twice, as output and as reference, so plays 14 and 15 cost more than their length suggests.
- Failed, rejected and expired jobs are not billed, and the finished job's `usage.billed_seconds` is what you pay for.

## FAQ

**Why did the after version not look better?**
Each render is a fresh sample, and there is no seed to hold it still, so judge a rewrite over two or three runs rather than one. If the after prompt keeps losing, check it against the shape above: one sentence that says who does what, one camera move per time range, and every reference bound to a role.

**Do these plays work on Seedance 2.0?**
Most of them do. Three do not carry over: play 6, because Seedance 2.0 follows shot numbers rather than timestamps, and the edit plays 14 and 15, because only Seedance 2.5 edits video. BytePlus also advises against multi-view subject images on 2.0, and 2.0 clips stop at 15 seconds.

**How long should a prompt be?**
Long enough to cover subject, action, camera, light, sound and what must not change. The rewrites here run from 26 to 66 words. The API accepts up to 40,000 bytes, so length is a matter of clarity, not a limit you will reach.

**What gets rejected before a job even starts?**
A fixed aspect ratio on a first-frame or first-and-last-frame request, frames combined with reference lists, an edit that carries images, audio or frames, an `@Image 3` when only two images were sent, and any `seed` or `watermark: true`. Rejections are not billed, and `ab.py` catches all but the last two locally.

**Can I write the prompt in another language?**
Yes. Dialogue in particular should be written in the language you want spoken; BytePlus lists native generation in more than ten languages. Reference mentions also work in other languages: `@图片1` and `@imagen 1` are recognized alongside `@Image 1`.

**Is the "before" prompt always rejected or broken?**
No. Every before prompt here passes the API's request rules (the tests check it). It is weak, not wrong, which is why the difference only shows when you render both.

## Sources

- BytePlus, Seedance 2.5 prompt guide: <https://docs.byteplus.com/en/docs/modelark/seedance-2-5-prompt-guide>
- Seedance 2.5 model page (fields, modes, limits, prices): <https://argolink.io/en/models/seedance-2.5>
- API docs, Seedance chapter (polling, billing, errors): <https://argolink.io/en/docs>
- BytePlus ModelArk pricing: <https://docs.byteplus.com/en/docs/modelark/model-pricing>
- fal, Seedance 2.5 text-to-video: <https://fal.ai/models/bytedance/seedance-2.5/text-to-video>

All read on 2026-10-07.

## Tests

```bash
pip install pytest && pytest
```

The tests check every play against the request rules and run `ab.py` against a fake API, so they need no key and no network.

## License

MIT
