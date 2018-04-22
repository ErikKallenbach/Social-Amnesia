import praw
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import arrow
from time import sleep

# auto import and set a login for development purposes
from secrets import REDDIT_USERNAME, REDDIT_PASSWORD, CLIENT_ID, CLIENT_SECRET 

USER_AGENT = 'Social Scrubber: v0.0.1 (by /u/JavaOffScript)'

# define tkinter UI
root = Tk()

# lets have a python dictionary that will hold redditState stuff, that will eventually be factored out to a different file
redditState = {}

# prints out the redditState to console
def printState():
    print(redditState)


def callbackError(self, *args):
    # reddit error, happens if you try to run `reddit.user.me()` and login fails
    if(str(args[1]) == 'received 401 HTTP response'):
        messagebox.showerror('ERROR', 'Failed to login to reddit!')


# logs into reddit using PRAW
def setRedditLogin(username, password, clientID, clientSecret, loginConfirmText):
    # ============= REAL =================
    # reddit = praw.Reddit(
    #     client_id=clientID,
    #     client_secret=clientSecret,
    #     user_agent=USER_AGENT,
    #     username=username,
    #     password=password
    # )
    # ============= REAL =================

    # ================= FOR TESTING ===================
    username = REDDIT_USERNAME
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )
    #================= FOR TESTING ===================

    # confirm successful login
    if (reddit.user.me() == username):
        loginConfirmText.set(f'Logged in as {username}')

        redditState['user'] = reddit.redditor(username)
        redditState['recentlyPostedCutoff'] = arrow.now().replace(hours=0)
        redditState['maxScore'] = 0


# Sets the hours of comments or submissions to save, stores it in redditState
#  and updates the UI to show what its currently set to.
# hoursToSave: the input received from the UI
# currentHoursToSave: what is stored for the user in the UI
def setHoursToSave(hoursToSave, currentHoursToSave):
    if (hoursToSave == ''):
        hoursToSave = 0
    else:
        hoursToSave = int(hoursToSave)

    redditState['recentlyPostedCutoff'] = arrow.now().replace(
        hours=-hoursToSave)
    currentHoursToSave.set(f'Currently set to: {str(hoursToSave)} hours')


# Sets the maximum score level, any posts above this store will be skipped over
#  updates the UI to show what its currently set to.
# maxScore: the input received from the UI
# currentMaxScore: what is stored for the user in the UI
def setMaxScore(maxScore, currentMaxScore):
    if (maxScore == ''):
        maxScore = 0
    elif (maxScore == 'Unlimited'):
        redditState['maxScore'] = 9999999999
    else:
        maxScore = int(maxScore)
        redditState['maxScore'] = maxScore

    currentMaxScore.set(f'Currently set to: {str(maxScore)} upvotes')


def deleteItems(commentBool, currentlyDeletingText, deletionProgressBar, numDeletedItemsText):
    if commentBool:
        totalItems = sum(
            1 for item in redditState['user'].comments.new(limit=None))
        itemArray = redditState['user'].comments.new(limit=None)
    else:
        totalItems = sum(
            1 for item in redditState['user'].submissions.new(limit=None))
        itemArray = redditState['user'].submissions.new(limit=None)

    numDeletedItemsText.set(f'0/{str(totalItems)} items processed so far')

    count = 1
    for item in itemArray:
        if commentBool:
            itemString = 'Comment'
            itemSnippet = item.body[0:100]
        else:
            itemString = 'Submission'
            itemSnippet = item.title[0:100]

        timeCreated = arrow.get(item.created_utc)

        if (timeCreated > redditState['recentlyPostedCutoff']):
            # print(f'{itemString} `{itemSnippet}` is more recent than cutoff. skipping')
            currentlyDeletingText.set(f'{itemString} `{itemSnippet}` more recent than cutoff, skipping.')
        elif (item.score > redditState['maxScore']):
            # print(f'{itemString} `{itemSnippet}` is higher than max score, skipping.')
            currentlyDeletingText.set(f'{itemString} `{itemSnippet}` is higher than max score, skipping.')
        else:
            # comment back in once things get real
            # item.delete()
            # print(f'{itemString} `{itemSnippet}` deleted.`')
            # print(f'TESTING: We would delete {itemString} `{itemSnippet}`')
            currentlyDeletingText.set(f'TESTING: We would delete {itemString} `{itemSnippet}`')

        # print(round((count / totalItems) * 100))
        numDeletedItemsText.set(f'{str(count)}/{str(totalItems)} items processed.')
        deletionProgressBar['value'] = round(
            (count / totalItems) * 100, 1)
        root.update()
        count += 1
        sleep(1)


