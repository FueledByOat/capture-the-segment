# Strava Club Segment Scraper

This repository contains a two-step Python automation tool designed to log into Strava, save your session cookies, and then scrape segment leaderboards for a specific Strava Club to calculate tie-based team scores.

## Overview of the Scripts

The process is split into two scripts to safely handle authentication:

1. **Script 1 (Login & Cookie Saver):** Opens a Google Chrome browser and navigates to the Strava login page. You have 30 seconds to manually log in. Once logged in, the script securely saves your session cookies to a local file (`strava_cookies.json`).
2. **Script 2 (Data Scraper):** Reads the saved cookies to bypass the login screen in the background. It visits a predefined list of Strava segments, filters them by your Club ID, extracts the leaderboard for the current week, applies team-based tie scoring, and exports the results to CSV files.

---

## 🛠 Prerequisites

Before running these scripts, you must have the following installed on your computer:
* **Python 3.8 or newer**: You can download it from python.org.
* **Google Chrome**: The login script requires the Chrome browser to be installed.

---

## 📦 Setup Instructions

If you are new to running Python scripts, follow these steps to get your environment ready:

### 1. Install Dependencies
This project includes a `pyproject.toml` file which lists all the required third-party libraries. 

Open your terminal, navigate to the folder containing these files, and run:

`pip install .`

### 2. Configure Your Club ID
Before running the scraping script, you **must** open Script 2 in a text editor and find this line:

`club_id = 123456`

Change `123456` to your actual Strava Club ID.

---

## 🚀 How to Run

### Step 1: Log into Strava
Run the first script from your terminal:

`python script1_login.py`

**What to do:** A Chrome window will pop up. You have exactly **30 seconds** to enter your email, password, and log in. Once 30 seconds pass, the script will automatically close the browser and save a file named `strava_cookies.json` in your folder. 

### Step 2: Scrape the Data
Once `strava_cookies.json` has been successfully created, run the second script:

`python script2_scrape.py`

**What to do:** Just wait! The script will pause randomly between 2 to 7 seconds between pages to mimic human behavior and avoid being blocked by Strava. 

### Outputs
Once finished, Script 2 will generate two files in your folder:
* `leaderboard_ties_scored.csv`: A formatted table of segment times with your team's tie-based scoring headers.
* `raw_name_time_log.csv`: A raw, unformatted log of every name, date, and time extracted.
