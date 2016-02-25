![Logo](https://github.com/HellkatAnarchy/Dota-2-Player-Info-Getter/blob/master/images/dotaspybanner.png?raw=true)

###What is DotaSpy?

DotaSpy is an application that allows a user to gather information about a Dota 2 player using there Steam Profile.
All they have to do is paste the steam profile link in, submit it and they're given the players name, picture, role and most played 3 heroes.

This information is gotten by asking the Steam and Dota API's for information about the players last X games, where X defaults at 50 and can be changed by the user, from 1-100.

###How was it made?

This project was written in Python and uses the following libraries:
Tkinter
os
webbrowser 
urllib (Request)
json
io
PIL (Image, ImageTK)

PIL is Pillow in this case. The program wont run properly unless you have this installed.
To install, follow guide at https://pillow.readthedocs.org/en/3.0.0/installation.html