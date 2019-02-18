##R Running the app using debug=True allows the app to auto-update every time the code gets edited.

import os
from flask import *
import re
import mail_client

app = Flask(__name__)
app.debug = True

## flag the grid as frozen - disable all buttons
frozen = 0

grid_df = None
available = []
visitors = [None] * 10
home = [None] * 10

if frozen != 0:
    # this are the randomly generated intersection points of home/visitor (favorite/underdog)
    visitors=[8, 1, 4, 0, 6, 9, 5, 3, 2, 7]
    home=[5, 7, 4, 9, 1, 0, 2, 8, 3, 6]



def read_csv(filename):
    header = None
    data = []
    with open(filename,'r') as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            line = line.rstrip('\n\r ').split(',')
            if not header:
                header = line
            else:
                data.append(dict(zip(header,line)))

    return header, data

def to_csv(data,filename,ordered=None):
    if data is not None and len(data) > 0:
        header = data[0].keys()
        if ordered is not None: header=ordered
        with open(filename,'w') as f:
            f.write(",".join(header) + "\n")
            for d in data:
                line = [str(d[k]) for k in header ]
                f.write(",".join(line) + "\n")


# map out the 100 points on the grid: home digit, visitor digit
if frozen:
    _ , grid_df = read_csv('grid.csv')
    vcol, hcol = [], []
    for i in range(10):
        # make a block array of the same is visitor digit[i]
        vcol.extend([ visitors[i] ]*10) 
        # duplicate all 10 home digits per each visitior digit[i]
        hcol.extend(home)

    for j in range(len(hcol)):
        grid_df[j]['home_digit'] = hcol[j]
        grid_df[j]['vstr_digit'] = vcol[j]


    ## box_number, user_id, home_digit, vstr_digit
    to_csv(grid_df,'grid.csv',ordered=['box_number','user_id','home_digit','vstr_digit'])



def get_available(df,current_user):
    try:
        ##vv = df[pd.isnull(df['user_id']) | (df['user_id'] == current_user) ]
        ##return vv["box_number"].tolist()
        vv = []
        for d in df:
            if d['user_id'] in ['nan','NaN','None','none','',current_user]:
                vv.append(int(d['box_number']))
        return vv
    except:
        return []



@app.route("/show_grid",methods=['GET','POST'])
def show_grid(*args,**kwargs):
    ## grid.csv:
    ## box_number, user_id, home_digit, vstr_digit
    global grid_df
    global available
    global frozen
    global visitors
    global home


    current_user = request.form['current_user']


    ## create lock file
    if not os.path.exists('grid.lock'):

        if not frozen:
            with open('grid.lock', 'w') as lockfile:
                lockfile.write(current_user + "\n")
            print("grid locked. user=" + current_user)

        ## get number of boxes allotted
        _ , pdf = read_csv('players.csv')
        ## select_limit = int(pdf[pdf['user_id'] == current_user ]['box_limit'])
        ## hard coded select limit at 10, this is default in register as well
        select_limit = 10
        for d in pdf:
            if d['user_id'] == current_user:
                select_limit = int(d['box_limit'])

        print('select limit=',select_limit)

        _ , grid_df = read_csv('grid.csv')
        available = get_available(grid_df,current_user)
        # box_numbers = grid_df['box_number'].tolist()
        box_numbers = [ d['box_number'] for d in grid_df]
        box_ids= ["box_%s" % x for x in box_numbers]

        box_owners = []
        for d in grid_df:
            if d['user_id'] in ['nan','NaN','None','none','']:
                if frozen:
                    box_owners.append('----')
                else:
                    box_owners.append('null')
            else:
                box_owners.append(d['user_id'])

        ## create (id,owner) tuple list
        boxes = list(zip(box_ids,box_owners))

        ## create (id, score_value) list for H/V row/column labels
        home_digits = [("home_%d" % i,s) for i,s in enumerate(home)]
        vstr_digits = [("vstr_%d" % i,s) for i,s in enumerate(visitors)]

        return render_template('grid.html',
                                boxes=boxes,
                                home_digits=home_digits,
                                vstr_digits=vstr_digits,
                                current_user=current_user,
                                select_limit=select_limit,
                                frozen=frozen)
    else:
        ## try again later page
        return render_template('try_again.html',current_user=current_user)



