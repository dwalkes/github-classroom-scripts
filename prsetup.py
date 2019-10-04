#!/usr/bin/python3
import subprocess
import webbrowser
import traceback
import argparse
import sys
import csv
import configparser
assign = configparser.ConfigParser()

ASSIGNCONFIG_FILE='scripts_config/assignconfig.txt'
CLASSROSTER_FILE='scripts_config/classroom_roster.csv'
import os
exists = os.path.isfile(ASSIGNCONFIG_FILE)
if exists:
    assign.read(ASSIGNCONFIG_FILE)
else:
    print("Missing assignment configuration at " + ASSIGNCONFIG_FILE )
    print("Please add this file with details about your GitHub Classroom Setup.")
    print("See assignconfig_example.txt for an example.")
    exit(1)

error_students={}

assign_name_git_url_prefix="git@github.com:"+ assign['DEFAULT']['GITHUB_CLASSROOM'] + "/"

parser = argparse.ArgumentParser(
                    description="Setup pull requests for students using github classroom for assignment submission.\n"
                                "  By default with no arguments, just opens PR pages for each student submission.")
parser.add_argument('--dry_run',dest='dry_run', action='store_true',
                    help='Do a dry run only, printing the commands which would be executed')
parser.add_argument('--log_cmds',dest='log_cmds', action='store_true',  default=False, help='Log all commands as run')
parser.add_argument('--delete_local',dest='delete_local', action='store_true', default=False,
                        help='Delete local repositories if they exist (to resync with master on remotes)')
parser.add_argument('--create_local',dest='create_local', action='store_true', default=False,
                        help='Create local repositories based on student submissions if they do not already exist')
parser.add_argument('--push_remote',dest='push_remote', action='store_true', default=False,
                        help='Push updated local repositories to remote submission repositories (for PR creation)')
parser.add_argument('--no_open_pr_page',dest='open_pr_page', action='store_false', default=True,
                        help='Skip opening pull request webpages for each student')
parser.add_argument('--force_push',dest='force_push', action='store_true', default=False,
                        help='force push to remote repository, to unconditionally update content there')
parser.add_argument('--first_student',dest='first_student', action='store_true', default=False,
                        help='Stop after the first student')
parser.add_argument('--one_student',help='Use a single github student ID for update')



args = parser.parse_args()

def read_roster_students(csv_file):
    '''
    Read a CSV file with github_username column defined in the header (matching GitHub Classroom export format) and
    return the corresponding list of students
    :param csv_file: file exported from Github classrom, opened with read permissions, containing a column
    "github_username"
    :return: an array of students from the github_username column.
    '''
    csv_reader=csv.DictReader(csv_file)
    students=[]
    for row in csv_reader:
        students.append(row["github_username"])
    return students

def get_roster_students():
    students=None
    try:
        with open(CLASSROSTER_FILE, mode='r') as csv_file:
            students=read_roster_students(csv_file)
    except FileNotFoundError:
        print("Could not find classroom roster at " + CLASSROSTER_FILE)
        print("Please run the script from a directory which contains this scripts_config folder and csv file."
              "See README for details")
        exit(1)
    return students

def cmd(cmdargs):
    ret="bogus return" # just to prevent errors in dry run cases
    if args.dry_run or args.log_cmds:
        print(*cmdargs)
        sys.stdout.flush()
    if not args.dry_run:
        ret=str(subprocess.check_output(cmdargs))
    return ret

def create_remote_if_not_existing(name,remote_url):
    remotes=cmd(["git","remote"])
    if remotes.find(name) == -1:
        cmd(["git","remote","add",name,remote_url])

def checkout_and_track_or_update(remote,local_branch,remote_branch):
    branches=cmd(["git", "branch"])
    cmd(["git", "fetch", remote])
    if branches.find(local_branch) != 0:
        cmd(["git", "fetch", "--recurse-submodules=no", remote, remote_branch+":"+local_branch])

def delete_local_if_exists(local_branch):
    branches=cmd(["git", "branch"])
    if branches.find(local_branch):
        cmd(["git", "branch", '-D', local_branch])

def remote_branch_exists(remote,remote_branchname):
    exists=False
    remote_branches=cmd(["git", "branch", "-r"])
    if remote_branches.find(remote+"/"+remote_branchname) == 0 :
        exists=True
    return exists

