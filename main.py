#This program allows a user to obtain information about a dota 2 player by calling the dota match api for xml files, and parsing the info about the player from these games.
#It should ask the user to first create a steam api key in order to call the api (I cannot be giving people my api key) (This is skipped if the user already has an api key saved (Save this in a file)
#It should then ask for a player to be searched for.
#Then it should show information about that player for the current patch. For example MMR, Most common role, Best 3 heroes, Most played 3 heroes, name, profile picture and more.

#imports here
import tkinter as tk
import os
import webbrowser
import urllib.request
import json
import io
import sys
from PIL import Image, ImageTk

class SetupWindow:
    #A function to check whether the API key looks valid
    def checkKey(self):
        if len(self.apiKey.get()) == 32:
            #Create file
            apikeyFile = open("apikey.txt",'a')
            #Save to file
            apikeyFile.write(self.apiKey.get())
            apikeyFile.close()
            self.SetupWindow.destroy()
            self.CurrentWindow = MainWindow()
        else:
            tk.messagebox.showinfo("Invalid API Key", "The API Key you've entered is invalid. Try again.")
            
    def openAPILink(self,event):
        webbrowser.open_new("http://steamcommunity.com/dev/apikey")
        
    def __init__(self):
        #Create gui with link to key generation site and with a place to enter it
        #Graphics variables initialisation
        self.WindowBackgroundColor = "#bdc3c7"
        self.WindowWidth = "600"
        self.WindowHeight = "200"
        self.SetupFont = 'Times New Roman'
        self.SetupWindow = tk.Tk()
        self.SetupWindow.resizable(width="FALSE", height="FALSE")
        self.SetupWindow.attributes("-fullscreen", False)
        self.SetupWindow.title('Dota 2 Player Information Getter - First time setup')
        self.SetupWindow.configure(background=self.WindowBackgroundColor)
        #Setting the window size and placing it to 0.35*Screen width and 0.3*Screen height. Had to cast to int twice to get rid of decimal points.
        self.SetupWindow.geometry(self.WindowWidth + "x" + self.WindowHeight + "+" + str(int(int(self.SetupWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(self.SetupWindow.winfo_screenheight() * 0.3)))) 
        #Window variable initialisation
        self.apiKey = tk.StringVar()
        tk.Label(self.SetupWindow, text = "Setup"
                 , font = (self.SetupFont,16), background = self.WindowBackgroundColor, fg="#ffffff").place(x=0, y=0)
        tk.Label(self.SetupWindow, text = "  An API key is required to pull information from Dota 2 matches."
                 , font = (self.SetupFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=50, y=30)
        self.APIKeyLabel = tk.Label(self.SetupWindow, text = "Please enter an API key from http://steamcommunity.com/dev/apikey."
                 , font = (self.SetupFont,14), background = self.WindowBackgroundColor, fg="#ffffff")
        self.APIKeyLabel.place(x=50, y=55)
        self.APIKeyLabel.bind("<Button-1>", self.openAPILink)
        self.APIKeyEntry = tk.Entry(self.SetupWindow, bd = 0, font = (self.SetupFont,12), exportselection=0, textvariable = self.apiKey, width=40).place(x=125,y=105)
        tk.Button(self.SetupWindow, text ="Okay", command = self.checkKey, bg= "#95a5a6", relief='flat').place(x=450,y=102)

#Unfinished. Code has only been ported from V1.
class PlayerProfile():
    def fetchSteamID(self):
        #If using a vanity ID for their steam profile
        if self.SteamURL.get()[26:28] == "id":
            #Use Steam user api to resolve vanity ID
            SteamUserJson = json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + CurrentWindow.apikey + "&vanityurl=" + self.SteamURL.get()[29:-1] + "&format=JSON").read()).decode('utf-8'))
            if SteamUserJson["response"]["success"] == 1:
                #Set steamID to the value from here.
                steamID = (SteamUserJson["response"]["steamid"])
            else:
                #If the api returns a failure
                tk.messagebox.showinfo("Error", "There was an error with the request. Please try again later.")
                return "error"
        #If using a regular ID
        elif self.SteamURL.get()[26:28] == "pr":
            steamID = self.SteamURL.get()[35:-1]
        #If what is entered is not a valid Steam URL
        else:
            tk.messagebox.showinfo("Error", "Steam URL invalid. Please enter a valid one.")
            return "error"
        #And now we check if a player has the SteamID that is found
        #If not found
        if (json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + CurrentWindow.apikey + "&steamids=" + steamID + "&format=JSON").read()).decode('utf-8'))["response"]["players"] == []):
            tk.messagebox.showinfo("Error", "Steam URL invalid. Please enter a valid one.")
            return "error"
        #If found
        else:
            self.SteamID = steamID
            return steamID
    def fetchSteamUserJson(self):
        SteamUserJson = json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + CurrentWindow.apikey + "&steamids=" + self.SteamID + "&format=JSON").read()).decode('utf-8'))
        self.SteamUserJson = SteamUserJson
        return SteamUserJson
    def fetchSteamName(self):
        steamName = self.SteamUserJson["response"]["players"][0]["personaname"]
        self.SteamName = steamName
        return steamName
    def fetchSteamNationality(self):
        if "loccountrycode" in self.SteamUserJson["response"]["players"][0]:
            steamNationality = "[" + self.SteamUserJson["response"]["players"][0]["loccountrycode"] + "]"
        else:
            steamNationality = ""
        self.SteamNationality = steamNationality
        return steamNationality
    def fetchSteamAvatarURL(self):
        steamAvatarURL = self.SteamUserJson["response"]["players"][0]["avatarfull"]
        self.SteamAvatarURL = steamAvatarURL
        return steamAvatarURL
    def fetchSteamAvatar(self):
        data_stream = io.BytesIO(urllib.request.urlopen(self.SteamAvatarURL).read())
        # open as a PIL image object
        pil_image = Image.open(data_stream)
        tk_image = ImageTk.PhotoImage(pil_image)
        self.SteamAvatar = tk_image
        return tk_image
    def fetchHeroAndRole(self, MatchesToGet):
        MatchHistory = (json.loads((urllib.request.urlopen("http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1/?key=" + CurrentWindow.apikey + "&account_id=" + self.SteamID + "&format=JSON&matches_requested=" + str(MatchesToGet)).read()).decode('utf-8')))
        if MatchHistory["result"]["status"] == 1:
            #Then we find for each match the heroid of the player with accountid SteamID - 76561197960265728 to give us the 32BitSteamID.
            #For each match returned
            for MatchNumber in range(0,(MatchesToGet - 1)):
                #For regular 5v5 games only
                if MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 0 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 5 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 6 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 7:
                    #For each player in the match
                    for PlayerPosition in range(0,9):
                        #If the selected player has the 32Bit SteamID of the player searched for
                        if MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["account_id"] == (int(self.SteamID) - 76561197960265728):
                            #Adds to the count of support or core
                            if (self.HeroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][1]).lower() == "core":
                                self.CoreCount = self.CoreCount + 1
                            elif (self.HeroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][1]).lower() == "support":
                                self.SupportCount = self.SupportCount + 1
                            #Increments timesplayed
                            self.HeroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][2] += 1  
        else:
            tk.messagebox.showinfo("Error 15", "Cannot get match history for a user that hasn't allowed it.")
    def __init__(self):
        self.SteamURL = CurrentWindow.steamURL
        self.SteamID = ""
        self.SteamUserJson = []
        self.SteamName = ""
        self.SteamNationality = ""
        self.SteamAvatarURL = ""
        self.SteamAvatar = ""
        self.CoreCount = 0
        self.SupportCount = 0
        self.Role = ""
        from heroes import heroList
        self.HeroList = heroList

