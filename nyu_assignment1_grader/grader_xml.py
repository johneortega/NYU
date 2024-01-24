#/usr/bin/env python
### simple program to parse xml start end tags
### John Ortega jortega@cs.nyu.edu 02/09/2018
"""
This function will read in students' answers from 'path_student_answers' 
and print out the results to the console.
A '.txt' file will also be generated under the directory 'path_results' 
for each student, which contains elaborate information.

Before execution, please make sure that there exists a directory named 
'statistics' under 'path_results'. There will be two files output to this 
directory, which can be used to generate pooled annotation. 
python3 grader_xml.py adam_answers.xml student_xmls_bad student_results_test
"""

import sys
import os.path
import xml.etree.ElementTree as ET
import os
import operator
from collections import Counter

def parseXml(aFile,filetype="key"):
 
    # create element tree object
    tree = ET.parse(aFile)
 
    # get root element
    root = tree.getroot()
 
    # create empty dictionary for positions and vals
    positionKeys = {}

    # iterate news items
    for item in root.findall('./TAGS'):
        # iterate child elements of item
        for child in item:
            if child.tag == 'ADJECTIVE':
                start=0
                end=0
                startend=""
                if 'spans' in child.attrib:
                    startend = str(child.attrib['spans'])
                else:
                    if 'start' in child.attrib:
                        start=int(child.attrib['start'])
                        #if filetype=="student":
                        #    start=int(start)+1
                    if 'end' in child.attrib:
                        end=int(child.attrib['end'])
                        #if filetype=="student":
                        #    end=int(end)+1
                    if start>0 and end>0:
                        startend=str(start) + "~" + str(end)
                        # used as a key becuase later versions of MAE use it
                        #if filetype=="student":
                        #    print("creating student: " + startend)
                    else:
                        print("start/end tags don't exist")
                        sys.exit()
                positionVals = {}    
                for key, value in child.attrib.items():
                    positionVals[key] = value
                positionKeys[startend]=positionVals
    return positionKeys

def print_list(l, output):
    for item in l:
        output.write(str(item) + '\n')

# answer_key is a dictionary of keys 
# stud_key is the one to find
def check_keys(stud_key, answer_key):
    # this will be like 130~140 where the key may be 131~141
    stud_arr = stud_key.split('~')
    stud_begin = int(stud_arr[0])
    stud_end = int(stud_arr[1])
    for n in range(0,2): # check up to two positions out
        new_stud_begin = stud_begin + n
        new_stud_end = stud_end + n
        new_stud_key = str(new_stud_begin) + '~' + str(new_stud_end)
        if new_stud_key in answer_key:
            return True, new_stud_key
    return False, stud_key

    
        
