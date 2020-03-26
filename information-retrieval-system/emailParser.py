# Import the email modules we'll need
import os
from email.parser import BytesParser, Parser
from email.policy import default
from  email import  message_from_string
# Achal Shah and Praful Johari

import xml.etree.cElementTree as ET
from xml.dom import minidom
from xml.parsers.expat import ExpatError

def getEmail(mail_file):
    def readEmail(mail_file):
        with open(mail_file) as f:
            lines = f.readlines()
        actual_email = lines[:-8]
        startLine = 0
        try:
            while actual_email[startLine].find("From")==-1:
                startLine += 1
            return True, "".join(actual_email[startLine:])
        except IndexError as err:
            print("from missing error happened in {}".format(mail_file))
            return False, ""
    
    flag, email_text  = readEmail(mail_file)
    if False == flag:
        return  flag, dict()
    email = dict()
    email["header"] =  Parser(policy=default).parsestr(email_text)
    email["message"] ="{}".format(  email["header"].get_payload())
    return True, email

getEmail("./HillaryEmails/HillaryEmails/1.txt")


def prettyPrintXML(elem):
    # Return a pretty-printed XML string for the Element.
    generatedXML = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(generatedXML)
    return reparsed.toprettyxml(indent="  ")
def printXML(elem):
    # Return a pretty-printed XML string for the Element.
    generatedXML = ET.tostring(elem, 'utf-8')
    return  generatedXML

def addDocument(batchRoot, documentID, documentData):
    document = ET.SubElement(batchRoot, "document")
    # document.set("id", documentID)
    idElement = ET.SubElement(document, "id");
    idElement.text = documentID;
    for tag, value in documentData.items():
        # print tag, value
        tagElement = ET.SubElement(document, tag)
        tagElement.text = value

def parseMultiLine(dataset):
    # Parsing the dataset
    # print "Started Multiline Parse"
    text = ""
    line = dataset.readline()
    while line != "" and line[0] != ".":
        text = text + line.strip()
        if text[-1] == "\n":
            text = text[:-1]

        text = text + " "
        line = dataset.readline()
    return text.rstrip(),line

def parseDirectory(directory):
    files = os.listdir(directory)
    # files = files[8:9]
    return [ (files[index].split(".")[0], directory+ "/"+files[index]) for index in range(len(files))]
def testXMLCompatibility(docid, document):
    tmp = ET.Element("root")
    addDocument(tmp, docid, document)
    try:
        prettyPrintXML(tmp)
    except ExpatError as err:
        return False
    return True

LIMIT = 200000
Warning = set()
# Warning.add(9)
def parseDataset(directory, batchRoot):
    dataset = parseDirectory(directory)
    count = 0
    for item in dataset:
        count += 1
        if count > LIMIT:
            return
        if count in Warning:
            continue
        doc_id = item[0]
        doc_file = item[1]
        flag, email = getEmail(doc_file)
        if flag:
            document = dict()
            try:
                document["from"] = "{}".format(email["header"]["from"])
                document["to"] = "{}".format(email["header"]["to"])
                document["subject"] = "{}".format(email["header"]["subject"])
                document["body"] = email["message"] if email["message"]!=None else ""
                if True == testXMLCompatibility(doc_id, document):
                    addDocument(batchRoot, doc_id, document)
                else:
                    print("XMLCompatibility: error happened in {}".format(doc_file))
            except IndexError as err:
                print("IndexError: other key missing error happened in {}".format(doc_file))
            except AttributeError as err:
                print("AttributeError: unknown missing error happened in {}".format(doc_file))

# Generating XML
dataFileObject = open("emaildataset.xml", "w")

root = ET.Element("root")

parseDataset("./HillaryEmails/HillaryEmails", root)

tree = prettyPrintXML(root)
if tree:
    dataFileObject.write(tree)
dataFileObject.close()
