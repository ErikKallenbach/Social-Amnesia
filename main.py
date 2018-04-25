# standard python imports
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

#local files
from reddit import setRedditLogin, setTimeToSave, setMaxScore, deleteItems

# define tkinter UI
root = Tk()

# If the user needs to be informed of an error, this will let tkinter take
#   care of that
def callbackError(self, *args):
    # reddit error, happens if you try to run `reddit.user.me()` 
    #   and login fails
    if(str(args[1]) == 'received 401 HTTP response'):
        messagebox.showerror('ERROR', 'Failed to login to reddit!')


def buildNumberList(max):
    numList = []
    for i in range(0, max):
        numList.append(str(i))
    return numList


# Builds the tab that lets the user log into their social media accounts
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
        command=lambda: setRedditLogin(redditUsernameEntry.get(), 
                                       redditPasswordEntry.get(),
                                       redditClientIDEntry.get(), 
                                       redditClientSecretEntry.get(),
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


# Builds the tab that will handle reddit configuration and actions
def buildRedditTab(redditFrame):
    redditFrame.grid()

    # Configuration to set total time of items to save
    currentTimeToSave = StringVar()
    currentTimeToSave.set('Currently set to save [nothing]')
    timeKeepLabel = Label(
        redditFrame, text='Keep comments/submissions younger than: ')

    hoursDropDown = Combobox(redditFrame, width=2)
    hoursDropDown['values'] = buildNumberList(24)
    hoursDropDown.current(0)

    daysDropDown = Combobox(redditFrame, width=2)
    daysDropDown['values'] = buildNumberList(7)
    daysDropDown.current(0)

    weeksDropDown = Combobox(redditFrame, width=2)
    weeksDropDown['values'] = buildNumberList(52)
    weeksDropDown.current(0)

    yearsDropDown = Combobox(redditFrame, width=2)
    yearsDropDown['values'] = buildNumberList(15)
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
        command=lambda: setTimeToSave(
            hoursDropDown.get(), daysDropDown.get(), 
            weeksDropDown.get(), yearsDropDown.get(), currentTimeToSave)
    )

    # Configuration to set saving items with a certain amount of upvotes
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

    # Allows the user to actually delete comments or submissions
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
        command=lambda: deleteItems(True, currentlyDeletingText, deletionProgressBar, numDeletedItemsText, root)
    )

    deleteSubmissionsButton = Button(
        redditFrame,
        text='Delete submissions',
        command=lambda: deleteItems(False, currentlyDeletingText, deletionProgressBar, numDeletedItemsText, root)
    )

    timeKeepLabel.grid(row=0, column=0)
    hoursDropDown.grid(row=0, column=1)
    hoursLabel.grid(row=0, column=2)
    daysDropDown.grid(row=0, column=3)
    daysLabel.grid(row=0, column=4)
    weeksDropDown.grid(row=0, column=5)
    weeksLabel.grid(row=0, column=6)
    yearsDropDown.grid(row=0, column=7)
    yearsLabel.grid(row=0, column=8)
    setTimeButton.grid(row=0, column=9)
    timeCurrentlySetLabel.grid(row=0, column=10)
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
