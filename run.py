import datetime as dt
import base64
import csv#set input file
import os.path

# ----------TEMPLATES----------

open_quiz = """<?xml version="1.0" ?>
    <quiz>\n"""

category_template = """<question type="category">
        <category>
            <text>$course$/{category}</text>
        </category>
    </question>\n"""

question_template = """<question type="multichoice">
     <!-- QUESTION TEXT -->
     <name>
         <text><![CDATA[{question_name}]]></text>
     </name>
     <questiontext format="html">
         <text><![CDATA[
                {question_text}
                ]]>
          </text>
     </questiontext>

      {answer_block}

    <!-- FEEDBACK TEXT -->
    <generalfeedback format="html"><text><![CDATA[{general_feedback}]]></text></generalfeedback>
    <correctfeedback format="html"><text><![CDATA[{correct_feedback}]]></text></correctfeedback>
    <incorrectfeedback format="html"><text><![CDATA[{incorrect_feedback}]]></text></incorrectfeedback>

    <!-- QUESTION SETTINGS -->
     <shuffleanswers>0</shuffleanswers>
     <single>true</single>
     <answernumbering>abc</answernumbering>

  </question>\n"""

image_template = '<p><img style="width: 100%;" src="data:image/image/png;base64,{image_string}" /></p>'

close_quiz = "</quiz>"


answer_template = """<answer fraction="{answer_fraction}">
        <text><![CDATA[{answer_text}]]></text>
        <feedback format="html"><text><![CDATA[{answer_feedback}]]></text></feedback>
     </answer>"""

log = "QUIZ XML CREATION LOGS"

# ----------FUNCTIONS----------

def read_input(input_file):
    """Prepares file into list"""
    csvfile = open(input_file, 'r', encoding="utf8")
    raw_list = csv.reader(csvfile, delimiter=',')
    return raw_list

def read_qs(raw_list):
    """Creates list of questions based on raw list"""
    q_list = []
    question = []
    for x in raw_list:
        if x[0] == "[START QUESTION]":
            question = []
        elif x[0] == "[END QUESTION]":
            q_list.append(question)
        elif x[0] == "CATEGORY NAME:":
            q_list.append([["category", x[2]]])
        elif len(x[0]) == 0 or x[0] in ("ANSWERS", "GENERAL FEEDBACK"):
            pass
        else:
            question.append(x[0:7])
    return q_list

def create_question_dict(one_list):
  """Creates the question dictionary from a list."""
  global log
  question_dict = {}

  for x in one_list:
    if x[0] == 'A' or x[0] == 'a':
      question_dict['A'] = x[2]
      question_dict['A_feedback'] = x[6]
    elif x[0] == 'B' or x[0] == 'b':
      question_dict['B'] = x[2]
      question_dict['B_feedback'] = x[6]
    elif x[0] == 'C' or x[0] == 'c':
      question_dict['C'] = x[2]
      question_dict['C_feedback'] = x[6]
    elif x[0] == 'D' or x[0] == 'd':
      question_dict['D'] = x[2]
      question_dict['D_feedback'] = x[6]
    elif x[0] == 'E' or x[0] == 'e':
      question_dict['E'] = x[2]
      question_dict['E_feedback'] = x[6]
    elif x[0] == 'F' or x[0] == 'f':
      question_dict['F'] = x[2]
      question_dict['F_feedback'] = x[6]
    elif x[0] == "CORRECT ANSWER:":
      question_dict["Answer"] = x[2]
    elif x[0] == "FEEDBACK TEXT:":
      question_dict["general_feedback"] = x[2]
    elif x[0] == "QUESTION NAME:":
        question_dict["question_name"] = x[2]
    elif x[0] == "QUESTION TEXT:":
        question_dict["question_text"] = x[2]
    elif x[0] == "QUESTION IMAGE FILENAME:":
        question_dict["question_image"] = x[2] + x[4]
    elif x[0] == "FEEDBACK IMAGE FILENAME:":
        question_dict["feedback_image"] = x[2] + x[4]
    elif x[0] == "category":
        question_dict["category"] = x[1]
    else:
      log = log  + " Unknown: " + x + "\n"

  if "question_image" in question_dict:
    if len(question_dict["question_image"]) > 0:
      try:
        filename = question_dict["question_image"]
        image_string = base64_image(filename)
        image_block = image_template.format(image_string=image_string)
        question_dict["question_text"] = question_dict["question_text"] + image_block
        log = log  + " [question img: %s]" % filename
      except:
        log = log + " [FAIL qustion img]"

  if "feedback_image" in question_dict:
    if len(question_dict["feedback_image"]) > 0:
      try:
        filename = question_dict["feedback_image"]
        image_string = base64_image(filename)
        image_block = image_template.format(image_string=image_string)
        question_dict["general_feedback"] = question_dict["general_feedback"] + image_block
        log = log + " [feedback img: %s]" % filename
      except:
        log = log + " [FAIL feedback img]"

  return question_dict