def compare_annotation(key, student, output, statistic_correct, statistic_wrong_marked, statistic_failed_to_mark, statistic_marked_not_in_key, f1_total, prec_total, recall_total):
    correct = []
    failed_to_mark = []
    missing_tags = []

    for studKey,studVal in student.items():
        new_stud_key_passed, new_stud_key = check_keys(studKey,key)
        if new_stud_key_passed:
            try:
                ## check that morphology, position, and 
                morph = studVal['morphology']
                pos   = studVal['position']
                text  = studVal['text'] 
                if morph == key[new_stud_key]['morphology'] and pos   == key[new_stud_key]['position'] and text  == key[new_stud_key]['text']: 
                    correct.append(new_stud_key)
                    statistic_correct.append(new_stud_key)
                else:
                    if new_stud_key not in statistic_wrong_marked:
                        statistic_wrong_marked[new_stud_key] = []
                    statistic_wrong_marked[new_stud_key].append(studVal)
            except:
                if new_stud_key not in statistic_wrong_marked:
                    statistic_wrong_marked[new_stud_key] = []
                statistic_wrong_marked[new_stud_key].append(studVal)
        else:
            # this is the case where they marked somethign that was not found as a key
            # have to pass in value here
            # this is a dictionary with the key as the position
            # it will have a list of the values for that key
            if studKey not in statistic_marked_not_in_key:
                statistic_marked_not_in_key[studKey] = []
            statistic_marked_not_in_key[studKey].append(studVal)
    
    for profKey,profVal in key.items():
        if profKey not in student:
            failed_to_mark.append(profKey)
            statistic_failed_to_mark.append(profKey)
        else:
            if profKey not in correct:
                missing_tags.append(profKey)
                statistic_failed_to_mark.append(profKey)
            
    recall_value = 0.0
    precision_value = 0.0
    F1_value = 0.0
    if len(key.items()) > 0: 
        recall_value = len(correct)/float(len(key.items()))
    if len(student.items()) > 0:
        precision_value = len(correct)/float(len(student.items()))
    if (recall_value + precision_value) > 0:
        F1_value = 2.0*recall_value*precision_value/(recall_value + precision_value)
    
    print('correct instances = ', len(correct))
    print ('reca/ll = ', recall_value)
    print ('precision = ', precision_value)
    print ('F1 = ', F1_value, "\n")
    
    f1_total.append(F1_value)
    prec_total.append(precision_value)
    recall_total.append(recall_value)
    
    output.write('correct instances = '+str(len(correct))+'\n')
    output.write('recall = '+str(recall_value)+'\n')
    output.write('precision = '+str(precision_value)+'\n')
    output.write('F1 = '+str(F1_value)+'\n')
    output.write("\ncorrect("+str(len(correct))+")\n")
    print_list(correct, output)
    output.write("\nfailed_to_mark("+str(len(failed_to_mark))+")\n")
    print_list(failed_to_mark, output)

