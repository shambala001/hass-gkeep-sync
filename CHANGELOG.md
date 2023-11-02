# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com), and this project adheres to [Semantic Versioning](https://semver.org).

## Unreleased

## v0.1.0 - 2022-11-03

### Changed
- Change name to `gkeep_sync` to prevent duplicate issue in HACS
- Add minimum Home Assistant version (`2022.10.4`)
- Remove US country code
- Update `gkeepapi` to `v0.14.2`
- Rename config keys (`title` to `name`, `things` to `items`)

### Removed
- Remove support for `sync_shopping_list` service