def create_quiz_parts(q_list):
    """Creates the quiz parts list of dictionaries from list of lists"""
    quiz_parts = []
    for x in q_list:
        y = []
        y = create_question_dict(x)
        quiz_parts.append(y)
    return quiz_parts


def create_answer_block(a):
  """Create the answer XML block from a dictionry."""

  c = a["Answer"]

  if c == 'A':
    correct = 1
  elif c == 'B':
    correct = 2
  elif c == 'C':
    correct = 3
  elif c == 'D':
    correct = 4
  elif c == 'E':
    correct = 5
  else:
    correct = 0
    print(str(a["question_name"]) + "\nWARNING: no answer marked as correct")

  answer_list = []

  if 'A' in a:
    answer_list.append([a['A'], a['A_feedback']])
  if 'B' in a:
    answer_list.append([a['B'], a['B_feedback']])
  if 'C' in a:
    answer_list.append([a['C'], a['C_feedback']])
  if 'D' in a:
    answer_list.append([a['D'], a['D_feedback']])
  if 'E' in a:
    answer_list.append([a['E'], a['E_feedback']])

  count = 1
  answer_block = "\n"

  for x in answer_list:
    answer_variables = {"answer_text": x[0],
                        "answer_feedback": x[1]}
    if count == correct:
      answer_variables["answer_fraction"] = 100
    else:
      answer_variables["answer_fraction"] = 0
    answer = answer_template.format(**answer_variables)
    answer_block = answer_block + answer
    count = count + 1

  return answer_block


def create_question_variables(question_dict, answer_block):
  """Combines the answer block with the question dictionry"""
  question_variables = question_dict
  question_variables["answer_block"] = answer_block
  return question_variables


def create_question(question_variables):
  """Create one question xml block."""
  question = question_template.format(**question_variables)
  return question


def create_output_file(final_xml, log):
  """Saves the output files."""
  timestamp = dt.datetime.now().strftime("%d-%b-%y_%H-%M")
  save_file = open("output_quiz_%s.xml" % timestamp, "w", encoding="utf-8")
  save_file.write(final_xml)
  save_file.close()

  save_log = open("logs_%s.txt" % timestamp, "w")
  save_log.write(log)
  save_log.close()

  print("xml created: output_quiz_%s.xml" % timestamp)


def base64_image(filename):
  """Takes a file name and returns a base64 encoded string."""
  with open(filename, "rb") as image_file:
      encoded_string = str(base64.b64encode(image_file.read()))
  x = list(encoded_string)
  x.pop()
  x.pop(1)
  x.pop(0)
  encoded_string = ''.join(x)
  return encoded_string

def create_question_block(question_dict):
  """Takes list of question variables and outputs xml."""
  answer_block = create_answer_block(question_dict)
  question_variables = create_question_variables(question_dict, answer_block)
  question_block = create_question(question_variables)
  return question_block

# ----------COMPILE QUIZ----------

#set input file
input_file = input('Enter name of csv file (.csv will be added): ')

input_file = input_file + '.csv'

if os.path.isfile(input_file):
    print("Processing: %s" % input_file)

    final_xml = ""

    final_xml = final_xml + open_quiz

    question_count = 0
    category_count = 0
    #
    raw_list = read_input(input_file)
    q_list = read_qs(raw_list)
    quiz_parts = create_quiz_parts(q_list)

    for x in quiz_parts:
      if len(x) == 1:
        y = category_template.format(category=x['category'])
        final_xml = final_xml + y
        log = log + "\n" + "###" + str(x['category']) + "###"
        category_count += 1
      else:
        try:
          x['correct_feedback'] = ''
          x['incorrect_feedback'] = ''
          y = create_question_block(x)
          final_xml = final_xml + y
          question_count += 1
          log = log + "\n" + str(question_count) + " %s" % x['question_name']
        except Exception as e:
          log = log + "\n" + "__Failure on: %s" % x['question_name']
          print("__Failure on: %s" % x['question_name'])
          print(e)

    print("Questions created: %s" % question_count)
    print("Categories created: %s" % category_count)

    final_xml = final_xml + close_quiz

    create_output_file(final_xml, log)
else:
    print("%s is not a file" % input_file)
