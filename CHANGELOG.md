# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [1.10.1] - 2020-10-29

### Updated

- Update "instructions for patients" screens to reflect new traceback instructions in the app

## [1.10.0] - 2020-10-29

### Added

- Split the signup flow into multiple pages: add a second page for entering mobile phone as 2FA device

### Fixed

- Add the password label and help text back to the sign up page
- Hide the "Your account" link on the 2FA page because people can't see/edit their account info yet

## [1.9.2] - 2020-10-14

### Updated

- Rewrite default validation messages
- Content updates to various pages in the app, including the Quick Guide page
- Remove the "required" attribute from form inputs
- (Super)admins are no longer permitted to change other users' passwords

### Fixed

- Redirect to the login page if yubikey verification page is visited before user is authenticated

## [1.9.1] - 2020-10-09

### Fixed

- Lowercase emails during logins attempts. We convert emails to lowercase during signup, so we should do it during login as well.

## [1.9.0] - 2020-10-08

### Added

- Add new page and flash messages to handle scenarios where account invitations are expired, deleted or accepted
- Pass the admin user's email to the account invitation template in Notify

## [1.8.6] - 2020-10-07

### Updated

- Update French content in various places across the application

### Fixed

- Replace straight apostrophes (`'`) with curly apostrophes (`’`)

## [1.8.5] - 2020-10-06

### Updated

- Now that more provinces are onboarded, bump the limits for how many keys can be generated before alarms go off
- Add custom error templates for common error states
- Very small change to the phonetic alphabet

### Fixed

- Application throttling works as expected, fixed the sequencing of operations
- Remove prior login attempts for newly created accounts
- Fix the login page layout on IE11

## [1.8.4] - 2020-09-30

### Updated

- Remove traceback instructions for the instructions for patients. We want to wait for the app to be updated before those go out.

## [1.8.3] - 2020-09-30

### Updated

- Update in-app content

  - Update instructions and screenshots for instructions that healthcare providers give to patients

### Fixed

- Data migration to add "sent" dates to any invitations missing that fields
- Allow resending invitations whenever no user account exists — previously, an "accepted" invitation for a deleted user would prevent that user from being invited again
- Remove duplicate "preconnect" link in HTML header

## [1.8.2] - 2020-09-25

### Updated

- Title Case the words in the phonetic alphabet
- Updated content for the Privacy and Terms of use pages

### Fixed

- Fixed CSS for "logged-in" nav items for the login page
- Fixed CSS for login thank you message on IE11

## [1.8.1] - 2020-09-21

### Fixed

- Fixed CSS for the big code box on the "/key" page

## [1.8.0] - 2020-09-21

### Updated

- Use Notify to send user-facing emails: ie, the password reset and the invitation email

### Fixed

- No longer flag invitations as accepted when the user clicks on the link

## [1.7.0] - 2020-09-21

### Added

- Adds a welcome page for new users (after completing signup + 2fa for the first time)

### Updated

- Update the quick guide with an example code

## [1.6.2] - 2020-09-18

### Updated

- Up the invitations limit properly to 200 per hour temporarily
- COVID Keys back down to 25

## [1.6.1] - 2020-09-18

### Updated

- Up the COVID Key limit to 200 per hour temporarily

## [1.6.0] - 2020-09-15

#### ⚠️ This release includes a data migration

### Fixed

- Fix password reset links running in non-production environments
- Default superusers are associated with CDS, not "Ontario"
- Let managers remove other team members who have created a CovidKey in the past

### Added

- Add "thank you" message to login page

## [1.5.1] - 2020-09-08

### Fixed

- Added aria-describedby attributes to inputs when there are validation error messages.
- Yubikey verification form now using base form (no colons, removed autocomplete, etc.)

## [1.5.0] - 2020-09-03

#### ⚠️ This release includes a data migration

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
