# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
- Remove Basicauth

## [2.3.2] - 2021-09-13

## Updated

- Updated beautiful soup to version 4.10.0 from 4.9.3
- Updated black to version 21.8b0 from 21.6b0
- Updated cffi to version 1.14.6 from 1.14.5
- Updated dependency-injector to version 4.36.0 from 4.34.0
- Updated django to version 3.2.7 from 3.2.5
- Updated django-axes to version 5.24.0 from 5.20.0
- Updated django-cors-headers to version 3.8.0 from 3.7.0
- Updated django-ipware to version 4.0.0 from 3.0.2
- Updated django-sass to version 1.1.0 from 1.0.1
- Updated django-waffle to version 2.2.1 from 2.2.0
- Updated idna to version 3.2 from 2.10
- Updated newrelic to version 6.8.1.164 from 6.4.3.160
- Updated notifications-python-client to version 6.2.1 from 6.2.0
- Updated pathspec to version 0.9.0 from 0.8.1
- Updated phonenumbers to version 8.12.31 from 8.12.26
- Updated pillow to version 8.3.2 from 8.3.0
- Updated protobuf to version 3.18.0rc2 from 3.17.3 
- Updated python-dotenv to version 0.19.0 from 0.18.0
- Updated regex to version 2021.8.28 from 2021.7.1
- Updated requests to version 2.26.0 from 2.25.1
- Updated six to version 1.16.0 from 1.15.0
- Updated sqlparse to version 0.4.2 from 0.4.1
- Updated toml/tomli to version 1.2.1 from 0.10.2
- Updated whitenoise to version 5.3.0 from 5.2.0
- Updated develop to version 6.0b1 from 5.5
- Updated python-dateutil to version 2.8.2 from 2.8.1


## [2.3.1] - 2021-08-30

## Updated

- Fixed alignment issues with buttons on review page, 'Choose date and time' screens and invitations page 
- Changed button text on confirmation page after sending alerts and changed button copy on adding new date screen 
- Fixed up French translations 
- Removed italics in addresses
- Changed hint message on "Change your mobile number" page
- Fixed up non-breaking spaces in French before colons and around text in quotes- Fixed up typos on Portal start page
- Fixed up bolding in Terms of Use page


## [2.3.0] - 2021-08-09

## Updated

- Remove QR code DNS health check 
- Fix/send Alert menu fix
- Update the address complete api key 
- Changes to "Sending Alerts" screen
- QR code 403 changes 
- Fix French apostrophes
- Removed lock for sending surveys to health care users regardless of whether they sent an alert previously or not.

## Added

- Added CloudWatch synthetic canary to monitor QR code
- Added CloudWatch alarm for unhealthy QR code canary 
- Enabled AWS Shield for QR Code 
- Enable sending of surveys to healthcare users
- Added new bulk action for marking inactive


## [2.2.0] - 2021-07-07

## Updated

- Modify uwsgi config to scale number of workers/threads
- Portal content audit updates
- Registration site content audit updates
- Fix autoscaling config
- Adjust health check thresholds so ELB doesn't kill processes as unhealthy when slow to respond under load
- Updated post-login flow for users with/without alert permission
- Fix bug when sorting on Alert History screen
- Add French translations for short month names
- Django and dependencies update
- Updated poster/tipsheet
- Accessibility and Mobile/responsive display fixes
- Updated navigation / flow and content on alerting wizard
- Fix bug in nav bar highlight in outbreaks section

## Added

- Add WhiteNoise to help with static asset caching
- Add Survey management/sending ui for post-pilot surveys
- Navigation home screen for portal for alerting enabled users

## [2.1.0] - 2021-06-01

## Updated

- Validate Canadian postal code format
- Enforce character limit for location name so it doesn't run off the poster
- Add QR Alert docs to Portal
- Add Location Outbreaks History view
- New venue types and selection html select control
- Content updates throughout
- Updated poster and instructions
- Phone number validation
- Updated Portal start screen and navigation
- Split notify service for different notify services in portal and qrposter
- Change rounding of datetime wizard values in minutes
- New privacy and ToU pages
- Google analytics separate between environments and portal / qrposter

## [2.0.3] - 2021-05-14

## Updated

- Skip basicauth on /status for dns health checks

## [2.0.2] - 2021-05-13

## Updated

- Added a temporary user/pass for registration site to prevent early access
- Fixed a language switch bug when in an environment with dual domains (ie, production)

## [2.0.1] - 2021-05-12

### Updated

- Added English and French URL config for Registration Site to fix language switching

## [2.0] - 2021-05-12

### Added

- QR Code Registration site
- Portal QR Code Venue search and Outbreak features

