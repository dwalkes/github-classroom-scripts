# Overview
This repository contains scripts which may be useful for courses which use
[GitHub Classroom](https://classroom.github.com) for assignment submission.
This is especially true for courses which use assignment series, where one assignment builds on the previous.
It was originally developed for use in University of Colorado course
[ECEN 5823](https://sites.google.com/colorado.edu/ecen5823/home).

# Running on Windows

Ensure you have [Python 3](https://www.python.org/downloads/windows/) installed and in your PATH or run with the full path to the python 3 interpreter.  Execute using
```
python ./github-classroom-scripts/pr-setup.py
```
or subtitute the python command with the path to your Python 3 interpreter.
If you need to support multiple python environments you may also consider [anaconda](https://virtualenv.pypa.io/en/latest/) or [virtualenv](https://virtualenv.pypa.io/en/latest/)


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
5. Run the scripts from the base directory using ```./github-classroom-scripts/scriptname.py``` or ```python ./github-classroom-scripts/scriptname.py``` where python refers to a python 3 interpreter in your PATH.  You need to run from the base directory containing your scripts_config folder and *not* this folder, so the script can find the roster file and assignconfig.txt file, also so the git commands will work on the appropriate repository.

See sections below for individual script details.



## SSH Agent
To avoid the need to re-enter credentials, use this script with an ssh agent and your authorized key
```
eval `ssh-agent`
ssh-add /path/to/key
```

## push-to-gitlab.py

This is a simple script that clones a repository from github classroom and pushes to gitlab, useful when you have
gitlab-ci automated test configuration setup in gitlab.  See assignconfig_example_push_to_gitlab.txt for a simplifiled
assignment config text file you can use to configure for this script.

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

Typically the first person on the team who runs this script would run:
```
./github-classroom-scripts/prsetup.py --create_local --push_remote
```
To both create local repositories to track student assignments as well as update remote branches on github.  This person would also use the opened PR pages to create pull requests.

The next people on the team would run
```
./github-classroom-scripts/prsetup.py --create_local
```
To create their local repositories, and the script would open browser pages to each pull request.

If you've already created the local repositories and remote repositories for a given assignment and just want to open pull request pages, run with no command arguments.

### Late submissions/resubmissions

If a student updates their repository after the deadline and requests an update for late submission credit, you can update their assignment using:
```
./github-classroom-scripts/prsetup.py --delete_local --create_local --push_remote --one_student <studentid>
```
### Overlays

Use the `--overlay_files` option along with the OVERLAY_FILES section of the configuration to overlay files from the working branch of
a private repo on top of the student submission in an overlay_<student_assignment_branch>.  The list of files specified in OVERLAY_FILES
will be added in a new commit on top of the student submission, allowing for additional content like test scripts to be included or to
ensure specific versions of repositories or submodules are used.

### Test Scripts

Use the `--test_script` option with relative path to an executable to kick off a tests on each student repository, 
recording the script execution success/failure status and writing output logs to the ~/test_script_results/ directory
based on assignment and student name.

This option is useful with the `--clone_dir` option which can be used to clone student repositories into individual directories.
This way, when failures occur during the test run, it's possible to go into the directory under `--clone_dir` corresponding to
the student's assignment and re-run any failing test scripts against the student's submission.  When `--clone_dir` is specified, the path to the individual student's cloned repository will be passed as the first argument to the `--test_script`.

### Push Alternates
Use the `--push_alternate` option to specify an alternate location to push with --set-upstream.  If specified, the assignment submission branch
(or assignment submission branch overlay, if `--overlay_files`) will be pushed to a new repo, possibly creating it.
This is useful with [gitlab push to create new project](https://docs.gitlab.com/ee/gitlab-basics/create-project.html#push-to-create-a-new-project) option,
in the case you use gitlab repositories for CI or testing.