@app.route("/save_submit", methods=['GET','POST'])
def save_submit(*args,**kwargs):
    global grid_df
    global available
    global frozen
    global visitors
    global home

    ## grab the returned select boxed string
    ## and post it back to grid.csv
    ## just checking for button press
    if (request.form['save_button'] != '' ):
        picked = request.form['picked']
        print ("picked= " + picked)
        current_user = request.form['current_user']
        ## strip off tags and get box index
        ## picked is a string = 'box_1,box_23,box_4'...
        picked = picked.replace("box_","")
        if not frozen:
            chosen = []
            if len(picked) > 0:
                try:
                    chosen = [int(x) for x in picked.split(",")]
                    print(chosen)
                    for box in chosen:
                        ## update grid with newly selected box
                        #grid_df.loc[box-1,'user_id'] = current_user
                        grid_df[box-1]['user_id'] = current_user
                except:
                    print("box selection error")

            new_available = [x for x in available if x not in chosen]
            ## make sure new available are marked correctly
            for i in new_available:
                #grid_df.loc[i-1,'user_id'] = None
                grid_df[i-1]['user_id'] = None

            ## box_number, user_id, home_digit, vstr_digit
            to_csv(grid_df,'grid.csv',ordered=['box_number','user_id','home_digit','vstr_digit'])

        if os.path.exists('grid.lock'):
            os.remove('grid.lock')
            print("grid released.")

    return render_template("menu_page.html",current_user=current_user,msg="")



## clear the lock of grid if the current user locked it
## and is not on the grid edit page
@app.route("/release_grid",methods=['GET','POST'])
def release_grid(*args,**kwargs):
    current_user = request.form['current_user']
    if os.path.exists('grid.lock'):
        with open('grid.lock', 'r') as lockfile:
            user = lockfile.readline().rstrip("\n\r ")
        if user == current_user:
            os.remove('grid.lock')
            print("dangling lock released. user=" + user)
    ## return empty response
    return ('', 204)



## get you back to the main page
@app.route("/show_menu",methods=['GET','POST'])
def show_menu(*args,**kwargs):
    current_user = request.form['current_user']
    return render_template("menu_page.html",current_user=current_user, msg="")



## read in the stadnings file to post
def post_file_standings():
    header = None
    data = []
    with open('standings.csv','r') as standings:
        while True:
            item = standings.readline()
            if not item:
                break
            item = item.rstrip('\r\n ').split(',')
            if not header:
                header = [x.upper() for x in item]
            else:
                data.append(item)

    return header, data


## calculate
def update_standings():
    header = None
    grid_map = {}
    with open('grid.csv','r') as grid:
        while True:
            box = grid.readline()
            if len(box) == 0:
                break
            box = box.strip('\n\r ').split(',')
            if not header:
                header = box
            else:
                try:
                    m = dict(zip(header,box))
                    v, h = int(m['vstr_digit']), int(m['home_digit'])
                    grid_map[(v,h)] = dict(user_id=m['user_id'], wins=[0,0,0,0,0,0])
                except:
                    pass

    header = None
    with open('scores.csv','r') as scores:
        while True:
            score = scores.readline()
            if len(score) == 0:
                break
            score = score.strip('\n\r ').split(',')
            if not header:
                header = score
            else:
                s = dict(zip(header,score))
                rnd, v_pts, h_pts = int(s['round']), int(s['v_pts']), int(s['h_pts'])
                total = v_pts + h_pts
                v = v_pts % 10
                h = h_pts % 10

                ## imcrement total for that box for the current round
                if total > 0 and ((v,h) in grid_map):
                    grid_map[(v,h)]['wins'][rnd - 1] += 1

    purse = [50,100,200,400,800,2000]
    #purse = [1,2,4,8,16,32]

    ## collect all winnings per user_id
    standings = []
    players = {}
    for player in grid_map.values():
        take = [x[0]*x[1] for x in list(zip(purse,player['wins']))]
        try:
            y = players[player['user_id']]
            w = [x[0]+x[1] for x in list(zip(y,take))]
            players[player['user_id']] = w
        except:
            players[player['user_id']] = take

    for k in players:
        v = players[k]
        #create a row list of [user_id, R1, R@, .. , total winnings]
        standings.append([k] + v + [sum(v)])

    ## sort by winning totals
    standings.sort(key=lambda x: -x[7])

    header = 'user_id R1 R2 R3 R4 R5 R6 total'.split()
    ##sdf = pd.DataFrame(columns=header,data=standings)
    ##sdf.to_csv('standings.csv',index=False)
    sdf = [ dict(zip(header,x)) for x in standings]
    to_csv(sdf,'standings.csv',ordered=header)

    ## caps for display
    header = [x.upper() for x in header]
    return header, standings


