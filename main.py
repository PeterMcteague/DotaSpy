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
from heroes import heroList

#API setup (If no file, ask for entry and save, otherwise skip).
def setup():
    #Variable setup
    #Look for file
    #If exist
    if os.path.exists("apikey.txt"):
        #We do nothing here as we're calling main anyway.
        main()
    else:
    #If not exist
        #A function to check whether the API key looks valid
        def checkKey():
            if len(apiKey.get()) == 32:
                #Create file
                apikeyFile = open("apikey.txt",'a')
                #Save to file
                apikeyFile.write(apiKey.get())
                apikeyFile.close()
                SetupWindow.destroy()
                main()
            else:
                tk.messagebox.showinfo("Invalid API Key", "The API Key you've entered is invalid. Try again.")
        def openAPILink(event):
            webbrowser.open_new("http://steamcommunity.com/dev/apikey")
        #Create gui with link to key generation site and with a place to enter it
        #Graphics variables initialisation
        WindowBackgroundColor = "#bdc3c7"
        WindowWidth = "600"
        WindowHeight = "200"
        SetupFont = 'Times New Roman'
        #Window creation
        SetupWindow = tk.Tk()
        SetupWindow.resizable(width="FALSE", height="FALSE")
        SetupWindow.attributes("-fullscreen", False)
        SetupWindow.title('Dota 2 Player Information Getter - First time setup')
        SetupWindow.configure(background=WindowBackgroundColor)
        #Setting the window size and placing it to 0.35*Screen width and 0.3*Screen height. Had to cast to int twice to get rid of decimal points.
        SetupWindow.geometry(WindowWidth + "x" + WindowHeight + "+" + str(int(int(SetupWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(SetupWindow.winfo_screenheight() * 0.3)))) 
        #Window variable initialisation
        apiKey = tk.StringVar()
        tk.Label(SetupWindow, text = "Setup"
                 , font = (SetupFont,16), background = WindowBackgroundColor, fg="#ffffff").place(x=0, y=0)
        tk.Label(SetupWindow, text = "  An API key is required to pull information from Dota 2 matches."
                 , font = (SetupFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=50, y=30)
        APIKeyLabel = tk.Label(SetupWindow, text = "Please enter an API key from http://steamcommunity.com/dev/apikey."
                 , font = (SetupFont,14), background = WindowBackgroundColor, fg="#ffffff")
        APIKeyLabel.place(x=50, y=55)
        APIKeyLabel.bind("<Button-1>", openAPILink)
        APIKeyEntry = tk.Entry(SetupWindow, bd = 0, font = (SetupFont,12), exportselection=0, textvariable = apiKey, width=40).place(x=125,y=105)
        tk.Button(SetupWindow, text ="Okay", command= checkKey, bg= "#95a5a6", relief='flat').place(x=450,y=102)

def main():
    def setupKey():
        MainWindow.destroy()
        os.remove("apikey.txt")
        setup()
    def getData():
        #First let's set our global variables. This isn't the way it should be done. We should be using functions. However, buttons make this hard.
        global heroList
        global CoreCount
        global SupportCount
        #First we reset our hero list if it exists
        if heroList:
            for count in range(0,len(heroList)):
               heroList[count][2] = 0
        from heroes import heroList
        #Here we're turning the entered profile URL into a SteamID. Key is the api key, vanityurl is the end part of the URL (I.e. in http://steamcommunity.com/id/GabeN/ it's GabeN).
        #We also get the text at that URL, decode it as UTF-8 then load it as a JSON.
        #As steam url's can either be in the format http://steamcommunity.com/profiles/SteamID/ or http://steamcommunity.com/id/VanityName, we have to work with both.
        #If using vanityurl
        global steamID
        if steamURL.get()[26:28] == "id":
            SteamUserJson = json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + apikey + "&vanityurl=" + steamURL.get()[29:-1] + "&format=JSON").read()).decode('utf-8'))
            if SteamUserJson["response"]["success"] == 1:
                #Set steamID to the value from here.
                #I would've liked to have returned steamID and kept it local, but it didn't turn out that way. It shouldn't be a bad thing as at this point it's essentially global anyway.
                steamID = (SteamUserJson["response"]["steamid"])
            else:
                tk.messagebox.showinfo("Error", "There was an error with the request. Please try again later.")
                return
        #If not
        elif steamURL.get()[26:28] == "pr":
            steamID = steamURL.get()[35:-1]
        #If invalid steamID
        else:
            tk.messagebox.showinfo("Error", "Steam URL invalid. Please enter a valid one.")
            return
        #Now we're going to get some info about the players steam profile including their avatar and name, using that steamID
        #If no players found for that steamid
        if (json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + apikey + "&steamids=" + steamID + "&format=JSON").read()).decode('utf-8'))["response"]["players"] == []):
            tk.messagebox.showinfo("Error", "Steam URL invalid. Please enter a valid one.")
            return
        #If players found
        else:
            SteamUserJson = json.loads((urllib.request.urlopen("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + apikey + "&steamids=" + steamID + "&format=JSON").read()).decode('utf-8'))
        global steamName
        steamName = SteamUserJson["response"]["players"][0]["personaname"]
        global steamNationality
        if "loccountrycode" in SteamUserJson["response"]["players"][0]:
            steamNationality = "[" + SteamUserJson["response"]["players"][0]["loccountrycode"] + "]"
        else:
            steamNationality = ""
        global steamAvatarURL
        steamAvatarURL = SteamUserJson["response"]["players"][0]["avatarfull"]
        #Calculating hero information
        #Variable setup
        CoreCount = 0 #Keeps a count of the number of core heroes played
        SupportCount = 0 #Keeps a count of the number of support heroes played
        #This would be found by getting the heroes that they've played and counting the number of cores and supports.
        #First we need to make a call of the api for the players match history using their 64bit steamid. E.g. http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1/?key=KEY&account_id=64BitSteamID
        #We request the last 50 matches of that player.
        MatchesToGet = 50
        MatchHistory = (json.loads((urllib.request.urlopen("http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1/?key=" + apikey + "&account_id=" + steamID + "&format=JSON&matches_requested=" + str(MatchesToGet)).read()).decode('utf-8')))
        if MatchHistory["result"]["status"] == 1:
            #Then we find for each match the heroid of the player with accountid SteamID - 76561197960265728 to give us the 32BitSteamID.
            #For each match returned
            for MatchNumber in range(0,(MatchesToGet - 1)):
                #For regular 5v5 games only
                if MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 0 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 5 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 6 or MatchHistory["result"]["matches"][MatchNumber]["lobby_type"] == 7:
                    #For each player in the match
                    for PlayerPosition in range(0,9):
                        #If the selected player has the 32Bit SteamID of the player searched for
                        if MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["account_id"] == (int(steamID) - 76561197960265728):
                            #Adds to the count of support or core
                            if (heroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][1]).lower() == "core":
                                CoreCount = CoreCount + 1
                            elif (heroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][1]).lower() == "support":
                                SupportCount = SupportCount + 1
                            #Increments timesplayed
                            heroList[int(MatchHistory["result"]["matches"][MatchNumber]["players"][PlayerPosition]["hero_id"]) - 1][2] += 1  
        else:
            tk.messagebox.showinfo("Error 15", "Cannot get match history for a user that hasn't allowed it.")
        MainWindow.destroy()
        main()
    #Get apikey
    apikeyFile=open("apikey.txt", 'r')
    apikey = apikeyFile.readline()
    apikeyFile.close()
    #Create UI
    WindowBackgroundColor = "#bdc3c7"
    WindowWidth = "800"
    WindowHeight = "800"
    MainFont = 'Times New Roman'
    MainWindow = tk.Tk()
    MainWindow.resizable(width="FALSE", height="FALSE")
    MainWindow.attributes("-fullscreen", False)
    MainWindow.title('Dota 2 Player Information Getter')
    MainWindow.configure(background=WindowBackgroundColor)
    MainWindow.geometry(WindowWidth + "x" + WindowHeight + "+" + str(int(int(MainWindow.winfo_screenwidth()) * 0.35)) + "+" + str(int(int(MainWindow.winfo_screenheight() * 0.1)))) 
    #Create button that links back to setup
    tk.Button(MainWindow, text ="Setup", command= setupKey, bg= "#95a5a6", relief='flat', height = 5, width = 10).place(x=720,y=720)
    #Create button and box for steamID
    steamURL = tk.StringVar()
    tk.Label(MainWindow, text = "Steam Profile Link: "
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=0, y=2)
    SteamIDEntry = tk.Entry(MainWindow, bd = 0, font = (MainFont,12), exportselection=0, textvariable = steamURL, width=40).place(x=155,y=5)
    tk.Button(MainWindow, text ="Submit", command= lambda: getData(), bg= "#95a5a6", relief='flat').place(x=485,y=2)
    #Display info if steamID is set
    if 'steamID' in globals():
        #Display SteamID under entry
        tk.Label(MainWindow, text = "Steam ID: " + steamID
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=0, y=40)
        
        #Display steam avatar
        data_stream = io.BytesIO(urllib.request.urlopen(steamAvatarURL).read())
        # open as a PIL image object
        pil_image = Image.open(data_stream)
        tk_image = ImageTk.PhotoImage(pil_image)
        tk.Label(MainWindow, background = WindowBackgroundColor, image = tk_image, width=184, height=184).place(x=0, y=80)
        #Display steam name and nationality
        tk.Label(MainWindow, text = steamName + " " + steamNationality
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=200, y=80)
        
        #Display hero role
        if CoreCount > SupportCount:
            tk.Label(MainWindow, text = "Core"
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
        elif SupportCount > CoreCount:
            tk.Label(MainWindow, text = "Support"
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)
        elif CoreCount == SupportCount:
            tk.Label(MainWindow, text = "In your last " + str(MatchesToGet) + " matches, you've played support and core heroes equally."
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=200, y=110)

        #Display 3 most played heroes
        #Sort hero list by played
        global heroList
        heroList = sorted(heroList, key=lambda timesPlayed: timesPlayed[2])
        #Display
        tk.Label(MainWindow, text = "3 Most played heroes:"
                 , font = (MainFont,14), background = WindowBackgroundColor, fg="#ffffff").place(x=0, y=300)
        heroPhoto1 = ImageTk.PhotoImage(file="images/" + str(heroList[-1][0]) + ".png")
        tk.Label(MainWindow, background = WindowBackgroundColor, image = heroPhoto1, width=80, height=45).place(x=0, y=330)
        heroPhoto2 = ImageTk.PhotoImage(file="images/" + str(heroList[-2][0]) + ".png")
        tk.Label(MainWindow, background = WindowBackgroundColor, image = heroPhoto2, width=80, height=45).place(x=80, y=330)
        heroPhoto3 = ImageTk.PhotoImage(file="images/" + str(heroList[-3][0]) + ".png")
        tk.Label(MainWindow, background = WindowBackgroundColor, image = heroPhoto3, width=80, height=45).place(x=160, y=330)
    MainWindow.mainloop()
setup()
