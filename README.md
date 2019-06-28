# BagrupWize
A project for analyzing student WhatsApp groups for Matach - developed as part of TalpiHack 06/19

## General Flow

Get WhatsApp export file (.txt) - this is done manually  (lets say it’s named X.txt)

Create ‘export dir’ with the export file and param.txt file of a known format (see later)

Run parsing & analysis (python) script that gets only the export dir as param (export_parser.py)

The script will write several files into export_dir:
- X.txt.csv - a csv file with single msg analysis, some cleanup and anonymization
- X.txt.no_heb.csv - same as X.txt.csv but only data fields, so no hebrew (simpler)
- X_names.csv - the anonymization names keymap (name => anonymous_name)
- X.txt.csv.p - pickle (python pickle) file which is the input for the analysis script
- student.csv - deeper analysis result - stats per student - when was he active and in what way. Note especially the assists column which  shows the number of times we think this student helped someone. It shows pretty good results! If you sort by the assists, you can identify more and less helpful students
- trends.png - a plot of activity trends of specific students who showed a significant change in their activity. 

## Important Release Note
We had issues with hebrew encoding, and eventually the script ran only on one of our laptops (a Mac). If the script fails on encoding errors when trying to read the WhatsApp export file, add hebrew encoding.

### Additional Notes: 
- The csv file can be opened and analyzed in Excel/GoogleSheets too. 
- We provided some Excel analysis as well.
- The analysis digestion should be published via the existing dashboard in the future
- Anonymization/standardization of names is done by turning the names to STUDENT_X (where X is a running index).
- The main teacher name is replaced by MAIN_TEACHER. Other teachers names are replaced by TEACHER_X (X a running index)

### Known Issues
- Msgs with a ‘:’ aren’t parsed correctly - need to be handled or at least removed. Currently they need to be removed manually
- Multi-line msgs are combined into one msg, but several consecutive msgs of the same user aren’t combined
- New msgs is identified by ‘2019/’ which isn’t nice
- Fix teacher-analyzation and create meaningful presentation
- The x-label of the trends graph (histogram actually) can be confusing - it represents the accumulated amount of messages in the group, and hence it is proportional to the date - bigger x-values represent later dates. You can use the dates instead (we prefered to split the whole conversation to chunks in the same size, and not by date). 
- trends.png plot has some issues with axis which we didn’t have time to fix, so sometimes it’s not created.

### Implementation notes
- Student trends were analyzed using chunks by number of msgs and not by time period
- Some msgs are identified as spam and removed as part of the parsing. That’s also the reason why the id has jumps. Spam identificators:
- “Spam senders” - list of names (in params.txt) of irrelevant senders (like ויקי)
- “Spam” words - a hard-coded set of words like “you changed the subject”
- Detecting questions - we saw detecting ? is good enough, and works better than using question keywords (because a lot of question keywords appear not as part of a question, and a lot of questions doesn’t have a question keyword)
- All keywords (subject-relevant, ack, encouragement etc.) are hard-coded and can be easily edited in BagrupWize.parsing.keywords.py
- In students.csv file there are always 100 students, even if less than 100 students participated in the group. The ones who didn’t participate appear with zeros in all cols.

### Single Line CSV format (X.txt.csv)
- DATE - dd/mm/yyyy 
- TIME - hh:mm 
- ID - msg id (number)
- SENDER (anonymized and standardized - STUDENT_X)
- TEXT_LENGTH - will be 0 for the “special” texts mentioned above
- NUM_KEYWORDS - number of subject-relevant keywords in the msg
- IS_RELEVANT_TO_SUBJECT -  does the msg contains subject-relevant keywords?
- IS _QUESTION - is the msg a question?
- IS_INFORMATIVE - defined as relevant to the subject and not a question (e.g. an answer)
- IS_ENCOURAGE - encouragement messages (e.g. good job!)
- IS_ACK - understanding acknowledgments (e.g. Got it)
- IS_LEFT_GROUP - is this a “left group” msg
- IS_MEDIA_OMITTED - is this “media omitted” messages
- TEXT - The msg whole text (multi line msgs are combined into 1 line), or one of the following:
- LEFT_GROUP
- MEDIA_OMITTED 

### params.txt format
group_type=<MATH/HEBREW>

group_code=<4 digit code of the group - e.g. 8375>

spam_names=<names, separated by commas of irrelevant msg senders>

teacher_name=<name of the main teacher>

other_teacher_names=<names,separated by commas of other teachers in the group>

---

Lesson times:    (A list of start times of all the lessons)

<yyyy,mm,dd,hh,mm>

<...>

<...>

End

Note: No spaces are allowed!


Enjoy :)
