# Security Policy

RegForge changes system configuration, so a malicious or mistaken `.reg` file is a real risk.

## Reporting a problem

If you find a tweak that is unsafe, deceptive, or modifies keys beyond what its README documents,
please use GitHub's **Report a vulnerability** (Security tab) rather than a public issue.

## Our safeguards

- Every tweak must document each key it changes.
- CI rejects `.reg` files that touch hive roots, hives other than HKCU/HKLM, or lack a rollback for every key.
- `enable.reg` may never delete keys.
- Never run a `.reg` file you have not read, including ones from this repository.
