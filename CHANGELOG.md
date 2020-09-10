# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Default superusers are associated with CDS, not "Ontario"

## [1.5.1] - 2020-09-08

### Fixed

- Added aria-describedby attributes to inputs when there are validation error messages.
- Yubikey verification form now using base form (no colons, removed autocomplete, etc.)

## [1.5.0] - 2020-09-03

### Added

- Superusers can now block users permanently via django-admin. Those users won't be able to login until a superuser reactivate them.

### Hotfixes

- Adding a check in the login_handler to prevent the login form from crashing when trying login with a non-existent e-mail

## [1.4.1] - 2020-09-03

### Updated

- Lower the daily limit of one time key generation to 25 in production

## [1.4.0] - 2020-09-03

### Updated

- Move the errors messages of fields that equality validation (Enter your password again, Enter your phone number again) into the first field to make it easier for accessibility.
- When the user changes password, the user loose his session. Now the user will keep his session on the device used to change the password but will loose his session on all other logged-in devices.

## [1.3.0] - 2020-09-02

### Added

- Adding a second layer of user throttling. After 100 failed logins in a 30 days window, the user will be blocked for 24 hours.
- New Quick Guide page now available in the footer.
- A slack notification is now sent on failed Github Actions
- Github Actions now running terraform check, plan and security scans on deploys (staging repository)

### Updated

- The privacy page has been simplified

## [1.2.0] - 2020-08-28

### Added

- Adding a list of authorized domains for outgoing account invites

## [1.1.0] - 2020-08-27

### Added

- Amazing new feature: added skiplink for logged-in users

## [1.0.0] - 2020-08-27

### Added

- Added CHANGELOG file
- Added VERSION file
- Added version to GitHub actions
- Added version to <head> of application