def buildLoginTab(loginFrame):
    loginFrame.grid()

    redditLabel = Label(loginFrame, text='reddit')

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
        command=lambda: setRedditLogin(redditUsernameEntry.get(), redditPasswordEntry.get(),
                                       redditClientIDEntry.get(), redditClientSecretEntry.get(),
                                       redditLoginConfirmText)
    )

    redditLabel.grid(row=0, column=0)
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


# creates the tab that will have reddit configuration
def buildRedditTab(redditFrame):
    redditFrame.grid()

    currentHoursToSave = StringVar()
    currentHoursToSave.set('Currently set to: 0 hours')
    hoursTextLabel = Label(
        redditFrame, text='Hours of comments/submissions to keep:')
    hoursEntryField = Entry(redditFrame)
    hoursCurrentlySetLabel = Label(
        redditFrame, textvariable=currentHoursToSave)
    setHoursButton = Button(
        redditFrame,
        text='Set Hours To Keep',
        command=lambda: setHoursToSave(
            hoursEntryField.get(), currentHoursToSave)
    )

    currentMaxScore = StringVar()
    currentMaxScore.set('Currently set to: 0 upvotes')
    maxScoreLabel = Label(
        redditFrame, text='Delete comments/submissions less than score:')
    maxScoreEntryField = Entry(redditFrame)
    maxScoreCurrentlySetLabel = Label(
        redditFrame, textvariable=currentMaxScore)
    setMaxScoreButton = Button(
        redditFrame,
        text='Set Max Score',
        command=lambda: setMaxScore(maxScoreEntryField.get(), currentMaxScore)
    )
    setMaxScoreUnlimitedButton = Button(
        redditFrame,
        text='Set Unlimited',
        command=lambda: setMaxScore('Unlimited', currentMaxScore)
    )

    currentlyDeletingText = StringVar()
    currentlyDeletingText.set('')
    deletionProgressLabel = Label(redditFrame, textvariable=currentlyDeletingText)

    deletionProgressBar = Progressbar(
        redditFrame, orient='horizontal', length=100, mode='determinate')

    numDeletedItemsText = StringVar()
    numDeletedItemsText.set('')
    numDeletedItemsLabel = Label(redditFrame, textvariable=numDeletedItemsText)

    deleteCommentsButton = Button(
        redditFrame,
        text='Delete comments',
        command=lambda: deleteItems(True, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    deleteSubmissionsButton = Button(
        redditFrame,
        text='Delete submissions',
        command=lambda: deleteItems(False, currentlyDeletingText, deletionProgressBar, numDeletedItemsText)
    )

    # showStateButton = Button(
    #     redditFrame,
    #     text='*TEST* Show Options *TEST*',
    #     command=printState
    # )

    hoursTextLabel.grid(row=0, column=0)
    hoursEntryField.grid(row=0, column=1)
    setHoursButton.grid(row=0, column=2)
    hoursCurrentlySetLabel.grid(row=0, column=3)
    maxScoreLabel.grid(row=1, column=0)
    maxScoreEntryField.grid(row=1, column=1)
    setMaxScoreButton.grid(row=1, column=2)
    setMaxScoreUnlimitedButton.grid(row=1, column=3)
    maxScoreCurrentlySetLabel.grid(row=1, column=4)
    deleteCommentsButton.grid(row=2, column=0)
    deleteSubmissionsButton.grid(row=2, column=1)
    deletionProgressLabel.grid(row=3, column=0)
    deletionProgressBar.grid(row=3, column=1)
    numDeletedItemsLabel.grid(row=3, column=2)



# Builds and runs the tkinter UI
def createUI():
    Tk.report_callback_exception = callbackError

    # root = Tk()
    root.title('Social Scrubber')

    tabs = Notebook(root)

    loginFrame = Frame(tabs)
    buildLoginTab(loginFrame)
    tabs.add(loginFrame, text='Login To Accounts')

    redditFrame = Frame(tabs)
    buildRedditTab(redditFrame)
    tabs.add(redditFrame, text='reddit')

    tabs.pack(expand=1, fill="both")

    root.mainloop()


def main():
    createUI()


if __name__ == '__main__':
    main()
