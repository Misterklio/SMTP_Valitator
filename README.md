# SMTP VALIDATOR

CLI to validate SMTP credentials from a list file. It supports STARTTLS (`587`) and SSL (`465`), shows colorized, streaming output, retries Office 365 using `smtp.office365.com`, and writes valid entries to `valid_smtp.txt`.

## Requirements
- Python 3 on Windows (`py` launcher available)
- Network access to target SMTP servers

## Input Format
- One entry per line: `URL|PORT|USER|PASSWORD`
- Lines starting with `#` or blank lines are ignored
- Example:
  - `smtp.office365.com|587|user@domain|password`
  - `mail.example.com|465|user@example.com|password123`

## Quick Start
- Place your entries in `list.txt` in `c:\AppServ\www`
- Run:
  - `py checker.py list.txt`

## Common Options
- `--reasons` shows SMTP error codes/messages on failures
- `--verbose` enables SMTP session debug logs
- `--no-color` disables ANSI colors
- `--no-shuffle` scans in file order
- `--no-dedupe` allows duplicate lines to be scanned repeatedly

Examples:
- `py SMTP_validator.py list.txt --reasons`
- `py SMTP_validator.py list.txt --reasons --verbose`
- `py SMTP_validator.py list.txt --no-color --no-shuffle`

## Output
- Colorized labels:
  - `Scanning:` gold
  - `Retry scanning:` ghostwhite (Office 365 fallback)
  - `Failed:` crimson
  - `Login successful:` chartreuse
- Host and port are green; user is grey and enclosed in brackets `[user]`
- Live spinner shows `Please wait ...` during checks

Example:
- `Scanning: smtp.office365.com:587 - [user@domain]`
- `Login successful: smtp.office365.com:587 - [user@domain]`
- or `Failed: smtp.office365.com:587 - [user@domain] (code=535, reason=Authentication failed)`

## Saved Results
- On successful login, the entry is appended to `valid_smtp.txt` as `URL|PORT|USER|PASSWORD`
- Office 365 fallback saves using `smtp.office365.com|PORT|USER|PASSWORD` if it succeeds

## Notes
- Office 365: Use `smtp.office365.com:587` with STARTTLS. Regional endpoints like `outlook-*.office365.com` may not accept SMTP submission.
- If MFA is enabled, SMTP AUTH may require an app password or be disabled entirely.

## Troubleshooting
- `Connection refused` or `timed out`: wrong host/port or firewall rules
- `SSL: WRONG_VERSION_NUMBER`: server is not offering SSL on `465`; try `587` with STARTTLS
- `535 Authentication failed`: credentials invalid or SMTP AUTH disabled for the account/tenant

## Contact
- Telegram: `@misterklio`
- Website: `https://oscoding.vip`
