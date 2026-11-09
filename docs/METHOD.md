# Method — decomposing a hard topic into simulation beats

The transferable core of the reference videos （漫士沉思录 / Manshi, by Lu Rui, Tsinghua Yao Class) is not the palette or the props — it is the decomposition: how a topic like P vs NP is broken into chunks a lay viewer can hold, in an order that makes each chunk feel inevitable. This document states each principle, then its instance in the Turing / P-NP material (the full 70-minute reference covers six beats beyond the one episode packaged here; the principles are drawn from the whole video, the worked episode from its Turing-machine beat).

## 1. One concrete cast of objects, recurring

Introduce a small cast of concrete objects early and reuse it for every abstraction, instead of inventing fresh examples per concept. **Instance:** ten numbers (56 19 84 29 93 16 78 22 60 51, sum 508) carry four tasks in the reference's second beat (sum, min, sort, equal-partition); the same ten numbers return on the Turing machine's tape, on the balance scale, and in the verification accounting. The viewer never re-learns an example — each return buys a new idea with old familiarity.

## 2. Stakes before machinery

Open with what the problem is worth and who cares, not with definitions. **Instance:** the reference opens on the Clay Institute's $1,000,000 prize (the cheque is shown as a real artifact) and a Minesweeper hook at 0:30 that is not cashed until ~53:00 — a planted question the viewer carries for the whole video.

## 3. Build the measuring tool before measuring

Before classifying problems, give the viewer the instrument: what "cost" means (worst case, asymptotics, big-O), demonstrated on the cast. **Instance:** the four tasks on the ten numbers are re-run at growing scale — 1 second becomes 36 years becomes the age of Earth — so exponential growth is felt in the body before it is named.

## 4. Objection pre-emption

Speak the audience's objection out loud, in their words, then answer it. **Instance:** after early "polynomial = fast" framing, the reference itself objects — merge sort, the ellipsoid method rescuing linear programming, AKS (2002) — teaching "feels hard ≠ is hard" before the viewer can over-trust the new tool. In the worked episode, S5 does the same at small scale: the paper-card joke "NP = Not P" is shown and struck through in red, correcting the most common misreading before it forms.

## 5. Definitions arrive late — demonstration, metaphor, instance, definition

Never lead with the formal definition. Show the phenomenon, name it with an everyday metaphor, run one full instance, and only then state the definition, which now compresses experience instead of replacing it. **Instance:** NP is defined only after the viewer has watched a machine guess a partition and verify it in 19 steps; "reduction" is defined only after a complete Sudoku→graph-coloring reduction is worked and the exam-cheating metaphor （打小抄） has made its direction intuitive.

## 6. One everyday metaphor per abstraction

Each abstract idea gets exactly one physical metaphor, kept consistent wherever the idea recurs. **Instance:** guessing-and-checking is a magic conch （神奇海螺） that whispers the answer; verification is a teacher grading papers （老师改卷） — easy to check, hard to produce; NP-completeness is a chain of dominoes / one problem wearing many costumes; the worked episode keeps the conch as a literal prop that sits inside the P platform — the metaphor made physical, recurring on cue.

## 7. Scale-shock numbers, computed

Abstract gaps are converted to body-scale quantities. **Instance:** factoring is made visceral by digit counts — a 617-digit number that brute force cannot touch against the 270-digit world record; the worked episode's version is the accounting coda: 19 steps (guess + verify) against 9216 (exhaustive × verify) and 2n = 20 — small numbers, honestly derived from the sim, chosen so the viewer can recompute them on the spot.

## 8. Verification asymmetry as the hinge

The whole P/NP story hangs on one asymmetry — finding is hard, checking is easy — so it is given its own beat, its own history (Jevons, 1874), and its own metaphor before any formalism. **Instance:** in the worked episode the asymmetry is not asserted but enacted: the nondeterministic machine's stage-1 guess writes a credential row of bits under the tape, and stage 2 checks it on the same scale the audience has been watching — the credential row is the physical form of "a short proof that can be checked".

## 9. History as pressure valve

After each hard concept, a person's story resets attention while deepening stakes. **Instance:** Gödel's 1956 letter to von Neumann — which already asks the P-vs-NP question — lost for 32 years; Cook and Levin arriving at the same theorem from opposite sides of the Cold War; Karp's 21 problems turning "thousands of failures" into one problem. In a short episode, one compact history card (the Church–Turing thesis card in S3) does the same job.

## 10. The simulation is the argument

Where the reference demonstrates a machine, the machine actually runs: head moves, tape rewrites, the step counter increments, the δ-table highlight follows the current state. A faked demonstration teaches a false mental model and — practically — cannot be kept consistent across cuts. **Instance:** frame-study of the reference showed its own sampled parity run does not fully reconcile across jump cuts; the worked episode's response was to make its machines internally exact — every step, highlight, and counter value derived from one executed run, so any frame can be audited against the δ table printed on the same screen.

## 11. Correction beats

Spend a beat un-teaching the over-simple lesson the video itself just taught. **Instance:** after NP-completeness lands, the reference corrects course — NP-complete ≠ hopeless (an 80,000-city TSP instance, from Korean delivery data, solved to optimality in 2025) — and separately debunks a folk myth (soap films "solving" Steiner problems) rather than letting it stand as intuition.

## 12. Elevation close

End by lifting the technical result into why it matters for a life: if P = NP, secrets, scarcity of insight, and the value of taste all change (Aaronson's argument; the Gasarch polls 61% → 83% → 88% tracking expert belief); if P ≠ NP, the universe is one where finding is harder than checking — which is exactly why some things stay precious. **Instance (episode scale):** the worked episode ends smaller but with the same shape — the question itself, "P = NP ?", typeset huge and held in silence, the machine and the platform still on stage behind it: the unresolved question is the souvenir.

## Beat-locking checklist (before any building)

For each beat, the script must state: (a) its topic in one line; (b) the transition that carries in from the previous beat; (c) the full narration; (d) which simulation carries it and what the sim computes; (e) the callback, if any, it plants or cashes. A beat missing (b) is where audiences drop; a beat missing (d) is where productions degenerate into slide decks. The template in `templates/script-template.md` enforces all five columns.
