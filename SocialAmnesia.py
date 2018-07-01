# standard python imports
from tkinter import *
from tkinter.ttk import *
import os
from pathlib import Path

# local files
from reddit import *
from twitter import *

# cx_freeze needs this import to run
from multiprocessing import Queue

# define tkinter UI
root = Tk()

# create the storage folder
storageFolder = Path(f'{os.path.expanduser("~")}/.SocialAmnesia')
redditStorageFolder = Path(f'{os.path.expanduser("~")}/.SocialAmnesia/reddit')
if not os.path.exists(storageFolder):
    os.makedirs(storageFolder)
    os.makedirs(redditStorageFolder)

# If the user needs to be informed of an error, this will let tkinter take
#   care of that
def callbackError(self, *args):
    # reddit error, happens if you try to run `reddit.user.me()`
    #   and login fails
    if (str(args[1]) == 'received 401 HTTP response'):
        messagebox.showerror('Error', 'Failed to login to reddit!')
    elif (str(args[1]) == "'user'"):
        messagebox.showerror('Error', 'You are not logged into reddit!')
    elif (str(args[1]) == "[{'code': 215, 'message': 'Bad Authentication data.'}]"):
        messagebox.showerror('Error', 'Failed to login to twitter!')
    elif (str(args[1]) == 'list index out of range'):
        messagebox.showerror('Error', 'No tweets or favorites found!')
    elif(str(args[1]) == "'api'"):
        messagebox.showerror('Error', 'You are not logged in to twitter!')
    else:
        messagebox.showerror('ERROR', str(args[1]))


# Builds a list of numbers from 0 up to `max`.
def buildNumberList(max):
    numList = []
    for i in range(0, max):
        numList.append(str(i))
    return numList


# Builds the tab that lets the user log into their social media accounts
def buildLoginTab(loginFrame):
    loginFrame.grid()

    # reddit login
    redditLabel = Label(loginFrame, text='reddit')
    redditLabel.config(font=('arial', 25))

    redditUsernameLabel = Label(loginFrame, text='Enter reddit username:')
    redditUsernameEntry = Entry(loginFrame)

    redditPasswordLabel = Label(loginFrame, text='Enter reddit password:')
    redditPasswordEntry = Entry(loginFrame)

    redditClientIDLabel = Label(loginFrame, text='Enter reddit client ID:')
    redditClientIDEntry = Entry(loginFrame)

    redditClientSecretLabel = Label(
        loginFrame, text='Enter reddit client secret:')
    redditClientSecretEntry = Entry(loginFrame)

    redditLoginConfirmText = StringVar()
    redditLoginConfirmText.set('Waiting for Login')
    redditLoginConfirmedLabel = Label(
        loginFrame, textvariable=redditLoginConfirmText)

    redditLoginButton = Button(
        loginFrame,
        text='Login to reddit',
        command=lambda: setRedditLogin(redditUsernameEntry.get(),
                                       redditPasswordEntry.get(),
                                       redditClientIDEntry.get(),
                                       redditClientSecretEntry.get(),
                                       redditLoginConfirmText,
                                       False)
    )

    # twitter login
    twitterLabel = Label(loginFrame, text='twitter')
    twitterLabel.config(font=('arial', 25))

    twitterConsumerKeyLabel = Label(loginFrame, text='Enter twitter Consumer Key:')
    twitterConsumerKeyEntry = Entry(loginFrame)

    twitterConsumerSecretLabel = Label(
        loginFrame, text='Enter twitter Consumer Secret:')
    twitterConsumerSecretEntry = Entry(loginFrame)

    twitterAccessTokenLabel = Label(
        loginFrame, text='Enter twitter Access Token:')
    twitterAccessTokenEntry = Entry(loginFrame)

    twitterAccessTokenSecretLabel = Label(
        loginFrame, text='Enter twitter Access Token Secret:')
    twitterAccessTokenSecretEntry = Entry(loginFrame)

    twitterLoginConfirmText = StringVar()
    twitterLoginConfirmText.set('Waiting for Login')
    twitterLoginConfirmedLabel = Label(
        loginFrame, textvariable=twitterLoginConfirmText)

    twitterLoginButton = Button(
        loginFrame,
        text='Login to twitter',
        command=lambda: setTwitterLogin(twitterConsumerKeyEntry.get(),
                                       twitterConsumerSecretEntry.get(),
                                       twitterAccessTokenEntry.get(),
                                       twitterAccessTokenSecretEntry.get(),
                                       twitterLoginConfirmText)
    )

    # build the login frame
    redditLabel.grid(row=0, column=0, columnspan=2)
    redditUsernameLabel.grid(row=1, column=0)
    redditUsernameEntry.grid(row=1, column=1)
    redditPasswordLabel.grid(row=2, column=0)
    redditPasswordEntry.grid(row=2, column=1)
    redditClientIDLabel.grid(row=3, column=0)
    redditClientIDEntry.grid(row=3, column=1)
    redditClientSecretLabel.grid(row=4, column=0)
    redditClientSecretEntry.grid(row=4, column=1)
    redditLoginButton.grid(row=5, column=0)
    redditLoginConfirmedLabel.grid(row=5, column=1)

    twitterLabel.grid(row=0, column=2, columnspan=2)
    twitterConsumerKeyLabel.grid(row=1, column=2)
    twitterConsumerKeyEntry.grid(row=1, column=3)
    twitterConsumerSecretLabel.grid(row=2, column=2)
    twitterConsumerSecretEntry.grid(row=2, column=3)
    twitterAccessTokenLabel.grid(row=3, column=2)
    twitterAccessTokenEntry.grid(row=3, column=3)
    twitterAccessTokenSecretLabel.grid(row=4, column=2)
    twitterAccessTokenSecretEntry.grid(row=4, column=3)
    twitterLoginButton.grid(row=5, column=2)
    twitterLoginConfirmedLabel.grid(row=5, column=3)

    # If a praw.ini file exists, log in to reddit
    prawConfigFile = Path(
        f'{os.path.expanduser("~")}/.config/praw.ini')
    if prawConfigFile.is_file():
        setRedditLogin('', '', '', '', redditLoginConfirmText, True)


