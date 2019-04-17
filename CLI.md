IMPORTANT TERMINAL CODE:

$ cd (name of directory)
 - for changing directories
ex: navigate to DESKTOP folder

> $ cd DESKTOP

ex: navigate up one folder

> $ cd ..

ex: for listing content in directory

> $ ls

ex: print working directory - information on current location

> $ pwd


## GIT COMMANDS!

ex: clone repo to local machine

$ git clone (link to repo)

ex: show commit history

$ git log

### STEP 0 - get the changes others have made

$ git pull


### STEP 1 - stage files to commit

ex: indicate which files to mark in the checkpoint 

$ git add (name of file)

$ git add . (saves all things down from current directory)


ex: shows files that have changed

$ git status 

# when you do git status to see local changes
red files haven't ben staged - not added to commit checkpoint
green files have been changed

### STEP 2 - create the checkpoint with annotation

$ git commit -m "name of commit" - this is like the non-gui version of the GitHub commit line

### STEP 3 - send checkpoint to master repo on GitHub

$ git push - send checkpoint to master repo (i.e. commit from step 2)