def main():
    keyFile=sys.argv[1]
    studDir=sys.argv[2]
    studResDir=sys.argv[3]
    if not os.path.isfile(keyFile) or not os.path.isdir(studDir) or not os.path.isdir(studResDir):
        print( "File or Directory doesn't exist")
        sys.exit()

    ## dictionaries contain positions like this 33~44 as keys
    ## then a dict of attributes
    ## {33-44}{morphology:present,X:Y}
    keyMap     = parseXml(keyFile)
    studentMap = {}
    statistic_correct = []
    statistic_wrong_marked = {}
    statistic_failed_to_mark = []
    statistic_marked_not_in_key = {}
    f1_total = []
    prec_total = []
    recall_total = []

    filelist = os.listdir(studDir)
    num = 1
    for infile in filelist:
        if infile[-4:] == '.xml':
            print (num)
            num = num+1
            print (infile)
        
            output_file = os.path.join(studResDir,infile[:-4]+'_Result.txt')
            output = open(output_file,'w')
            file_name = os.path.join(studDir,infile)
            studentMap = parseXml(file_name,"student")
            print('number of adjectives(answer key) = '+str(len(keyMap.items()))+'\n')
            print('number of adjectives(student) = '+str(len(studentMap.items()))+'\n')
            print(studentMap)
            output.write('number of adjectives(answer key) = '+str(len(keyMap.items()))+'\n')
            output.write('number of adjectives(student) = '+str(len(studentMap.items()))+'\n')

            compare_annotation(keyMap, studentMap, output, statistic_correct, statistic_wrong_marked, statistic_failed_to_mark, statistic_marked_not_in_key, f1_total, prec_total, recall_total)
            output.close()
        
    f = open(os.path.join(studResDir,'statistics/'+'statistic_correct.txt'),'w')
    statistic_c = Counter(statistic_correct)
    for s,v in statistic_c.most_common(80):
        #f.write(s+' :\t'+str(v)+'/'+str(num-1)+'\n')
        #f.write(s+' :\t'+ str(keyMap[s]['text']) + '\t' + str(v)+'/'+str(num-1)+'\n')
        f.write(s+' :\t'+ "text: " + str(keyMap[s]['text']) + '\t'+ "position: " + str(keyMap[s]['position']) + '\t' + "morphology: " + str(keyMap[s]['morphology']) + '\t'+ str(v)+'/'+str(num-1)+'\n')
    f.close()  

    '''
    f = open(os.path.join(studResDir,'statistics/'+'statistic_wrong_marked.txt'),'w')
    statistic_w = Counter(statistic_wrong_marked)
    for s,v in statistic_w.most_common(120):
        if s in keyMap:
            f.write(s+' :\t'+ "text: " + str(keyMap[s]['text']) + '\t'+ "position: " + str(keyMap[s]['position']) + '\t' + "morphology: " + str(keyMap[s]['morphology']) + '\t'+ str(v)+'/'+str(num-1)+'\n')
            #f.write(str(keyMap[s])+' :\t'+str(v)+'\n')
            for err in statistic_marked_not_in_key[the_key]:
                f.write('\t' + str(err)+'\n')
        else:
            f.write((s)+' position off:\t'+str(v)+'\n')
    f.close()
    '''

    f = open(os.path.join(studResDir,'statistics/'+'statistic_wrong_marked.txt'),'w')
    # dictionary with position as key and lists as value
    len_dict = {}
    for the_key, the_list in statistic_wrong_marked.items():
        len_dict[the_key] = len(the_list)
    for the_key, the_len in dict( sorted(len_dict.items(), key=operator.itemgetter(1),reverse=True)).items():
        f.write(the_key+' :\t'+ "text: " + str(keyMap[the_key]['text']) + '\t'+ "position: " + str(keyMap[the_key]['position']) + '\t' + "morphology: " + str(keyMap[the_key]['morphology']) + '\t'+ str(v)+'/'+str(num-1)+'\n')
        for example in statistic_wrong_marked[the_key]:
            f.write('\t'+ str(example)+'\n')
    f.close()
    
    f = open(os.path.join(studResDir,'statistics/'+'statistic_failed_to_mark.txt'),'w')
    statistic_f = Counter(statistic_failed_to_mark)
    for s,v in statistic_f.most_common(120):
        if s in keyMap:
            f.write(s+' :\t'+ "text: " + str(keyMap[s]['text']) + '\t'+ "position: " + str(keyMap[s]['position']) + '\t' + "morphology: " + str(keyMap[s]['morphology']) + '\t'+ str(v)+'/'+str(num-1)+'\n')
            #f.write(str(keyMap[s])+' :\t'+str(v)+'\n')
        else:
            f.write((s)+' position off:\t'+str(v)+'\n')
    f.close()
    
    f = open(os.path.join(studResDir,'statistics/'+'statistic_marked_not_in_key.txt'),'w')
    # dictionary with position as key and lists as value
    len_dict = {}
    for the_key, the_list in statistic_marked_not_in_key.items():
        len_dict[the_key] = len(the_list)
    for the_key, the_len in dict( sorted(len_dict.items(), key=operator.itemgetter(1),reverse=True)).items():
        f.write(the_key+' :\t'+ str(the_len) +': '+str(statistic_marked_not_in_key[the_key][0])+'\n')
    f.close()

    print( "writing files to: " + studResDir + "/statistics")
    f = open(os.path.join(studResDir,'statistics/'+'f1_all.txt'),'w')
    for a in f1_total:
        f.write(str(a) + '\n')
    f.close()
    f = open(os.path.join(studResDir,'statistics/'+'prec_all.txt'),'w')
    for a in prec_total:
        f.write(str(a) + '\n')
    f.close()
    f = open(os.path.join(studResDir,'statistics/'+'rec_all.txt'),'w')
    for a in recall_total:
        f.write(str(a) + '\n')
    f.close()
    #print( str(f1_total))
    #print( str(prec_total))
    #print( str(recall_total))
     
if __name__ == "__main__":
 
    # calling main function
    main()

