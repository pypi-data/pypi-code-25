import psycopg2, sys, pdb
from xml.etree.ElementTree import ElementTree, tostring, fromstring
from ucca import convert

# extracts all the concluded evaluation results of the specified users
# cur.execute("CREATE TABLE mtEvalOutput (id SERIAL PRIMARY KEY, output TEXT NOT NULL,
# mtTaskId INTEGER, uid INTEGER, status INTEGER, ts timestamp)")

def get_uid(host_name, db_name, username):
    "Returns the uid matching the given username."
    con = psycopg2.connect(host=host_name, database=db_name)
    c = con.cursor()
    c.execute("SELECT id FROM users WHERE username=%s", (username,))
    cur_uid = c.fetchone()
    if cur_uid == None:
        raise Exception("The user " + username + " does not exist")
    return int(cur_uid[0])

def output_entry(t):
    "Prints the tuple."
    print('===================')
    for x in t:
        if isinstance(x,bytes):
            print(x.decode('utf8'))
        elif isinstance(x,str):
            print(x.encode('utf8'))
        else:
            print(x)

if len(sys.argv) != 7:
    print('Usage: extract_annot_dump.py <usernames :-delimited> <passage offset> <T for only submitted passages> <passage id minimum> <passage id maximum> <T if full format, F for index>')
    sys.exit(-1)

host_name = "pgserver"
db_name = "work"
only_submitted = (sys.argv[3] == 'T')
paid_min = int(sys.argv[4])
paid_max = int(sys.argv[5])
users = []
usernames = sys.argv[1].split(':')
passage_offset = int(sys.argv[2])
format = ('full' if sys.argv[6] == 'T' else 'index')


for u in usernames:
    cur_uid = get_uid(host_name, db_name, u)
    users.append(cur_uid)

con = psycopg2.connect(host=host_name, database=db_name)
c = con.cursor()

for uname,uid in zip(usernames,users):
    if only_submitted:
        c.execute("SELECT xml,ts,paid,id FROM xmls WHERE uid=%s AND paid >= %s AND paid <= %s AND status=1 ORDER BY ts DESC",(uid,paid_min,paid_max))
    else:
        c.execute("SELECT xml,ts,paid,id FROM xmls WHERE uid=%s AND paid >= %s AND paid >= %s ORDER BY ts DESC",(uid,paid_min,paid_max))
        #c.execute("SELECT xml,ts,paid,id FROM xmls WHERE uid=%s ORDER BY ts DESC",(uid,))
        
    seen_paid = []
    for r in c.fetchall():
        raw_xml = r[0]
        ts = r[1]
        paid = r[2]
        xid = r[3]
        if paid not in seen_paid:
            seen_paid.append(paid)
            P = convert.from_site(fromstring(raw_xml))
            if format == 'full':
                output_entry([uname,paid-passage_offset,raw_xml,convert.to_text(P)[0],ts])
            else:
                print(str(paid-passage_offset)+' '+str(xid))






