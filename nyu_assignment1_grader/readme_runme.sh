
### first you need to export the submissions in a submission.zip folder
### then, when you unzip them you will see a directory similar to below
### assignment_2932132_export
### you should make sure that you have created the directory 'student_files'
### by running the command below, the submission files will be copied there
### the original directory without any data should look simimlar to this
### answers.xml          grader_xml.py  student_files    submissions.zip
### copy_files_by_id.sh  README.md      student_results  test_compare_annot.py
### the submissions folder should produce the new assignment folder

### fix the folders if they had data before
rm -rf student_files
rm -rf student_results
rm -rf assignment_*
mkdir student_files
mkdir -p student_results/statistics 

### unzip the submissions
unzip submissions.zip
./copy_files_by_id.sh assignment_2932132_export student_files


### next is to run the Python script
python3 grader_xml.py answers.xml student_files student_results

### view results
pushd student_results/statistics
ls -alhrt
