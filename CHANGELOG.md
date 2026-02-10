# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Added Desktop Shell with window stack, dock, and SVG rendering
- Integrated realTinyTalk as the first-class scripting language for apps
- Implemented AppProcess and ProcessManager (launch, list, kill)
- Vault integration for process-owned persistence (save/load notes)
- Notes app implemented in TinyTalk; UI to launch, save, and edit notes
- In-window HTML editor overlay for editing notes inside window
- IPC: publish/subscribe message bus with per-process subscriptions
- Per-process FFI policy flags (vault, filesystem, system, network)
- App packaging and simple App Store (install/uninstall apps)
- Extensive tests and CI workflow

## [0.1.0] - 2026-02-10
### Added
- Initial public beta release artifacts
- Examples: Notes app, demo server routes
- CLI & automation: release build workflow (CI)

### Fixed
- Stabilized unit tests and fixed event routing semantics

### Security
- Built-in FFI sandboxing options for processes

