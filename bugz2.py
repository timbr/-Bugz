from tim_modules import toolbox
import xml.etree.ElementTree as etree
import datetime
import shelve

bugz = shelve.open('bugzdb.pydb')
#bugz={}

bug = '1185'
#onlyopen = True
onlyopen = False

def escapeunicode(text):
    return str(text.replace(u'\xb5', 'u').replace(u'\u2022', '*').replace(u'\u201c', '"').replace(u'\u201d', '"').replace(u'\u2014', '^').replace(u'\xa3', 'GBP').replace(u'\xb0', '^').replace(u'\u2018', "'").replace(u'\u2019', "'").replace(u'\u2026', "...").replace(u'\u2122', "(TM)").replace(u'\u2013', "-").replace(u'\u2265', ">=").replace(u'\u2264', "<=").replace(u'\xa0', "#").replace(u'\xb1', "+/-").replace(u'\xba', "^").replace(u'\xb3', "^3").replace(u'\xec', "i").replace(u'\xd8', "diam "))
    # \xb5 is 'mu', \u2022 is bullet point, \u201c is open quote, \u201d is close quote, \u2014 is degree sign (I think), \xa3 is pound sign, \xb0 is definitely degree sign, \u2018 and \u2019 is open and close single quotes, \u2026 is an ellipsis (...), \u2122 is a trademark symbol, \u2013 is a dash, \u2265 is greater than or equal to sign, \u2264 is less-than or equal to sign, \uxa0 is tilde sign, \xb1 is plus or minus sign, \xba is a degree sign, \xb3 is superscript 3,  \xec is accute i, \xd8 is diameter symbol
    
def altescapeunicode(text):
    UnicodeEquivalents = {
    '\xb5'  : 'u',
    '\u2022': '*',
    '\u201c': '"',
    '\u201d': '"',
    '\u2014': '^',
    '\xa3'  : 'GBP',
    '\xb0'  : '^',
    '\u2018': "'",
    '\u2019': "'",
    '\u2026': "...",
    '\u2122': "(TM)",
    '\u2013': "-"}
    
    #for code in UnicodeEquivalents:
        #text.replace(


def updatelocaldb():
    if 'lastupdated' in bugz.keys():
        dbLastUpdated = bugz['lastupdated']
    else:
        dbLastUpdated = datetime.datetime(2007, 01, 01)
        
    timeformat = format = "%Y-%m-%d"
    one_day = datetime.timedelta(days=1)
    today = datetime.datetime.today()
    #yesterday = (today - one_day).strftime(timeformat)
    day_before_last_updated = (dbLastUpdated - one_day).strftime(timeformat)
    urlstring = "\
http://bugzilla/spddesign/buglist.cgi?bug_file_loc=&bug_file_loc_type=allwordssubstr&\
bug_id=&bugidtype=include&chfieldfrom=" + day_before_last_updated + "&chfieldto=Now&chfieldvalue=&deadlinefrom=&\
deadlineto=&email1=&email2=&emailassigned_to1=1&emailassigned_to2=1&emailcc2=1&emailqa_contact2=1\
&emailreporter2=1&emailtype1=substring&emailtype2=substring&field-1-0-0=product\
&field0-0-0=noop&long_desc=&long_desc_type=substring&product=CXY%20Stage\
&product=Divisional%20Meeting%20Actions&product=inVia%20Cont.%20Eng.&product=inVia%20Specials\
&product=RA801%20D3&product=RA802%20Pharma&product=RenCam2&product=SEM-SCA&query_format=advanced\
&remaction=&short_desc=&short_desc_type=allwordssubstr&type-1-0-0=anyexact&type0-0-0=noop\
&value-1-0-0=CXY%20Stage%2CDivisional%20Meeting%20Actions%2CinVia%20Cont.%20Eng.%2CinVia%20\
Specials%2CRA801%20D3%2CRA802%20Pharma%2CRenCam2%2CSEM-SCA&value0-0-0=&title=Issue%20List&ctype=atom"
    
    xmlfile = toolbox.geturl(urlstring)
    tree = etree.parse(xmlfile)
    root = tree.getroot()
    
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        for title in entry.findall('{http://www.w3.org/2005/Atom}title'):
            changedbugs =  str(title.text.split(']')[0][7:]) # This was causing me a problem because the title was unicode whihc made the bug number unicode
            createdict(changedbugs, 'force')
            #createdict(changedbugs)
    
    bugz['lastupdated'] = today
        
                 

