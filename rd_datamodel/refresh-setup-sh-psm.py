#'////////////////////////////////////////////////////////////////////////////
#' FILE: refresh-setup-sh.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-07
#' MODIFIED: 2022-02-07
#' PURPOSE: Refresh setup.py script
#' STATUS: stable
#' PACKAGES: os, re
#' COMMENTS: run `yarn m:update-setup 
#'////////////////////////////////////////////////////////////////////////////

from os import listdir
import re

dir = 'dist'
dir_lu = 'lookups'
file = 'setup_psm.sh'
files = listdir(dir_lu)
filepath = f'{file}'

start = '# <!--- start: listEmxFiles --->\n'
end = '# <!--- end: listEmxFiles --->\n'

files = [
    f'mcmd import -p {dir_lu}/{f}\n' for f in files
    if re.search(r'(psm_lookups_[_a-zA-Z]{1,}.csv)', f)
]

setupFiles = ['mcmd import -p dist/PerSAIDs.xlsx\n'] + files


with open(filepath, 'r') as stream:
    contents = stream.readlines()
    
newContents = contents[:contents.index(start) + 1] + setupFiles + contents[contents.index(end):]

with open(filepath, 'w') as stream:
    stream.writelines(newContents)