class MainWindow:
    def setupKey(self):
        self.MainWindow.destroy()
        os.remove("apikey.txt")
        SetupWindow()
    def getData(self):
        #Create PlayerProfile object
        self.PlayerProfile = PlayerProfile()
        #Run object methods and set graphics on MainWindow
        if self.PlayerProfile.fetchSteamID() != "error":
            self.PlayerProfile.fetchSteamUserJson()
            self.PlayerProfile.fetchSteamName()
            self.PlayerProfile.fetchSteamNationality()
            self.PlayerProfile.fetchSteamAvatarURL()
            self.PlayerProfile.fetchSteamAvatar()
            self.PlayerProfile.fetchHeroAndRole(50)
            #Add info gotten to UI
            #Display SteamID under entry
            tk.Label(self.MainWindow, text = "Steam ID: " + self.PlayerProfile.SteamID
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=0, y=40)
            #Display steam avatar
            tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.PlayerProfile.SteamAvatar, width=184, height=184).place(x=0, y=80)
            #Display steam name and nationality
            tk.Label(self.MainWindow, text = self.PlayerProfile.SteamName + " " + self.PlayerProfile.SteamNationality
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=80)
            
            #Display hero role
            if self.PlayerProfile.CoreCount > self.PlayerProfile.SupportCount:
                tk.Label(self.MainWindow, text = "Core"
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
            elif self.PlayerProfile.SupportCount > self.PlayerProfile.CoreCount:
                tk.Label(self.MainWindow, text = "Support"
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
            elif self.PlayerProfile.CoreCount == self.PlayerProfile.SupportCount:
                tk.Label(self.MainWindow, text = "In your last X matches, you've played support and core heroes equally."
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)

            #Display 3 most played heroes
            #Sort hero list by played
            self.PlayerProfile.HeroList = sorted(self.PlayerProfile.HeroList, key=lambda timesPlayed: timesPlayed[2])
            #Display
            tk.Label(self.MainWindow, text = "3 Most played heroes:"
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=0, y=300)
            self.heroPhoto1 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-1][0]) + ".png")
            tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto1, width=80, height=45).place(x=0, y=330)
            self.heroPhoto2 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-2][0]) + ".png")
            tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto2, width=80, height=45).place(x=80, y=330)
            self.heroPhoto3 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-3][0]) + ".png")
            tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto3, width=80, height=45).place(x=160, y=330)
    def __init__(self):
        #Get apikey
        apikeyFile=open("apikey.txt", 'r')
        self.apikey = apikeyFile.readline()
        apikeyFile.close()
        #Create UI
        self.WindowBackgroundColor = "#bdc3c7"
        self.WindowWidth = "800"
        self.WindowHeight = "800"
        self.MainFont = 'Times New Roman'
        self.MainWindow = tk.Tk()
        self.MainWindow.resizable(width="FALSE", height="FALSE")
        self.MainWindow.attributes("-fullscreen", False)
        self.MainWindow.title('Dota 2 Player Information Getter')
        self.MainWindow.configure(background=self.WindowBackgroundColor)
        self.MainWindow.geometry(self.WindowWidth + "x" + self.WindowHeight + "+" + str(int(int(self.MainWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(self.MainWindow.winfo_screenheight() * 0.1)))) 
        #Create button that links back to setup
        tk.Button(self.MainWindow, text ="Setup", command= self.setupKey, bg= "#95a5a6", relief='flat', height = 5, width = 10).place(x=720,y=720)
        #Create button and box for steamID
        self.steamURL = tk.StringVar()
        tk.Label(self.MainWindow, text = "Steam Profile Link: "
                     , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=0, y=2)
        self.SteamIDEntry = tk.Entry(self.MainWindow, bd = 0, font = (self.MainFont,12), exportselection=0, textvariable = self.steamURL, width=40).place(x=155,y=5)
        tk.Button(self.MainWindow, text ="Submit", command= self.getData, bg= "#95a5a6", relief='flat').place(x=485,y=2)


#Look for api key file
#If exist
if os.path.exists("apikey.txt"):
    #We do nothing here as we're calling main anyway.
    #Create MainWindow
    CurrentWindow = MainWindow()
else:
    SetupWindow = SetupWindow()
