# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 21.0.0

## Description:

- Updated the plugin for compatibility with Tutor v21 / Open edX Ulmo.
- Modernized packaging by introducing pyproject.toml (PEP 517 / PEP 621) and removing legacy packaging configuration.
- Replaced deprecated pkg_resources resource access with importlib.resources for loading bundled templates and patches.
- Updated the Enterprise Catalog Docker image.
- Updated GitHub Actions CI configuration to reflect the new Python support and packaging layout.

## Unreleased

- Basic Tutor plugin initialization.
- Enabling Enterprise using this tutor plugin.