# Builds the tab that will handle reddit configuration and actions
def buildRedditTab(redditFrame):
    redditFrame.grid()

    # Configuration section title
    configurationLabel = Label(redditFrame, text='Configuration')
    configurationLabel.config(font=('arial', 25))

    # Configuration to set total time of items to save
    currentTimeToSave = StringVar()
    currentTimeToSave.set('Currently set to save: [nothing]')
    timeKeepLabel = Label(
        redditFrame, text='Keep comments/submissions younger than: ')

    hoursDropDown = Combobox(redditFrame, width=2)
    hoursDropDown['values'] = buildNumberList(24)
    hoursDropDown['state'] = 'readonly'
    hoursDropDown.current(0)

    daysDropDown = Combobox(redditFrame, width=2)
    daysDropDown['values'] = buildNumberList(7)
    daysDropDown['state'] = 'readonly'
    daysDropDown.current(0)

    weeksDropDown = Combobox(redditFrame, width=2)
    weeksDropDown['values'] = buildNumberList(52)
    weeksDropDown['state'] = 'readonly'
    weeksDropDown.current(0)

    yearsDropDown = Combobox(redditFrame, width=2)
    yearsDropDown['values'] = buildNumberList(15)
    yearsDropDown['state'] = 'readonly'
    yearsDropDown.current(0)

    hoursLabel = Label(redditFrame, text='hours')
    daysLabel = Label(redditFrame, text='days')
    weeksLabel = Label(redditFrame, text='weeks')
    yearsLabel = Label(redditFrame, text='years')

    timeCurrentlySetLabel = Label(
        redditFrame, textvariable=currentTimeToSave)
    setTimeButton = Button(
        redditFrame,
        text='Set Total Time To Keep',
        command=lambda: setRedditTimeToSave(
            hoursDropDown.get(), daysDropDown.get(),
            weeksDropDown.get(), yearsDropDown.get(), currentTimeToSave)
    )

    # Configuration to set saving items with a certain amount of upvotes
    currentMaxScore = StringVar()
    currentMaxScore.set('Currently set to: 0 upvotes')
    maxScoreLabel = Label(
        redditFrame, text='Delete comments/submissions less than score:')
    maxScoreEntryField = Entry(redditFrame, width=5)
    maxScoreCurrentlySetLabel = Label(
        redditFrame, textvariable=currentMaxScore)
    setMaxScoreButton = Button(
        redditFrame,
        text='Set Max Score',
        command=lambda: setRedditMaxScore(maxScoreEntryField.get(), currentMaxScore)
    )
    setMaxScoreUnlimitedButton = Button(
        redditFrame,
        text='Set Unlimited',
        command=lambda: setRedditMaxScore('Unlimited', currentMaxScore)
    )

    # Configuration to let user skip over gilded comments
    gildedSkipBool = IntVar()
    gildedSkipLabel = Label(redditFrame, text='Skip Gilded comments:')
    gildedSkipCheckButton = Checkbutton(
        redditFrame, variable=gildedSkipBool, command=lambda: setRedditGildedSkip(gildedSkipBool))

    # Allows the user to actually delete comments or submissions
    deletionSectionLabel = Label(redditFrame, text='Deletion')
    deletionSectionLabel.config(font=('arial', 25))

    currentlyDeletingText = StringVar()
    currentlyDeletingText.set('')
    deletionProgressLabel = Label(
        redditFrame, textvariable=currentlyDeletingText)

    deletionProgressBar = Progressbar(
        redditFrame, orient='horizontal', length=100, mode='determinate')

    numDeletedItemsText = StringVar()
    numDeletedItemsText.set('')
    numDeletedItemsLabel = Label(redditFrame, textvariable=numDeletedItemsText)

    deleteCommentsButton = Button(
        redditFrame,
        text='Delete comments',
        command=lambda: deleteRedditItems(
            root, True, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    deleteSubmissionsButton = Button(
        redditFrame,
        text='Delete submissions',
        command=lambda: deleteRedditItems(
            root, False, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    testRunBool = IntVar()
    testRunBool.set(1)
    testRunText = 'TestRun - Checking this will show you what would be deleted, without deleting anything'
    testRunCheckButton = Checkbutton(
        redditFrame, text=testRunText, variable=testRunBool, command=lambda: setRedditTestRun(testRunBool))

    # Allows the user to schedule runs
    schedulerSectionLabel = Label(redditFrame, text='Scheduler')
    schedulerSectionLabel.config(font=('arial', 25))

    schedulerRedditBool = IntVar()
    schedulerRedditText = 'Select to delete reddit comments + submissions daily at'

    hoursSelectionDropDown = Combobox(redditFrame, width=2)
    hoursSelectionDropDown['values'] = buildNumberList(24)
    hoursSelectionDropDown['state'] = 'readonly'
    hoursSelectionDropDown.current(0)

    schedulerRedditCheckButton = Checkbutton(redditFrame, text=schedulerRedditText, variable=schedulerRedditBool, command=lambda: setRedditScheduler(
        root, schedulerRedditBool, int(hoursSelectionDropDown.get()), StringVar(), Progressbar()))

    # This part actually builds the reddit tab
    configurationLabel.grid(row=0, columnspan=11, sticky=(N, S), pady=5)

    timeKeepLabel.grid(row=1, column=0)
    hoursDropDown.grid(row=1, column=1, sticky=(W))
    hoursLabel.grid(row=1, column=2, sticky=(W))
    daysDropDown.grid(row=1, column=3, sticky=(W))
    daysLabel.grid(row=1, column=4, sticky=(W))
    weeksDropDown.grid(row=1, column=5, sticky=(W))
    weeksLabel.grid(row=1, column=6, sticky=(W))
    yearsDropDown.grid(row=1, column=7, sticky=(W))
    yearsLabel.grid(row=1, column=8, sticky=(W))
    setTimeButton.grid(row=1, column=9, columnspan=2)
    timeCurrentlySetLabel.grid(row=1, column=11)

    maxScoreLabel.grid(row=2, column=0)
    maxScoreEntryField.grid(row=2, column=1, columnspan=8, sticky=(W))
    setMaxScoreButton.grid(row=2, column=9)
    setMaxScoreUnlimitedButton.grid(row=2, column=10)
    maxScoreCurrentlySetLabel.grid(row=2, column=11)

    gildedSkipLabel.grid(row=3, column=0)
    gildedSkipCheckButton.grid(row=3, column=1)

    Separator(redditFrame, orient=HORIZONTAL).grid(
        row=4, columnspan=13, sticky=(E, W), pady=5)

    deletionSectionLabel.grid(row=5, columnspan=11, sticky=(N, S), pady=5)

    deleteCommentsButton.grid(row=6, column=0, sticky=(W))
    deleteSubmissionsButton.grid(row=6, column=0, sticky=(E))
    testRunCheckButton.grid(row=6, column=1, columnspan=11)

    deletionProgressLabel.grid(row=7, column=0)
    deletionProgressBar.grid(row=8, column=0, sticky=(W))
    numDeletedItemsLabel.grid(row=8, column=0, sticky=(E))

    Separator(redditFrame, orient=HORIZONTAL).grid(
        row=9, columnspan=13, sticky=(E, W), pady=5)

    schedulerSectionLabel.grid(row=10, columnspan=11, sticky=(N, S), pady=5)

    schedulerRedditCheckButton.grid(row=11, column=0)
    hoursSelectionDropDown.grid(row=11, column=1)


# Builds tab that handles twitter config and actions
def buildTwitterTab(twitterFrame):
    twitterFrame.grid()

    # Configuration section title
    configurationLabel = Label(twitterFrame, text='Configuration')
    configurationLabel.config(font=('arial', 25))

    # Configuration to set total time of items to save
    currentTimeToSave = StringVar()
    currentTimeToSave.set('Currently set to save: [nothing]')
    timeKeepLabel = Label(
        twitterFrame, text='Keep items younger than: ')

    hoursDropDown = Combobox(twitterFrame, width=2)
    hoursDropDown['values'] = buildNumberList(24)
    hoursDropDown['state'] = 'readonly'
    hoursDropDown.current(0)

    daysDropDown = Combobox(twitterFrame, width=2)
    daysDropDown['values'] = buildNumberList(7)
    daysDropDown['state'] = 'readonly'
    daysDropDown.current(0)

    weeksDropDown = Combobox(twitterFrame, width=2)
    weeksDropDown['values'] = buildNumberList(52)
    weeksDropDown['state'] = 'readonly'
    weeksDropDown.current(0)

    yearsDropDown = Combobox(twitterFrame, width=2)
    yearsDropDown['values'] = buildNumberList(15)
    yearsDropDown['state'] = 'readonly'
    yearsDropDown.current(0)

    hoursLabel = Label(twitterFrame, text='hours')
    daysLabel = Label(twitterFrame, text='days')
    weeksLabel = Label(twitterFrame, text='weeks')
    yearsLabel = Label(twitterFrame, text='years')

    timeCurrentlySetLabel = Label(
        twitterFrame, textvariable=currentTimeToSave)
    setTimeButton = Button(
        twitterFrame,
        text='Set Total Time To Keep',
        command=lambda: setTwitterTimeToSave(
            hoursDropDown.get(), daysDropDown.get(),
            weeksDropDown.get(), yearsDropDown.get(), currentTimeToSave)
    )

    # Configuration to set saving items with a certain amount of favorites
    currentMaxFavorites = StringVar()
    currentMaxFavorites.set('Currently set to: 0 Favorites')
    maxFavoritesLabel = Label(
        twitterFrame, text='Delete tweets that have fewer favorites than:')
    maxFavoritesEntryField = Entry(twitterFrame, width=5)
    maxFavoritesCurrentlySetLabel = Label(
        twitterFrame, textvariable=currentMaxFavorites)
    setMaxFavoritesButton = Button(
        twitterFrame,
        text='Set Max Favorites',
        command=lambda: setTwitterMaxFavorites(
            maxFavoritesEntryField.get(), currentMaxFavorites)
    )
    setMaxFavoritesUnlimitedButton = Button(
        twitterFrame,
        text='Set Unlimited',
        command=lambda: setTwitterMaxFavorites('Unlimited', currentMaxFavorites)
    )

    # Configuration to set saving items with a certain amount of retweets
    currentMaxRetweets = StringVar()
    currentMaxRetweets.set('Currently set to: 0 Retweets')
    maxRetweetsLabel = Label(
        twitterFrame, text='Delete tweets that have fewer retweets than: ')
    maxRetweetsEntryField = Entry(twitterFrame, width=5)
    maxRetweetsCurrentlySetLabel = Label(
        twitterFrame, textvariable=currentMaxRetweets)
    setMaxRetweetsButton = Button(
        twitterFrame,
        text='Set Max Retweets',
        command=lambda: setTwitterMaxRetweets(
            maxRetweetsEntryField.get(), currentMaxRetweets)
    )
    setMaxRetweetsUnlimitedButton = Button(
        twitterFrame,
        text='Set Unlimited',
        command=lambda: setTwitterMaxRetweets(
            'Unlimited', currentMaxRetweets)
    )

    # Allows the user to delete tweets or remove favorites
    deletionSectionLabel = Label(twitterFrame, text='Deletion')
    deletionSectionLabel.config(font=('arial', 25))

    currentlyDeletingText = StringVar()
    currentlyDeletingText.set('')
    deletionProgressLabel = Label(
        twitterFrame, textvariable=currentlyDeletingText)

    deletionProgressBar = Progressbar(
        twitterFrame, orient='horizontal', length=100, mode='determinate')

    numDeletedItemsText = StringVar()
    numDeletedItemsText.set('')
    numDeletedItemsLabel = Label(twitterFrame, textvariable=numDeletedItemsText)

    deleteCommentsButton = Button(
        twitterFrame,
        text='Delete tweets',
        command=lambda: deleteTwitterTweets(
            root, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    deleteSubmissionsButton = Button(
        twitterFrame,
        text='Remove Favorites',
        command=lambda: deleteTwitterFavorites(
            root, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    testRunBool = IntVar()
    testRunBool.set(1)
    testRunText = 'TestRun - Checking this will show you what would be deleted, without actually deleting anything'
    testRunCheckButton = Checkbutton(
        twitterFrame, text=testRunText, variable=testRunBool, command=lambda: setTwitterTestRun(testRunBool))

    # Allows the user to schedule runs
    schedulerSectionLabel = Label(twitterFrame, text='Scheduler')
    schedulerSectionLabel.config(font=('arial', 25))

    schedulerTwitterBool = IntVar()
    schedulerTwitterText = 'Select to delete twitter comments + submissions daily at'

    hoursSelectionDropDown = Combobox(twitterFrame, width=2)
    hoursSelectionDropDown['values'] = buildNumberList(24)
    hoursSelectionDropDown['state'] = 'readonly'
    hoursSelectionDropDown.current(0)

    schedulerTwitterCheckButton = Checkbutton(twitterFrame, text=schedulerTwitterText, variable=schedulerTwitterBool, command=lambda: setTwitterScheduler(
        root, schedulerTwitterBool, int(hoursSelectionDropDown.get()), StringVar(), Progressbar()))

    # Actually build the twitter tab
    configurationLabel.grid(row=0, columnspan=11, sticky=(N, S), pady=5)
    timeKeepLabel.grid(row=1, column=0)
    hoursDropDown.grid(row=1, column=1, sticky=(W))
    hoursLabel.grid(row=1, column=2, sticky=(W))
    daysDropDown.grid(row=1, column=3, sticky=(W))
    daysLabel.grid(row=1, column=4, sticky=(W))
    weeksDropDown.grid(row=1, column=5, sticky=(W))
    weeksLabel.grid(row=1, column=6, sticky=(W))
    yearsDropDown.grid(row=1, column=7, sticky=(W))
    yearsLabel.grid(row=1, column=8, sticky=(W))
    setTimeButton.grid(row=1, column=9, columnspan=2)
    timeCurrentlySetLabel.grid(row=1, column=11)

    maxFavoritesLabel.grid(row=2, column=0)
    maxFavoritesEntryField.grid(row=2, column=1, columnspan=8, sticky=(W))
    setMaxFavoritesButton.grid(row=2, column=9)
    setMaxFavoritesUnlimitedButton.grid(row=2, column=10)
    maxFavoritesCurrentlySetLabel.grid(row=2, column=11)

    maxRetweetsLabel.grid(row=3, column=0)
    maxRetweetsEntryField.grid(row=3, column=1, columnspan=8, sticky=(W))
    setMaxRetweetsButton.grid(row=3, column=9)
    setMaxRetweetsUnlimitedButton.grid(row=3, column=10)
    maxRetweetsCurrentlySetLabel.grid(row=3, column=11)

    Separator(twitterFrame, orient=HORIZONTAL).grid(
        row=4, columnspan=13, sticky=(E, W), pady=5)

    deletionSectionLabel.grid(row=5, columnspan=11, sticky=(N, S), pady=5)

    deleteCommentsButton.grid(row=6, column=0, sticky=(W))
    deleteSubmissionsButton.grid(row=6, column=0, sticky=(E))
    testRunCheckButton.grid(row=6, column=1, columnspan=11)

    deletionProgressLabel.grid(row=7, column=0)
    deletionProgressBar.grid(row=8, column=0, sticky=(W))
    numDeletedItemsLabel.grid(row=8, column=0, sticky=(E))

    Separator(twitterFrame, orient=HORIZONTAL).grid(
        row=9, columnspan=13, sticky=(E, W), pady=5)

    schedulerSectionLabel.grid(
            row=10, columnspan=11, sticky=(N, S), pady=5)

    schedulerTwitterCheckButton.grid(row=11, column=0)
    hoursSelectionDropDown.grid(row=11, column=1)


# Builds and runs the tkinter UI
def createUI():
    Tk.report_callback_exception = callbackError

    root.title('Social Amnesia')

    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.createcommand('tk::mac::ReopenApplication', root.deiconify)

    tabs = Notebook(root)

    loginFrame = Frame(tabs)
    buildLoginTab(loginFrame)
    tabs.add(loginFrame, text='Login To Accounts')

    redditFrame = Frame(tabs)
    buildRedditTab(redditFrame)
    tabs.add(redditFrame, text='reddit')

    twitterFrame = Frame(tabs)
    buildTwitterTab(twitterFrame)
    tabs.add(twitterFrame, text='twitter')

    tabs.pack(expand=1, fill="both")

    root.mainloop()


def main():
    createUI()


if __name__ == '__main__':
    main()
