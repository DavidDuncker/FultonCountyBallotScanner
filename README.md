# FultonCountyBallotScanner
Software designed to download and analyze the 2020 presidential ballots in Fulton County, GA

Work in progress.

main.py has all the code to download the ballots. It creates a configuration file that prompts the user for 1) the default browser download folder, 
2) the browser that the user wants to use, and 3) the folder that the user wants to use to store the downloaded data. It then opens 
https://theatlantajournalconstitution.sharefile.com/share/view/s3c2d5cda4b5a42a88b6a76990379d181/fo8028b0-c150-45f5-911d-f9959144930e/ and scrapes
each individual batch of ~100 ballots. Expect the download to take a week.

image_processor.py processes the downloaded ballots. The Image Processing Manager class contains functions that take in a path to a ballot file, 
and manipulates it in a way where it can zero in on certain ballot bubbles, crop to that bubble, and compare filled-in bubbles between two ballots. 
The ScanningCursor class focuses on the rectangles around the margin of the ballot, and attempts to use them to create gridlines within the ballot 
for the purpose of locating a specific bubble and reading the bar code on the bottom left side of the ballot.

Selenium is required for downloading the ballots. Numpy is required for processing the ballots.
