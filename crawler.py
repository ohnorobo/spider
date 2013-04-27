#!/usr/bin/python

import re, pprint, httplib2, time
from BeautifulSoup import BeautifulSoup, SoupStrainer


seen = []
new = []
bad = []
robot = ""
base = ""


def start_crawl(seed):
    robot = get_robot(seed)
    robot = convert_robot(robot)

    new.append(seed)
    crawl()
    print seen


#########ROBOT####

# gets url for robots.txt from any url
# gets text of robots.txt
def get_robot(url):
    global base
    if "/" in url:
        base = re.match("*?/", url)
    else:
        base = url

    robot_url = base + "/robots.txt"
    return pull_page(robot_url)



#convert everything under that to a dict (ordered)
#find line "User-agent: *"
#key = base url
#value = True or False for allow/disallow
def convert_robot(robot_text):

    parsed_robot = {}
    user_agent = ""
    lines = robot_text.split("\n")

    for line in lines:
        if "User-agent" in line:
            user_agent = line[12:0]

        if user_agent == "*":
            parse_robot_line(line, parsed_robot)


def parse_robot_line(line, parsed_robot):
    if "Disallow: " in line:
        parsed_robot[base + line[10:]] = False;
    if "Allow: " in line:
        parsed_robot[base + line[8:]] = True;


#goes through robot.txt rules and returns is page is valid or not
def valid_for_robot(url, robot):
    page_allowed = True
    for key in robot.get_keys():
        if key in url:
            page_allowed = robot[key]




###########CRAWLING####

# finds new pages to visit
# ads visited pages to the list
def crawl():
    while len(seen) < 100 :
        if len(new) == 0:
            return 0 #break if no new links

        current_url = new[0]

        pprint.pprint(current_url)

        time.sleep(5)

        try :
            current_content = pull_page(current_url)

            seen.append(current_url)
            new.remove(current_url)

            current_links = extract_links(current_content)

            add_new_links(current_links)
        except: #for any problem make url bad
            bad.append(current_url)
            new.remove(current_url)

        print "#####"
        pprint.pprint(seen)
        print "#####"


#add unseen links to the crawl list
def add_new_links(links):
    for link in links:
        if (link not in seen) and (link not in bad):
            if ".pdf" not in link:
                new.append(link)
            else:
                seen.append(link) #add pdfs to list without crawling


########HTTP PARSING###

# pull down the content of a page
# return it as a string
def pull_page(url):
    status, response = httplib2.Http().request("http://" + url)
    return response


# takes page content
# extracts all links and returns a list
def extract_links(page):
    links = []

    for link in BeautifulSoup(page, parseOnlyThese=SoupStrainer('a')):
        if link.has_key('href'):
            url = link['href']
            if 'ccs.neu.edu' in url:
                links.append(url)
            if '.' in url[:-5]: #remove .html or .pdf
                print "skipping " + url
            else:
                links.append(base + "/" + url)

    return links


# Main
start_crawl("www.ccs.neu.edu")
