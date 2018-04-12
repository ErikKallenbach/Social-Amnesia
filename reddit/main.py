import praw
from tkinter import *
from tkinter import ttk
import arrow

from secrets import CLIENT_ID, CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD

USER_AGENT = 'Social Scrubber: v0.0.1 (by /u/JavaOffScript)'

# hardcoded for now, this will eventually be set by user, somehow
reddit = praw.Reddit(
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  user_agent=USER_AGENT,
  username=REDDIT_USERNAME,
  password=REDDIT_PASSWORD
)

#lets have a python dictionary that will hold state stuff, that will eventually be factored out to a different file
state = {}

def setInitState():
  state['user'] = reddit.redditor(REDDIT_USERNAME)
  state['recentlyPostedCutoff'] = arrow.now().replace(hours=0)
  state['maxScore'] = 0


# prints out the state to console
def printState():
  print(state)


# Sets the hours of comments or submissions to save, stores it in state
#  and updates the UI to show what its currently set to.
# hoursToSave: the input recieved from the UI
# currentHoursToSave: what is stored for the user in the UI
def setHoursToSave(hoursToSave, currentHoursToSave):
  if (hoursToSave == ''):
    hoursToSave = 0
  else:
    hoursToSave = int(hoursToSave)

  state['recentlyPostedCutoff'] = arrow.now().replace(hours=-hoursToSave)
  currentHoursToSave.set(f'Currently set to: {str(hoursToSave)} hours')


# Sets the maximum score level, any posts above this store will be skipped over
#  updates the UI to show what its currently set to.
# maxScore: the input recieved from the UI
# currentMaxScore: what is stored for the user in the UI
def setMaxScore(maxScore, currentMaxScore):
  if (maxScore == ''):
    maxScore = 0
  elif (maxScore == 'Unlimited'):
    state['maxScore'] = 9999999999
  else:
    maxScore = int(maxScore)
    state['maxScore'] = maxScore
  
  
  currentMaxScore.set(f'Currently set to: {str(maxScore)} upvotes')


# checks items against possibly whitelisted conditions defined in state, and either skips or deletes
def checkWhiteList(item, commentBool):
  if commentBool: 
    itemString = 'Comment' 
    itemSnippet = item.body[0:100]
  else: 
    itemString = 'Submission'
    itemSnippet = item.title[0:100]

  timeCreated = arrow.get(item.created_utc)

  if (timeCreated > state['recentlyPostedCutoff']):
    print(f'{itemString} `{itemSnippet}` is more recent than cutoff. skipping')
  elif (item.score > state['maxScore']):
    print (f'{itemString} `{itemSnippet}` is higher than max score, skipping')
  else:
    # comment back in once things get real
    # item.delete()
    # print(f'{itemString} `{itemSnippet}` Deleted`')
    print (f'TESTING: We would delete {itemString} `{itemSnippet}`')


# Get and delete comments
def deleteComments():
  for comment in state['user'].comments.new(limit=None):
    checkWhiteList(comment, True)


# Get and delete submissions
def deleteSubmissions():
  for submission in state['user'].submissions.new(limit=None):
    checkWhiteList(submission, False)


def buildRedditTab(redditFrame):
  redditFrame.grid()

  currentHoursToSave = StringVar()
  currentHoursToSave.set('Currently set to: 0 hours')
  hoursTextLabel = Label(
      redditFrame, text='Hours of comments/submissions to keep:')
  hoursEntryField = Entry(redditFrame)
  hoursCurrentlySetLabel = Label(redditFrame, textvariable=currentHoursToSave)
  setHoursButton = Button(
      redditFrame,
      text='Set Hours To Keep',
      command=lambda: setHoursToSave(hoursEntryField.get(), currentHoursToSave)
  )

  currentMaxScore = StringVar()
  currentMaxScore.set('Currently set to: 0 upvotes')
  maxScoreLabel = Label(
      redditFrame, text='Delete comments/submissions less than score:')
  maxScoreEntryField = Entry(redditFrame)
  maxScoreCurrentlySetLabel = Label(redditFrame, textvariable=currentMaxScore)
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

  deleteCommentsButton = Button(
      redditFrame,
      text='Delete comments',
      command=deleteComments
  )

  deleteSubmissionsButton = Button(
      redditFrame,
      text='Delete submissions',
      command=deleteSubmissions
  )

  showStateButton = Button(
      redditFrame,
      text='Show Options',
      command=printState
  )

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
  showStateButton.grid(row=3)


# Builds and runs the tkinter UI
def createUI():
  root = Tk()
  root.title('Social Scrubber')

  tabs = ttk.Notebook(root)
  
  redditFrame = ttk.Frame(tabs)
  
  buildRedditTab(redditFrame)

  tabs.add(redditFrame, text='reddit')

  tabs.pack(expand=1, fill="both")

  root.mainloop()


def main():
  setInitState()
  createUI()


if __name__ == '__main__':
  main()