## [1.19.4] - 2021-04-28

### Updated

- Fix for manage profiles page when showing last password change timestamp

## [1.19.3] - 2021-04-08

### Updated

- Update Django to 3.2
- Content changes for Portal iteration v1.1

## [1.19.2] - 2021-03-17

### Updated

- Update Django dependencies
- Update screenshots to reflect updated App menu

## [1.19.1] - 2021-02-25

### Added

- The initial flow for creating outbreak alert notifications. This includes:
  - A new app named 'outbreak' with a 'notification' model
  - A new main menu navigation only accessible for users with 'can_send_alert' permission
  - A new flow for creating these alert notifications, if permitted
  
## [1.18.1] - 2021-02-12

### Added

- New AWS infrastructure for hosting a separate ECS task for QR Code registration
- Modified Portal Django project so that it can host either the Portal or the QR Code registration

## [1.17.1] - 2021-01-29

### Added

- OTK sent via SMS using new html pages
- OTK is temporarily cached in the session

## [1.16.1] - 2021-01-27

### Updated

- Added some context to the Support page for when to contact portal team vs admin

## [1.16.0] - 2021-01-19

### Added

- Added the Northern Inter-Tribal Health Authority as their own province

## [1.15.1] - 2021-01-11

### Updated

- Changed HTML rendering for backup codes so they won't be duplicated when copied
- More explicit content around saving your backup codes

## [1.15.0] - 2021-01-07

### Added

- Added a confirmation email that is sent to new users upon successful signup

### Updated

- Added package "dependency-injector" for managing the GC notification client as a service.
  This is a code refactor and doesn't affect functionality.

## [1.14.0] - 2021-01-06

### Added

- Add accordion-like "side" nav for mobile-sized about pages

### Updated

- Updated content for backup code pages and password rules
- Prevent visually-hidden text from being selectable
- Remove bottom padding from main nav links on mobile

## [1.13.0] - 2020-12-16

### Added

- Split the "start" page into 2 new pages
  - Page 1 to ask if this patient is positive and has the app on their phone?
  - Page 2 to ask if this patient is ready to enter the code or write it down somewhere
  - Change "start" link in main nav to "Generate keys"
  - Added a green "start" GOV.UK type-button

### Updated

- Remove h3s in About section: use h2s instead
- Resize h2s, make them smaller
- Minor content updates to account page and 2FA flow

## Removed

- Remove "Next" link to Support page from the "Admin accounts" page
- Remove "Welcome" page
  - No 301 redirect for the "welcome" URL because there was no in-app link to it
  - New users are now directed to the "start" page

## [1.12.1] - 2020-12-11

### Updated

- "Main" nav now visible for not-logged-in users

## [1.12.0] - 2020-12-11

### Added

- Added new "About the Portal" section
  - Included in the main navigation and has a new page layout
  - Mostly it is the content in the Quick guide, but broken up into more manageable sections
- Added new "Support" page
  - Replaces "Contact us" in the main nav

### Updated

- Announcement banners are now full-screen (except on the login page)

## Removed

- Remove "Quick guide" page
  - 301 redirect the old URL to the new about page

## [1.11.2] - 2020-12-03

### Removed

- Remove BACKUP_CODE feature flag now that backup codes rollout has gone swimmingly

## [1.11.1] - 2020-12-4

#### ⚠️ This release includes a data migration

### Updated

- Updated the privacy pages to include new text about Google Analytics.
- Added Goolge Analytics tag placeholder and configurator through admin portal.

## [1.11.0] - 2020-12-01

#### ⚠️ This release includes a data migration

- Add static backup codes
  - On user account page: see codes and generate more codes
  - On signup: new accounts can create codes instead of adding a phone
  - On login: login accepts a backup code, and allows users to message an administrator
  - On attempted login: lock out users after a set number of failed 2FA attempts
  - If not able to log in: users can request a backup code from their administrator
  - On generating codes: print styles for the backup codes

## [1.10.6] - 2020-11-27

### Fixed

- Red delete button on the "Delete yubikey" page (missed this earlier)

## [1.10.5] - 2020-11-27

### Updated

- Change the maintenance page text in EN and FR for our scheduled maintenance.

## [1.10.4] - 2020-11-26

#### ⚠️ This release includes a data migration

### Updated

- Add the ability to create a site wide or user specific site banner.

## [1.10.3] - 2020-11-26

### Updated

- Remove STMP email configuration and ADMINS variable
  - Note: this is not a user-facing change but updating the version so that we can release independently

## [1.10.2] - 2020-11-16

### Updated

- List users under "Manage team" alphabetically by email address
- "Delete" buttons are red (ie, they are destructive actions) and horizontal

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
