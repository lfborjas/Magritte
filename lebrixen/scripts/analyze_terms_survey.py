#!/usr/bin/env python

#Script to retrieve and analyze the survey in polldaddy.com
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
import os
from simplejson import loads, dumps
SURVEY_ID = '676440' #the term extraction survey
QUESTIONS_ORIGIN_FILE = '%s/Descargas/%s.html' % (os.environ['HOME'], SURVEY_ID) #the term extraction default file


def get_questions(survey_id=SURVEY_ID, origin = QUESTIONS_ORIGIN_FILE):

    if not hasattr(origin, 'read'):
        raise Exception('The origin must be a file-like object')

    #try to get 'em from the file
    questions_file = '%s_questions.json' % survey_id
    if os.path.exists(questions_file):
        print 'Getting questions from a file'
        f = open(questions_file, 'r')
        rval= loads(f.read())
        f.close()
        return rval
    else:
        #the file doesn't exist, retrieve the url and parse it as a soup:
        soup = BeautifulSoup(origin.read())
        questions = {}
        for question in soup('div', attrs={'class': 'box type-100'}):
            question_number = question.find('span', "number").string
            question_text = question.find('td', "question").string
            questions.update({question_number : question_text.strip()})

        #write the questions to a file for future extractions:
        if questions:
            wf = open(questions_file, 'w')
            wf.write(dumps(questions))
            wf.close()
            
        return questions

def get_answers(survey_id=SURVEY_ID, origin=None):
    if not hasattr(origin, 'read'):
        raise Exception('The origin must be a file-like object')

    answers_file = '%s_answers.json' % survey_id

    answers = {}

    #load the previous answers from the file, if they exist:
    if os.path.exists(answers_file):
        print 'Getting answers from file'
        f = open(answers_file, 'r')
        answers= loads(f.read())
        f.close()

    soup = BeautifulSoup(origin.read())
    for question in soup('div', attrs={'class': 'box type-100'}):
        question_number = question.find('span', "number").string
        question_answers = [qtext.p.string for qtext in question('td', 'answer-text')]
        answers.update({question_number: question_answers})

    if answers:
        wf = open(answers_file, 'w')
        wf.write(dumps(answers))
        wf.close()

    return answers

if __name__ == '__main__':
    #questions_url = "http://polldaddy.com/surveys/%s/report/q-and-a" % survey_id
    origin_file = open(QUESTIONS_ORIGIN_FILE, 'r')
    questions = get_questions(origin=origin_file)
    answers = get_answers(origin=origin_file)
    print questions, answers




