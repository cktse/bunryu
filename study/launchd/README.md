# Daily quiz email — launchd LaunchAgent (specs §10.8.8)

Runs `email_quiz.py --send --once-daily` once per day at **07:00 local**, with a
login/boot **catch-up** (`RunAtLoad`) for days the Mac was off at 07:00. The
app's `--once-daily` guard checks `progress.json` and no-ops if an email was
already sent today, so the multiple triggers collapse to one send — and because
exposure is logged only on a *successful* send, a failed attempt (e.g. no network
right after wake) is retried on the next trigger.

## Install (per machine — touches `~/Library`, so you run these)

```sh
# 1. copy the agent into your LaunchAgents
cp "study/launchd/com.bunryu.dailyquiz.plist" ~/Library/LaunchAgents/

# 2. load it (modern launchctl)
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.bunryu.dailyquiz.plist
#   (older macOS: launchctl load ~/Library/LaunchAgents/com.bunryu.dailyquiz.plist)

# 3. (optional) fire once now to verify end-to-end
launchctl kickstart -k gui/$(id -u)/com.bunryu.dailyquiz
```

Check status / logs:

```sh
launchctl print gui/$(id -u)/com.bunryu.dailyquiz | grep -E "state|last exit"
tail -n 20 ~/Library/Logs/bunryu-dailyquiz.log
```

Unload / uninstall:

```sh
launchctl bootout gui/$(id -u)/com.bunryu.dailyquiz
#   (older macOS: launchctl unload ~/Library/LaunchAgents/com.bunryu.dailyquiz.plist)
rm ~/Library/LaunchAgents/com.bunryu.dailyquiz.plist
```

## Notes

- **A LaunchAgent (per-user), not a LaunchDaemon** — the send needs your logged-in
  session: `study/secrets.json`, network, and the repo path. It runs while you are
  logged in.
- **Absolute, machine-specific paths.** The plist hard-codes the Python
  interpreter (the real pyenv binary, not the shim, so it needs no pyenv/PATH
  setup) and the repo path. **Regenerate the plist if either moves** — e.g. after
  a `pyenv` version change (`python3 -c 'import sys; print(sys.executable)'`).
- **`secrets.json` must be filled in** (`study/secrets.json`), or the send exits
  with an error (logged).
- **iCloud note:** the repo lives in iCloud Drive; keep it materialized locally so
  launchd can read `email_quiz.py` (avoid "download-on-demand" eviction of the
  `study/` files).
- Change the time by editing `StartCalendarInterval` (Hour/Minute), then reload
  (`bootout` then `bootstrap`).
