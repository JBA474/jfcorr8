# jfcorr8

Corridor 8: Galactic Wars (1996 prototype) on JonoF's Build engine, laid out like [jonof/jfwhaven](https://github.com/jonof/jfwhaven)
so it builds against the `mister` branches of [ItsDanik/jfbuild](https://github.com/ItsDanik/jfbuild)
and [ItsDanik/jfaudiolib](https://github.com/ItsDanik/jfaudiolib) and runs as a game set of the
[jfSW MiSTer hybrid core](https://github.com/ItsDanik/jfSW_MiSTer) (8BitDo-class gamepad, rumble,
the core's OSD Cheats page).

`src/` and `CMakeLists.txt` are generated from the original DOS sources by the scripts in
`build-tools/` (see the `q_*full.sh` driver there), so the port stays reproducible from the
originals. The game data itself is not in this repository.

**Status:** playtesting and bug-fixing in progress, feedback welcome.

**Origin of the sources:** Capstone's CORR8 prototype source as released by Les Bird (RTCM mirror https://rtcm.site/knowledge-base/downloads-rtcm/src-corridor8-source). The id Software placeholders in the prototype's data are replaced in the game set by Freedoom 0.13.0 assets (BSD 3-clause) and the game's own art; see the set's README.

**License:** inherited from the trees this builds on. The source tree is under Ken Silverman's Build license (`buildlic.txt`, free of charge, no commercial use), the same as JonoF's jfbuild, jfwhaven and jftekwar; the MiSTer port additions in `src/` are under the same terms; the port scripts in `build-tools/` are GPL-2.0-or-later (`build-tools/LICENSE`). See `LICENSE`. The game code is Capstone's as released to hobbyists by Les Bird; no game data is included.

**Disclaimer:** I of course used AI. Most of the porting, building and log-level testing was done with
Claude Code (Anthropic) under my direction; the games were played on the hardware by me.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
