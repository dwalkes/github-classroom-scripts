#!/usr/bin/python3
import subprocess
import webbrowser
import traceback
import argparse
import sys
import csv
import configparser
import pathlib
import shutil
import tempfile

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
                    description="Push a repository from github to gitlab")
parser.add_argument('--dry_run',dest='dry_run', action='store_true',
                    help='Do a dry run only, printing the commands which would be executed')
parser.add_argument('--log_cmds',dest='log_cmds', action='store_true',  default=False, help='Log all commands as run')
parser.add_argument('--first_student',dest='first_student', action='store_true', default=False,
                        help='Stop after the first student')
parser.add_argument('--one_student',help='Use a single github student ID for update')
parser.add_argument('--assignment_name',help='The assignment name to use for the assignment (from github classroom)')


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
        ret=subprocess.check_output(cmdargs).decode('utf-8')
    return ret

def open_browser_at_url(url):
    if not args.dry_run:
        webbrowser.open(url)

if args.dry_run:
    print("Doing a dry run, not actually setting up any remotes or repos")

students = get_roster_students()

if len(students) == 0:
    print("No students defined, check the format of " + CLASSROSTER_FILE )
    exit(1)

if args.one_student:
    print("Updating only student " + args.one_student)
    students = [ args.one_student ]

if args.assignment_name is None:
    print("Please specfiy assignment name from github classroom")
    exit(1)


workdir = os.getcwd()
for student in students:
    tmpdir=tempfile.mkdtemp()
    os.chdir(tmpdir)
    reponame=args.assignment_name+"-"+student
    assign_submission_repo_full = assign_name_git_url_prefix+reponame+".git"
    assign_push_repo_full = assign["DEFAULT"]["PUSH_REPO"]+"/" + reponame+".git"
    try:
        cmd(["git","clone",assign_submission_repo_full])
        os.chdir(reponame)
        cmd(["git","push","--set-upstream",assign_push_repo_full,"master"])
        shutil.rmtree(tmpdir)
        open_browser_at_url(assign['DEFAULT']['OPEN_URL'] +"/" + reponame)

    except Exception as err:
        print("Could not complete assignment PR setup for student {}".format(student))
        error_students[student]=str(err)+traceback.format_exc()

os.chdir(workdir)
if len(error_students.keys()) != 0:
    print("The following {} students had errors attempting to create pull requests:".format(len(error_students.keys())))
    for student in error_students.keys():
        print("Student {}: error {}".format(student,error_students[student]))
else:
    print("All student actions complete with success!")
