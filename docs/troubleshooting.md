# pi-log Troubleshooting Guide

This document provides a comprehensive troubleshooting reference for shell behavior, pyenv initialization, interpreter discovery, pre-commit hook failures, serial ingestion issues, parser failures, and systemd service behavior.

---

# 1. Shell Verification

### Check active shell:
```
echo $SHELL
```

Expected:
```
/bin/zsh
```

If incorrect:
- Command Palette → Terminal: Select Default Profile → zsh
- Restart VS Code

---

# 2. pyenv Initialization

### Verify pyenv is active:
```
which python3.10
```

Expected:
```
~/.pyenv/shims/python3.10
```

If missing, add to `.zshrc`:
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Restart VS Code.

---

# 3. Virtual Environment Consistency

### Project runtime:
```
python3.9 -m venv .venv
```

### Pre-commit interpreter:
```
default_language_version:
  python: python3.10
```

---

# 4. pre-commit Hook Environment

### Rebuild hook envs:
```
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### Common failure:
- pip conflict involving ansible-lint

### Fix:
- Remove all `additional_dependencies`
- Pin only via `rev:`

---

# 5. Known Failure Modes (Local Dev)

## Failure Mode 1 — VS Code launches bash
**Symptoms:**
- `echo $SHELL` → `/bin/bash`
- pyenv not loading

**Resolution:**
- Select zsh as default profile
- Clear VS Code terminal state

---

## Failure Mode 2 — pyenv not initializing
**Symptoms:**
- `which python3.10` returns nothing

**Resolution:**
- Ensure `.zshrc` contains pyenv initialization

---

## Failure Mode 3 — ansible-lint version conflict
**Symptoms:**
- pip reports conflicting versions

**Resolution:**
- Remove `additional_dependencies`

---

# 6. Pi-Side Troubleshooting (Ingestion, Serial, Systemd)

## Failure Mode 4 — `/dev/ttyUSB0` missing at service startup
**Symptoms:**
- Logs show:
```
SerialException: could not open port /dev/ttyUSB0
```

**Cause:**
- Systemd starts before USB enumeration completes.

**Resolution:**
Add to `pi-log.service`:
```
ExecStartPre=/bin/sleep 5
```

Redeploy via Ansible.

---

## Failure Mode 5 — Serial device present but ingestion loop not reading
**Symptoms:**
- `sudo cat /dev/ttyUSB0` shows data
- DB remains empty
- No “Parsed reading” logs

**Causes:**
- Parser mismatch
- SerialReader not calling `_handle_parsed`
- Service crash loop

**Resolution:**
- Verify parser matches MightyOhm format
- Check logs:
```
sudo tail -f /opt/pi-log/logs/error.log
```

---

## Failure Mode 6 — Parser returns partial record
**Symptoms:**
```
process_line failed: 'cps'
```

**Cause:**
- `parse_geiger_csv()` returned a dict missing required fields.

**Resolution:**
- Ensure parser extracts:
  - cps
  - cpm
  - usv
  - mode
  - raw

---

## Failure Mode 7 — No SQLite database created
**Symptoms:**
```
ls -l /opt/pi-log/data
```
shows empty directory.

**Causes:**
- Ingestion loop crashes before DB init
- Serial port failure prevents startup
- Wrong WorkingDirectory in service file

**Resolution:**
- Fix service file WorkingDirectory:
```
WorkingDirectory=/opt/pi-log
```
- Add startup delay
- Fix parser errors

---

## Failure Mode 8 — Push client errors
**Symptoms:**
```
PushClient failed: <error>
```

**Causes:**
- Network unreachable
- Invalid API key
- Upstream API offline

**Resolution:**
- Verify `settings.push.enabled`
- Verify URL + API key
- Check Pi network connectivity

---

# 7. Environment Parity Checklist

- [ ] VS Code uses zsh
- [ ] pyenv initializes
- [ ] python3.10 available
- [ ] pre-commit installs cleanly
- [ ] ansible-lint runs without conflict
- [ ] `.venv` uses Python 3.9
- [ ] Pi service uses correct WorkingDirectory
- [ ] Pi service includes ExecStartPre delay
- [ ] Parser matches MightyOhm CSV format
- [ ] SQLite DB created at `/opt/pi-log/data/readings.db`
- [ ] Logs show successful ingestion

---

# 8. Diagnostic Commands

### Local:
```
echo $SHELL
which python3.10
env | sort
pre-commit clean
pre-commit install
```

### Pi:
```
ls -l /dev/ttyUSB*
sudo tail -f /opt/pi-log/logs/service.log
sudo tail -f /opt/pi-log/logs/error.log
sudo systemctl status pi-log
sudo sqlite3 /opt/pi-log/data/readings.db "SELECT * FROM readings LIMIT 5;"
```

---

# 9. Appendix: Flowcharts and Diagrams

See:
- `docs/diagrams/sequence.md`
- `docs/diagrams/system-overview.md`
