import unittest
import math
from gradescope_utils.autograder_utils.decorators import weight
import xml.etree.ElementTree as ET


class TestCompareAnnot(unittest.TestCase):
    def setUp(self):
        self.keyFile = 'answers.xml'
        self.studFile = 'submission.xml'
        self.localScore = 0
        self.localTest = True

    @weight(10)
    def test_compare_annot(self):
        ## dictionaries contain positions like this 33~44 as keys
        ## then a dict of attributes
        ## {33-44}{morphology:present,X:Y}
        keyMap = parseXml(self.keyFile, "key")
        studentMap = parseXml(self.studFile, "student")
        print('number of adjectives(answer key) = ' + str(len(keyMap.items())) + '\n')
        print('number of adjectives(student) = ' + str(len(studentMap.items())) + '\n')
        f1_score = compare_annotation(keyMap, studentMap)
        print('f1_score = ' + str(f1_score) + '\n')
        self.localScore = int(math.ceil(f1_score * 10))
        print('self local score = ' + str(self.localScore) + '\n')


def parseXml(aFile, filetype="key"):
    # create element tree object
    tree = ET.parse(aFile)

    # get root element
    root = tree.getroot()

    # create empty dictionary for positions and vals
    positionKeys = {}
    checkSpans1 = ['240~247', '673~682', '781~789', '1444~1451', '1280~1286']
    checkSpans2 = ['239~246', '672~681', '780~788', '1443~1450', '1279~1285']
    spansCheck = 0

    # iterate news items
    for item in root.findall('./TAGS'):

        # iterate child elements of item
        for child in item:
            if child.tag == 'ADJECTIVE':
                start = 0
                end = 0
                startend = ""
                if 'spans' in child.attrib:
                    startend = str(child.attrib['spans'])
                    # startend = str(start_) + '~' + str(end_)
                else:
                    if 'start' in child.attrib:
                        start = int(child.attrib['start'])
                        # if filetype=="student":
                        #    start=int(start)+1
                    if 'end' in child.attrib:
                        end = int(child.attrib['end'])
                        # if filetype=="student":
                        #    end=int(end)+1
                    if start > 0 and end > 0:
                        startend = str(start) + "~" + str(end)
                        # used as a key becuase later versions of MAE use it
                        # if filetype=="student":
                        #    print("creating student: " + startend)
                    else:
                        print("start/end tags don't exist")
                        sys.exit()
                positionVals = {}
                for key, value in child.attrib.items():
                    positionVals[key] = value
                positionKeys[startend] = positionVals
    if (filetype == 'student'):
        for spans in checkSpans1:
            if (spans in positionKeys.keys()):
                spansCheck += 1
        if (spansCheck == 0):
            for spans in checkSpans2:
                if (spans in positionKeys.keys()):
                    spansCheck += 1
            if (spansCheck > 0):
                newPK = {}
                for startend in positionKeys.keys():
                    # in some cases the span is correct_index-1
                    start_ = int(startend.split('~')[0]) + 1
                    end_ = int(startend.split('~')[1]) + 1
                    st_en = str(start_) + '~' + str(end_)
                    newPK[st_en] = positionKeys[startend]
                positionKeys = newPK
    return positionKeys


def print_list(l, key):
    for item in l:
        print(key[item]['text'] + ' (' + str(item) + ')\n')


def compare_annotation(key, student):
    correct = []
    failed_to_mark = []
    missing_tags = []
    for studKey, studVal in student.items():
    
        if studKey in key:
            ## check that morphology, position, and 
            morph = studVal['morphology']
            pos = studVal['position']
            text = studVal['text']
            if (morph == key[studKey]['morphology'] and pos == key[studKey]['position'] and text == key[studKey][
                'text']):
                correct.append(studKey)
    for profKey, profVal in key.items():
        if profKey not in student:
            failed_to_mark.append(profKey)  # profKey = start~end
        else:
            if profKey not in correct:
                missing_tags.append(profKey)

    recall_value = 0.0
    precision_value = 0.0
    F1_value = 0.0
    if len(key.items()) > 0:
        recall_value = len(correct) / float(len(key.items()))
    if len(student.items()) > 0:
        precision_value = len(correct) / float(len(student.items()))
    if (recall_value + precision_value) > 0:
        F1_value = 2.0 * recall_value * precision_value / (recall_value + precision_value)

    print('correct instances = ', len(correct))
    print('recall = ', recall_value)
    print('precision = ', precision_value)
    print('F1 = ', F1_value, "\n")

    return F1_value