@app.route("/show_standings",methods=['GET','POST'])
def show_standings(*args,**kwargs):
    current_user = request.form['current_user']
    if not frozen:
        msg = r'No Standings.|Standings Will Be Posted Once Games Begin.'
        return render_template('menu_page.html',current_user=current_user, msg=msg)

    ## header, data = post_file_standings()
    header, data = update_standings()
    return render_template('standings.html',
                                current_user=current_user,
                                header=header,
                                data=data)


@app.route("/")
def index(*args,**kwargs):
    return render_template("login_page.html",msg="")

@app.route("/show_login")
def show_login(*args,**kwargs):
    return render_template("login_page.html",msg="")



## creates a comma delimited string of all winners in each of the 63 games
def winners_to_str(scores,grid):

    grid_map = {}
    for box in grid:
        vstr, home = int(box['vstr_digit']), int(box['home_digit'])
        user_id = box['user_id']
        if user_id in ['nan','NaN','None','none','']: user_id = ''
        grid_map[(vstr,home)] = user_id

    winners = []
    which = []
    for game in scores:
        v_pts, h_pts = int(game['v_pts']), int(game['h_pts'])

        ## map out which team won
        highlight = "null"
        if v_pts < h_pts: highlight = "H"
        if v_pts > h_pts: highlight = "V"
        which.append(highlight)

        winner = 'null'
        if (v_pts + h_pts) > 0:
            try:
                v = v_pts % 10
                h = h_pts % 10
                winner = grid_map[(v,h)]
            except:
                pass
        winners.append(winner)

    return ",".join(winners), ",".join(which)


@app.route("/show_scores",methods=['GET','POST'])
def show_scores(*args,**kwargs):

    current_user = request.form['current_user']

    if not frozen:
        msg = r'No Scoreboard.|Scores Will Be Posted Once Games Begin.'
        return render_template('menu_page.html', current_user=current_user, msg=msg)

    header = None
    games = []
    scores = []
    with open('scores.csv','r') as score_file:
        while True:
            item = score_file.readline()
            if not item:
                break
            item = item.rstrip('\r\n ').split(',')
            ## header: 'round,game,visitor,home,v_pts,h_pts'
            if not header:
                header = item
            else:
                line = dict(zip(header,item))
                game = int(line['game'])
                tags = ["%s_%d" % (x,game) for x in ['box','vstr','home','vv','hh','who']]
                ## pull of round col and game num
                ## creates ['box_1,vstr_1,home_1,vv_1,hh_1,who_1,visitor,home,v_pts,h_pts']
                ## abbreviate long team names
                names = [ x[:9] for x in [line['visitor'],line['home']] ]
                games.append(tags + names + [ line['v_pts'],line['h_pts'] ] )
                scores.append(line)

    header = None
    grid = []
    with open('grid.csv','r') as grid_file:
        while True:
            ## box_number,user_id,home_digit,vstr_digit
            item = grid_file.readline()
            if not item:
                break
            item = item.rstrip('\r\n ').split(',')
            if not header:
                header = item
            else:
                line = dict(zip(header,item))
                grid.append(line)

    winners, which = winners_to_str(scores,grid)
    return render_template('scores.html',
                            current_user=current_user,
                            winners=winners,
                            which=which,
                            games=games)




