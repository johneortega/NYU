#!/bin/bash

# first argument is directory
if [ $# -ne 2 ]; then
    # TODO: print usage
    echo "arg1 is homework dir and arg2 is destination dir"
    exit 1
fi

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
the_find=$(find ${1} -iname "*.xml")
the_new_dir=${2}
for file in $the_find
do
    file_name_split=$(echo ${file} | grep -o 'submission_[0-9].*/' | tr -d /)
    echo "cp ${file} ${the_new_dir}/${file_name_split}.xml"
    cp ${file} ${the_new_dir}/${file_name_split}.xml
done 
IFS=$SAVEIF
