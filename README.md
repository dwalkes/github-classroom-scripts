# Overview
This repository contains scripts which may be useful for courses which use
[GitHub Classroom](https://classroom.github.com) for assignment submission.
This is especially true for courses which use assignment series, where one assignment builds on the previous.
It was originally developed for use in University of Colorado course
[ECEN 5823](https://sites.google.com/colorado.edu/ecen5823/home).

# Using These Scripts
1. Add this repository as a git submodule on a parent repository used by instructors/student assistants for assignment grading.
  This would typically be a private repository which contains completed assignments for reference by instructors and
   teaching assistants.
2. Add a scripts_config/classroom_roster.csv file in the parent repository containing the list of students exported from
the Roster Mangement->Download section of your GitHub classroom, where the scripts_config folder is at the same directory as the github-classroom-scripts submodule folder.  You may need to prune this to remove teaching
assistants and yourself from the list, as well as any students who haven't actually submitted an assignment
(perhaps dropped the course).  Make sure you check this into a private repository to avoid sharing student information
publicly.
3. Setup your assignment and GithubClassroom using a scripts_config/assignconfig.txt file.  An example config file is
provided in the assignconfig_example.txt file.
4. Run ```pip3 install -r requirements.txt``` to install requirements in your python3 environment
5. Run the scripts from the base directory using ```./github-classroom-scripts/scriptname.py``` so the script will work
 on the parent repository and find the roster file and assignconfig.txt file, also so the git commands will work on the
 appropriate repository.

See sections below for individual script details.

## prsetup.py

This script works with an assignment series where assignments start with a base set of code and then build on each
other throughout the semester.  It sets up pull request in each student's repository which allow you to easily compare
the changes made between the previous/current assignments.  This pull request will not actually be merged, but will be
a place where instructors and student assistants can add code review comments which students can see and respond to.

The script creates:
* A remote named  *student*_assignment*number*_remote pointing to the student's submission repository.
* A local branch named *student*_assignment*number*_submission containing the content of the student's assignment
submission.
* Remote branches in the student's repository with the same branch names above, containing the current and previous
submission or, in the case that this is the first assignment, the difference between the current submission and the
assignment used as the base submission.

The script also opens a page which compares the current and previous submission branches. Clicking the "Create PR"
button on this page creates a pull request.

Start by editing the variables at the top of the script to point to your github classroom page and assignments.

Run the script with no arguments for usage instructions.
