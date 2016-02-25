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
            #Make sure currentwindow is given global scope, as code was written for it to be at the top level.
            global CurrentWindow
            CurrentWindow = MainWindow()
        else:
            tk.messagebox.showinfo("Invalid API Key", "The API Key you've entered is invalid. Try again.")
            
    def openAPILink(self,event):
        webbrowser.open_new("http://steamcommunity.com/dev/apikey")
        
    def __init__(self):
        #Create gui with link to key generation site and with a place to enter it
        #Graphics variables initialisation
        self.WindowBackgroundColor = "#bdc3c7"
        self.WindowWidth = "600"
        self.WindowHeight = "300"
        self.SetupFont = 'Times New Roman'
        self.SetupWindow = tk.Tk()
        self.img = ImageTk.PhotoImage(file='images/dotaspyicon.png')
        self.SetupWindow.tk.call('wm', 'iconphoto', self.SetupWindow, self.img)
        self.SetupWindow.resizable(width="FALSE", height="FALSE")
        self.SetupWindow.attributes("-fullscreen", False)
        self.SetupWindow.title('DotaSpy - First time setup')
        self.SetupWindow.configure(background=self.WindowBackgroundColor)
        #Setting the window size and placing it to 0.35*Screen width and 0.3*Screen height. Had to cast to int twice to get rid of decimal points.
        self.SetupWindow.geometry(self.WindowWidth + "x" + self.WindowHeight + "+" + str(int(int(self.SetupWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(self.SetupWindow.winfo_screenheight() * 0.3))))
        #Banner image
        self.banner = ImageTk.PhotoImage(file='images/dotaspybanner.png')
        tk.Label(self.SetupWindow, background = self.WindowBackgroundColor, image = self.banner, width=400, height=100).place(x=100, y=20)
        #Window variable initialisation
        self.apiKey = tk.StringVar()
        tk.Label(self.SetupWindow, text = "Setup"
                 , font = (self.SetupFont,16), background = self.WindowBackgroundColor, fg="#ffffff").place(x=0, y=150)
        tk.Label(self.SetupWindow, text = "  An API key is required to pull information from Dota 2 matches."
                 , font = (self.SetupFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=50, y=180)
        self.APIKeyLabel = tk.Label(self.SetupWindow, text = "Please enter an API key from http://steamcommunity.com/dev/apikey."
                 , font = (self.SetupFont,14), background = self.WindowBackgroundColor, fg="#ffffff")
        self.APIKeyLabel.place(x=50, y=205)
        self.APIKeyLabel.bind("<Button-1>", self.openAPILink)
        self.APIKeyEntry = tk.Entry(self.SetupWindow, bd = 0, font = (self.SetupFont,12), exportselection=0, textvariable = self.apiKey, width=40).place(x=125,y=255)
        tk.Button(self.SetupWindow, text ="Okay", command = self.checkKey, bg= "#95a5a6", relief='flat').place(x=450,y=252)

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
        self.resetHeroList()
        MatchHistory = (json.loads((urllib.request.urlopen("http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1/?key=" + CurrentWindow.apikey + "&account_id=" + self.SteamID + "&format=JSON&matches_requested=" + str(MatchesToGet)).read()).decode('utf-8')))
        if MatchHistory["result"]["status"] == 1:
            #Then we find for each match the heroid of the player with accountid SteamID - 76561197960265728 to give us the 32BitSteamID.
            #For each match returned
            for MatchNumber in range(0,(MatchesToGet)):
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
            tk.messagebox.showinfo("Error 15", "Error, could not get DOTA info.")
    def resetHeroList(self):
        for item in self.HeroList:
            item[2] = 0
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
    def key(self, event):
        self.getData()
    
    def setupKey(self):
        self.MainWindow.destroy()
        os.remove("apikey.txt")
        SetupWindow()
        
    def getData(self):
        #Only allow data to be gotten if MatchesToGet < 100 > 0 and type int.
        try:
            if 100 >= self.MatchesToGet.get() > 0:
                #Create PlayerProfile object
                self.PlayerProfile = PlayerProfile()
                #Run object methods and set graphics on MainWindow
                if self.PlayerProfile.fetchSteamID() != "error":
                    #Get rid of error label
                    self.ErrorLabel = tk.Label(self.MainWindow, text = ""
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff", width = 80, height = 6).place(x=0, y=50)
                    self.ErrorLabel2 = tk.Label(self.MainWindow, text = ""
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff", width = 71, height = 5).place(x=0, y=180)   
                    self.PlayerProfile.fetchSteamUserJson()
                    self.PlayerProfile.fetchSteamName()
                    self.PlayerProfile.fetchSteamNationality()
                    self.PlayerProfile.fetchSteamAvatarURL()
                    self.PlayerProfile.fetchSteamAvatar()
                    self.PlayerProfile.fetchHeroAndRole(self.MatchesToGet.get())
                    #Add info gotten to UI
                    #Display SteamID under entry
                    tk.Label(self.MainWindow, text = "Steam ID: " + self.PlayerProfile.SteamID
                             , font = (self.MainFont,12), background = self.WindowBackgroundColor, fg="#ffffff", height = 1).place(x=0, y=50)
                    #Display steam avatar
                    tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.PlayerProfile.SteamAvatar, width=184, height=184).place(x=0, y=80)
                    #Display steam name and nationality
                    tk.Label(self.MainWindow, text = self.PlayerProfile.SteamName + " " + self.PlayerProfile.SteamNationality
                             , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=80)
                    #Display hero role
                    if self.PlayerProfile.CoreCount > self.PlayerProfile.SupportCount:
                        self.RoleLabel = tk.Label(self.MainWindow, text = "Core                                                                  "
                             , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
                    elif self.PlayerProfile.SupportCount > self.PlayerProfile.CoreCount:
                        self.RoleLabel = tk.Label(self.MainWindow, text = "Support                                                               "
                             , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
                    elif self.PlayerProfile.CoreCount == self.PlayerProfile.SupportCount == 0:
                        self.RoleLabel = tk.Label(self.MainWindow, text = str(self.PlayerProfile.SteamName) + " either has a private profile or does not play Dota."
                             , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
                    elif self.PlayerProfile.CoreCount == self.PlayerProfile.SupportCount:
                        self.RoleLabel = tk.Label(self.MainWindow, text = "In this players last " + self.MatchesToGet.get() +  " matches, they've played support and core heroes equally."
                             , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
                    #Sort hero list by played
                    self.PlayerProfile.HeroList = sorted(self.PlayerProfile.HeroList, key=lambda timesPlayed: timesPlayed[2])
                    
                    #Display
                    #Display the last heroes played message                                    
                    if self.MatchesToGet.get() == 1:
                        tk.Label(self.MainWindow, text = "Last hero played:               "
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=160)
                    elif self.MatchesToGet.get() == 2: 
                        tk.Label(self.MainWindow, text = "Last 2 heroes played:           "
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=160)
                    elif self.MatchesToGet.get() == 3:
                        tk.Label(self.MainWindow, text = "Last 3 heroes played:           "
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=160)
                    else:
                        tk.Label(self.MainWindow, text = "Top 3 heroes played:            "
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff").place(x=200, y=160)

                    #Here we display the appropriate number of hero images and played count for the contents of the hero list.
                    #If no heroes played
                    if self.PlayerProfile.HeroList[-1][2] == 0:
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, width=12, height=7).place(x=0, y=300)
                    else:
                        #Display a thematic break label
                        self.seperator = ImageTk.PhotoImage(file="images/seperator.png")
                        tk.Label(self.MainWindow, background = "#ffffff", fg = "#ffffff", image = self.seperator, width=580, height= 1).place(x=200, y=145)
                        #Display photo and times played
                        self.heroPhoto1 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-1][0]) + ".png")
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto1, width=80, height=45).place(x=200, y=190)
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, text = str(self.PlayerProfile.HeroList[-1][2]),font = (self.MainFont,14), width=1, height=1, fg="#ffffff").place(x=240, y=240)
                    #If one hero played
                    if self.PlayerProfile.HeroList[-2][2] == 0:
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, width=12, height=7).place(x=80, y=310)
                    else:
                        self.heroPhoto2 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-2][0]) + ".png")
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto2, width=80, height=45).place(x=280, y=190)
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, text = str(self.PlayerProfile.HeroList[-2][2]),font = (self.MainFont,14), width=1, height=1, fg="#ffffff").place(x=320, y=240)
                    #If two heroes played
                    if self.PlayerProfile.HeroList[-3][2] == 0:
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, width=12, height=7).place(x=160, y=310)
                    else:
                        self.heroPhoto3 = ImageTk.PhotoImage(file="images/" + str(self.PlayerProfile.HeroList[-3][0]) + ".png")
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, image = self.heroPhoto3, width=80, height=45).place(x=360, y=190)
                        tk.Label(self.MainWindow, background = self.WindowBackgroundColor, text = str(self.PlayerProfile.HeroList[-3][2]),font = (self.MainFont,14), width=1, height=1, fg="#ffffff").place(x=400, y=240)
                        
                else:
                    #Cover the info up
                    self.ErrorLabel = tk.Label(self.MainWindow, text = "Error, profile not found or invalid."
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff", width = 80, height = 6).place(x=0, y=50)
                    self.ErrorLabel2 = tk.Label(self.MainWindow, text = " "
                                 , font = (self.MainFont,14), background = self.WindowBackgroundColor, fg="#ffffff", width = 71, height = 5).place(x=0, y=180)  
            else:
                tk.messagebox.showinfo("Error", "The number of games to scan must be in the range 1-100.")
                return    
        except tk.TclError:
            tk.messagebox.showinfo("Error", "Please enter a number.")
            return
        
    def __init__(self):
        #Get apikey
        apikeyFile=open("apikey.txt", 'r')
        self.apikey = apikeyFile.readline()
        apikeyFile.close()
        #Create UI
        self.WindowBackgroundColor = "#bdc3c7"
        self.WindowWidth = "800"
        self.WindowHeight = "265"
        self.MainFont = 'Times New Roman'
        self.MainWindow = tk.Tk()
        self.MainWindow.bind("<Return>", self.key)
        self.img = ImageTk.PhotoImage(file='images/dotaspyicon.png')
        self.MainWindow.tk.call('wm', 'iconphoto', self.MainWindow, self.img)
        self.MainWindow.resizable(width="FALSE", height="FALSE")
        self.MainWindow.attributes("-fullscreen", False)
        self.MainWindow.title('DotaSpy')
        self.MainWindow.configure(background=self.WindowBackgroundColor)
        self.MainWindow.geometry(self.WindowWidth + "x" + self.WindowHeight + "+" + str(int(int(self.MainWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(self.MainWindow.winfo_screenheight() * 0.1)))) 
        #Create button that links back to setup
        tk.Button(self.MainWindow, text ="Setup", command= self.setupKey, bg= "#95a5a6", relief='flat', height = 5, width = 10).place(x=720,y=180)
        #A label for the top header
        tk.Label(self.MainWindow, text = " "
                     , font = (self.MainFont,14), background = '#861111', fg="#ffffff", height = 2, width = 200).place(x=0, y=0)
        #The contents of the top header
        #Icon
        self.banner = ImageTk.PhotoImage(file='images/dotaspyiconsm.png')
        tk.Label(self.MainWindow, background = "#861111", image = self.banner, width=40, height=40).place(x=0, y=0)
        #Link text
        tk.Label(self.MainWindow, text = "Steam Profile Link: "
                     , font = (self.MainFont,14), background = '#861111', fg="#ffffff").place(x=50, y=8)
        #Entry field and button for SteamID
        self.steamURL = tk.StringVar()
        self.SteamIDEntry = tk.Entry(self.MainWindow, bd = 0, font = (self.MainFont,12), exportselection=0, textvariable = self.steamURL, width=40).place(x=205,y=11)
        tk.Button(self.MainWindow, text ="Submit", command= self.getData, bg= "#95a5a6", relief='flat').place(x=535,y=8)
        #Matches to get entry
        tk.Label(self.MainWindow, text = "Scan last X games: "
                     , font = (self.MainFont,14), background = '#861111', fg="#ffffff").place(x=600, y=8)
        self.MatchesToGet = tk.IntVar()
        self.MatchesToGet.set(50)
        self.MatchesToGetEntry = tk.Entry(self.MainWindow, bd = 0, font = (self.MainFont,12), exportselection=0, textvariable = self.MatchesToGet, width=4).place(x = 750,y=11)

#Look for api key file
#If exist
if os.path.exists("apikey.txt"):
    #Create MainWindow
    CurrentWindow = MainWindow()
else:
    #Create SetupWindow
    SetupWindow = SetupWindow()