def createdict(bug, force='false'):
    if bug not in bugz.keys() or force == 'force':
        xmlfile = toolbox.geturl('http://bugzilla/spddesign/show_bug.cgi?ctype=xml&id=' + bug)
    
        print "Getting bug " + bug

        tree = etree.parse(xmlfile)
        root = tree.getroot()
        
        if bug in bugz.keys():
            bugz.pop(bug) # delete existing entry

        comment={}
        i=0
        for entry in root[0].findall('long_desc'):
            comment[i] = {'who': entry[0].text, 'when': entry[1].text, 'thetext': escapeunicode(entry[2].text)}
            i += 1

        bugz[str(root[0].find('bug_id').text)] = {
            'Desc': escapeunicode(root[0].find('short_desc').text),
            'Status': root[0].find('bug_status').text,
            'Topic': root[0].find('product').text,
            'Dependson': [depon.text for depon in root[0].findall('dependson')],
            'Blocks': [blck.text for blck in root[0].findall('blocked')],
            'Reporter': root[0].find('reporter').text,
            'Assignedto': root[0].find('assigned_to').text,
            'CC': [copy.text for copy in root[0].findall('cc')],
            'Comment': comment
            }
    #print bug
    for blocker in bugz[bug]['Dependson']:
        if str(blocker) not in bugz.keys():
            #print blocker
            createdict(str(blocker))


def findchildren(bug,tab):
    if tab==-1:
        desc = bugz[bug]['Desc']
        status = bugz[bug]['Status']
        timeformat = format = "%d-%m-%Y    %H:%M:%S"
        timenow = datetime.datetime.today().strftime(timeformat)
        part_text = bug + ' - ' + status + '::  ' + str(desc)
        date_text = 'As of: ' + timenow
        link = 'LINK="http://bugzilla/spddesign/show_bug.cgi?id=' + str(bug) +'" '
        f.write('<node STYLE="fork" ' + link + ' TEXT="' + part_text + '\n' + date_text + '">\n')
        f.write('<edge WIDTH="thin"/>\n')

    result = bugz[bug]['Dependson']
        
    if onlyopen == True:
        OpenList=[]
        for issue in result:
            if bugz[issue]['Status'] in ['NEW', 'ASSIGNED', 'REOPENED']:
                OpenList.append(issue)
        result = OpenList
        
    if result != []:
        if tab != -1:
            f.write(' FOLDED="true" >\n')
        tab+=1
        for row in result:
            material = row
            status = bugz[row]['Status']
            materialdesc = bugz[row]['Desc']
            html = materialdesc.replace('&' , '&amp;').replace('"' , '&quot;')
            line = material + ' - ' + status + '::  ' + html
            #print line

            link = 'LINK="http://bugzilla/spddesign/show_bug.cgi?id=' + str(row) +'" '
            f.write('<node ' + link + 'POSITION="right" TEXT="' + line + '"')
            next = findchildren(material, tab)
            if next != 'nochild':
                f.write('</node>\n')
    else:
        f.write('/>\n')
        return 'nochild'

updatelocaldb()
createdict(bug)
       
print "Bug:", bug
print "Desc:", bugz[bug]['Desc']
print "Status:", bugz[bug]['Status']
print "Topic:", bugz[bug]['Topic']

print "Depends on:", bugz[bug]['Dependson']
print "Blocks:", bugz[bug]['Blocks']

print "Reporter:", bugz[bug]['Reporter']
print "Assigned to:", bugz[bug]['Assignedto']

print "CC:", bugz[bug]['CC']

print "\n"



for num in range(len(bugz[bug]['Comment'])-1, -1, -1):
    print ">>>> " + bugz[bug]['Comment'][num]['who'] + "     " + bugz[bug]['Comment'][num]['when'] 
    print bugz[bug]['Comment'][num]['thetext'] 
    print '\n'

outputfile='bugmindmap.mm'
f=open(outputfile, 'w')
f.write('<map version="0.8.1">\n')
f.write('<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->\n')
findchildren(bug, -1)
f.write('</node>\n')
f.write('</map>\n')
f.close()
bugz.close()