@app.route("/login", methods=['POST'])
def login(*args,**kwargs):

    ##user_id,name,email,box_limit,passwd,pool_id
    _ , players_df = read_csv('players.csv')
    user_id = request.form['userid']
    passwd = request.form['passwd']
    #pool_id = request.form['poolid']
    #pool_id = pool_id.strip()

    # if user_id in players_df['user_id'].tolist():
    if user_id in [x['user_id'] for x in players_df ]:
        #pdf = players_df[players_df['user_id'] == user_id ]
        pdf = [x for x in players_df if x['user_id'] == user_id ]
        #valid_pwd = (passwd in pdf['passwd'].tolist())
        valid_pwd = (passwd in [ x['passwd'] for x in pdf ])
        # valid_pool = (pool_id in pdf['pool_id'].tolist())
        #if valid_pwd and valid_pool and pool_id != '':
        if valid_pwd:
            ## set up user
            return render_template('menu_page.html',current_user=user_id, msg="")
        else:
            #error = r'Invalid Login.|Please Check Password and PoolId.'
            error = r'Invalid Login.|Please Check Password.'
            return render_template('login_page.html',msg=error)
    else:
        error = r'Invalid UserId.|<' + user_id + r'>  Has Not Been Registered'
        return render_template('login_page.html',msg=error)


## NOTE pool_id is handed out by me
## give me a way to organize players
## and allow them to gain access to the grid (AFTER THEY PAY!)
## -- therefore once they register - you have to put the
## -- poolid in for each players by hand..
## TDOO - might want to have an email alert to me
## -- that a new user has registered.
##
## Also the number of boxes is controlled by me - it will
## default to 1, but updated by me if additional boxes are
## desired

def validated(name,email,user_id,passwd,confirm,players_df):

    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    name_regex = re.compile(r"^([a-zA-Z]{2,}\s[a-zA-z]{1,}'?-?[a-zA-Z]{2,}\s?([a-zA-Z]{1,})?)$")
    userid_regex = re.compile(r"([a-zA-Z0-9_]+$)")

    inputs = dict(name=name,email=email,user_id=user_id)

    if not name_regex.match(name):
        inputs['name'] = ''
        return r"Invalid Name.|Please Enter First and Last Name", inputs
    if not email_regex.match(email):
        inputs['email'] = ''
        return r"Invalid Email.|Please Valid Email Address", inputs
    if not userid_regex.match(user_id):
        inputs['user_id'] = ''
        return r"Invalid UserId.|Userid Contains Letters and Numbers Only", inputs
    if len(user_id) < 6:
        inputs['user_id'] = ''
        return r"Invalid UserId.|Userid Must Be At Least 6 Characters.", inputs
    if  "," in passwd:
        return r"Invalid Password.|Password Contains Commas", inputs
    if len(passwd) < 6:
        return r"Invalid Password.|Password Must Be At Least 6 Characters.", inputs
    if passwd != confirm:
        return r"Invalid Password.|Password and Confirm Do Not Match.", inputs

    ##userids = [ x.lower() for x in players_df['user_id'].tolist() ]
    userids = [ x['user_id'].lower() for x in players_df ]
    if user_id.lower() in userids:
        return r'Invalid UserId.|'+user_id+ r' Has Already Been Registered', inputs

    return None, inputs