def push_local_branch_to_remote_check_if_exists(remote,local_and_remote_branchname):
    exists=remote_branch_exists(remote,local_and_remote_branchname)
    if args.force_push:
        cmd(["git", "push", "-f", remote, local_and_remote_branchname])
    else:
        cmd(["git", "push", remote, local_and_remote_branchname])
    return exists


def open_browser_at_url(url):
    if not args.dry_run:
        webbrowser.open(url)

if args.dry_run:
    print("Doing a dry run, not actually setting up any remotes or repos")

students = get_roster_students()

if len(students) == 0:
    print("No students defined, check the format of " + CLASSROSTER_FILE )
    exit(1)

if args.first_student:
    print("Truncating the list to only use the first student")
    del students[1:]

if args.one_student:
    print("Updating only student " + args.one_student)
    students = [ args.one_student ]

for student in students:
    try:
        if assign.getboolean('DEFAULT','STARTS_WITH_PREV_ASSIGN'):
            assign_prev_remote = student + "_assignment" + str(assign["DEFAULT"]["NUMBER_PREV"]) + "_remote"
            assign_prev_branch = student + "_assignment" + str(assign["DEFAULT"]["NUMBER_PREV"]) + "_submission"
            assign_base_repo_full = assign_name_git_url_prefix+assign["DEFAULT"]["NAME_PREV"]+"-"+student+".git"
            assign_prev_remote_branch_local_name = assign_prev_branch
        else:
            assign_prev_remote = assign["DEFAULT"]["BASE_REPO"]
            assign_prev_branch = assign["DEFAULT"]["BASE_REPO_BRANCH"]
            assign_base_repo_full = assign_name_git_url_prefix+assign["DEFAULT"]["BASE_REPO"] +".git"
            assign_prev_remote_branch_local_name = "assignment" + str(assign["DEFAULT"]["NUMBER_PREV"]) + "_base"

        assign_current_remote = student + "_assignment" + str(assign["DEFAULT"]["NUMBER_CURRENT"]) + "_remote"
        assign_current_branch = student + "_assignment" + str(assign["DEFAULT"]["NUMBER_CURRENT"]) + "_submission"
        if args.delete_local:
            delete_local_if_exists(assign_current_branch)
        if args.create_local:
            create_remote_if_not_existing(assign_prev_remote,
                                          assign_base_repo_full)
            create_remote_if_not_existing(assign_current_remote,
                                          assign_name_git_url_prefix + assign["DEFAULT"]["NAME_CURRENT"]
                                                + "-" + student + ".git")
            cmd(["git","fetch","--recurse-submodules=no",assign_prev_remote])
            cmd(["git","fetch","--recurse-submodules=no",assign_current_remote])
            if not remote_branch_exists(assign_prev_remote,assign_prev_branch):
                # This supports starting midway through the semester when a previous assignment in the series hasn't used the submission script
                assign_prev_branch="master"
            checkout_and_track_or_update(assign_prev_remote,assign_prev_remote_branch_local_name,assign_prev_branch)
            checkout_and_track_or_update(assign_current_remote,assign_current_branch,"master")
        if args.push_remote:
            push_local_branch_to_remote_check_if_exists(assign_current_remote,assign_prev_remote_branch_local_name)
            push_local_branch_to_remote_check_if_exists(assign_current_remote,assign_current_branch)
        if args.open_pr_page:
            open_browser_at_url("https://github.com/" + assign['DEFAULT']['GITHUB_CLASSROOM'] +"/" +
                                assign['DEFAULT']['NAME_CURRENT'] + "-" +
                                student + "/compare/"+assign_prev_remote_branch_local_name+"..."+assign_current_branch+"?expand=1")
    except Exception as err:
        print("Could not complete assignment PR setup for student {}".format(student))
        error_students[student]=str(err)+traceback.format_exc()

if len(error_students.keys()) != 0:
    print("The following {} students had errors attempting to create pull requests:".format(len(error_students.keys())))
    for student in error_students.keys():
        print("Student {}: error {}".format(student,error_students[student]))
else:
    print("All student actions complete with success!")



