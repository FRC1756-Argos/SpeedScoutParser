# SpeedScoutParser
Collects csv files from SpeedScout16 and generates an FRC scouting spreadsheet.

## Overview
This software collects emails sent by SpeedScout16 ([Android](https://github.com/dkt01/SpeedScout16-Android)/[iOS](https://itunes.apple.com/us/app/speedscout16-frc-scouting/id1088137228?mt=8)) and uses the scouting data to populate a Google Docs spreadsheet.  This spreadsheet may contain data analysis functionality to help teams in alliance selections.

## Prerequisites
SpeedScoutParser uses the Python interfaces to the following APIs:
 * [Google Drive API](https://developers.google.com/drive/v3/web/quickstart/python) - For accessing a Google Docs spreadsheet
 * [Gmail API](https://developers.google.com/gmail/api/quickstart/python) - For gathering emails from a Gmail account
 * [Google Apps Script API](https://developers.google.com/apps-script/guides/rest/quickstart/python) - For inserting rows into a spreadsheet

Additionally, you must have [Python 2.6 or greater](https://www.python.org/downloads/) installed and using [cron](https://help.ubuntu.com/community/CronHowto) to periodically run SpeedScoutParser requires a Linux/Mac OS/Unix computer.

## config File
The config file contains several parameters specific to your instance of SpeedScoutParser.