def email_me(new_user):

    rules = """
    <html>

    <head>
    </head>

    <body>
    <div style="font-family: Verdana;">
    <br>
    <span style="font-size:18px; color:#000000;">Welcome <strong>{name} ['{user_id}']</strong>, to the MegaBox March Madness Pool!</span>
    <br>
    <br>
    <div class="rules" style="border: 2px solid; background-color: #f2f2f2;padding:10px;width:1000px; font-family: Lucida Sans; font-size:16px; color:#000000;">
    <div class="rule_header" style="position:absolute; top:90px; left: 350px; font-size:18px; color:#000000;"><strong>Rules of the Game</strong></div>
    <ol>
    <br>
    <li>The game works like a standard "Football Box" Pool. &nbsp;Each player buys a box (Entry Fee = 100 per box) in a 10-by-10 grid.</li><br>
    <li>Each box in the grid represents the intersection of the last digits of the final score for each tournment game.</li><br>
    <li>The digits across the TOP of the grid represent the last digit in the final score from THE FAVORITE (The Higher Team Seed).</li><br>
    <li>The digits across the SIDE of the grid represent the last digit in the final score from THE UNDERDOG (The Lower Team Seed).</li><br>
    <li>The digits for the game grid will be drawn the Wednesday evening prior to start of the tournament.</li><br>
    <li>Your box numbers apply for EVERY game in the tournament.<br><br><strong>Whenever ANY tournament game's final score lands on your box - YOU WIN!</strong></li><br>
    </ol>
   
    
    <div>
    <br>
    <span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>Payouts Per Game --- By Round</strong></span> 
    <br> <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 1 (32 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            50 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 2 (16 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            100 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 3 (8 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            200 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 4 (4 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            400 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 5 (2 games)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            800 pts
        </td>
      </tr>
      <tr>
        <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Round 6 (NCAA Final)</strong>
        </td>
        <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            2000 pts
        </td>
      </tr>
    </table>
    <br>
    <br>
    </div>

    </div>
    <br>
    <span style="font-size:18px; color:#000000;">Go Choose Your Box At The Weblink Below!<br>Good Luck!</span>
    <br>
    <br>
    <a href="http://www.megaboxhoops.com/" style="font-size: 20px; text-decoration: none">March Madness MegaBox Pool</a>
    </div>

    </body>
    </html>
    """

    rules = rules.format(name=new_user['name'],user_id=new_user['user_id'])
    subject = "Welcome to The MegaBox March Madness Pool"
    mail_client.mail(new_user['email'],subject,text='',html=rules)

    ## email me about the new user
    subject = 'MegaBox March Madness Pool: New Player: %s' % new_user['name']
    player_table = """
    <html>
    <head>
    </head>
    <body>
    <br>
    <span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>NEW PLAYER</strong></span> 
    <br> <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="100" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Name</strong>
        </td>
        <td width="300" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            {name}
        </td>
      </tr>
      <tr>
        <td width="100" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>User_Id</strong>
        </td>
        <td width="300" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            {user_id}
        </td>
      </tr>
      <tr>
        <td width="100" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>Email</strong>
        </td>
        <td width="300" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
            {email}
        </td>
      </tr>
    </table>
    </body>
    </html>
    """

    player_table = player_table.format(name=new_user['name'],user_id=new_user['user_id'],email=new_user['email'])
    mail_client.mail("megaboxhoops@gmail.com",subject,text='',html=player_table)


@app.route("/show_register")
def show_register(*args,**kwargs):
    info = r'Provide Name and Email Address|Create a UserId and Password.'
    return render_template("register_page.html",msg=info,
                                                iname='',
                                                iemail='',
                                                iuser_id='')

def get_pool_id():
    ## generates pool_id fror new players
    ## this is the private key you email them so the can get into
    ## the site
    ## with multiple pools - this will be a handle pool assignment
    return 'megabox'
    

@app.route("/register", methods=['POST'])
def register(*args,**kwargs):
    name = request.form['fullname']
    email = request.form['email']
    user_id= request.form['userid']
    passwd = request.form['passwd']
    confirm= request.form['confirm']
    # players_df = pd.read_csv('players.csv')
    header, players_df = read_csv('players.csv')
    error, inputs = validated(name,email,user_id,passwd,confirm,players_df)
    if error == None:
        new_user=dict(user_id=user_id,
                      name=name,
                      email=email,
                      box_limit=10,
                      amount_paid=0,
                      passwd=passwd,
                      pool_id=get_pool_id())

        ## NOTE: box_limit is the fixed limit on how many boxes a player can select
        ## i.e. a registered players can pick up to 10 boxes.

        ## NOTE: pool_id is presently disabled- it allows for delination for multiple
        ## pools - all functionality for it is disabled or commented out presently.

        if len(players_df) == 0:
            players_df = [new_user]
        else:
            players_df.append(new_user)

        header = 'email user_id name passwd pool_id box_limit amount_paid'.split()
        to_csv(players_df,'players.csv',ordered=header)


        email_me(new_user)

        ## take them back to login page, and let them know they are registered
        thanks="Thanks %s [%s]!|You're Registered." % (inputs['name'],inputs['user_id'])
        return render_template('login_page.html',msg=thanks)
    else:
        return render_template('register_page.html', msg=error,
                                            iname=inputs['name'],
                                            iemail=inputs['email'],
                                            iuser_id=inputs['user_id'])




if __name__ == "__main__":
    app.run(debug=True,threaded=True)




