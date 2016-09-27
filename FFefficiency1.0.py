## FFefficiency v1.0
## 09/25/2016
## Prashant Padmanabhan
## This program computes the best possible team for each manager in any ESPN scoreboard page and calculates efficiency


# import required libraries
import urllib2
import re
from bs4 import BeautifulSoup
from operator import itemgetter, attrgetter, methodcaller
import HTML


# URL of the matchaup scoreboard page from ESPN
week = '1'
url = 'http://games.espn.com/ffl/boxscorequick?leagueId=207772&teamId=7&scoringPeriodId=1&seasonId=2016&view=scoringperiod&version=quick'

# Use BeautifulSoup to pull matchup tables and the number of players
page = urllib2.urlopen(url)
soup = BeautifulSoup(page,'html.parser')
div = soup.find('div', style='width: 49%; float: right;')
table = div.find_all('tr', {'class' : re.compile('pncPlayerRow*')})
num_players = len(table)
player_loop_count = num_players-1
team_name_cell = div.find('tr',class_='playerTableBgRowHead tableHead playertableTableHeader')
team_name = team_name_cell.get_text()
team_name = team_name[0:-10]

# Generate nested list of players on a team with all info and statstics
plist = []
points_list = []
team_list = ['Ari','Atl','Bal','Buf','Car','Chi','Cin','Cle','Dal','Den','Det','GB','Hou','Ind','Jax','KC','LA','Mia','Min','NE','NO','NYG','NYJ','Oak','Phi','Pit','SD','Sea','SF','TB','Ten','Wsh']
pos = ['QB','RB','WR','DE','DT','LB','S','CB','K','TE']

for i in range (0,player_loop_count):
    
    name = table[i].find('td',class_='playertablePlayerName')
    curr_name = name.get_text()
    names = re.split('\s+',curr_name)
    names = [s.strip(',') for s in names]
    points = table[i].find('td',class_='playertableStat appliedPoints appliedPointsProGameFinal')
    curr_points = points.get_text()
    points_list.append(float(curr_points))
    plist.append([a.encode('ascii','ignore') for a in names])
    if (len(plist[i]) > 3):
        plist[i][2] = plist[i][2]+','+plist[i][3]
        del plist[i][3]
    team_cut = [x for x in team_list if x in plist[i][-1]]
    #print team_cut
    #print plist
    temp = re.split(team_cut[0],plist[i][-1])
    plist[i][-1] = team_cut[0]
    plist[i].append(temp[1])
    plist[i].append(points_list[i])
    plist[i][0:-3] = [' '.join(plist[i][0:-3])]
    pos_cut = [x for x in pos if x in plist[i][2]]
    plist[i][2] = pos_cut[0]


# Create eleigible position list for each slot and sort player list by poistion and slice into slot lists
poslist = [['QB'],['RB'],['WR'],['TE'],['WR','TE'],['K'],['DT','DE'],['LB'],['S','CB']]

QBs = sorted([x for x in plist if x[2].upper() in poslist[0]],key=itemgetter(-1),reverse=True)
print QBs
RBs = sorted([x for x in plist if x[2].upper() in poslist[1]],key=itemgetter(-1),reverse=True)
WRs = sorted([x for x in plist if x[2].upper() in poslist[2]],key=itemgetter(-1),reverse=True)
TEs = sorted([x for x in plist if x[2].upper() in poslist[3]],key=itemgetter(-1),reverse=True)
FLEXs = sorted([x for x in plist if x[2].upper() in poslist[4]],key=itemgetter(-1),reverse=True)
Ks = sorted([x for x in plist if x[2].upper() in poslist[5]],key=itemgetter(-1),reverse=True)
DLs = sorted([x for x in plist if x[2].upper() in poslist[6]],key=itemgetter(-1),reverse=True)
LBs = sorted([x for x in plist if x[2].upper() in poslist[7]],key=itemgetter(-1),reverse=True)
DBs = sorted([x for x in plist if x[2].upper() in poslist[8]],key=itemgetter(-1),reverse=True)

# Get top players per position with FLEX being the top player subtracting the 2 best WRs and best TE
best_QB = QBs[0]
best_RB = [RBs[0],RBs[1]]
best_WR = [WRs[0],WRs[1]]
best_WR_names = [row[i] for row in best_WR for i in [0]]
best_TE = TEs[0]
best_TE_names = [best_TE[0]]
best_FLEX_possibilities = [row for row in FLEXs for i in [0] if row[i] not in best_WR_names and row[i] not in best_TE_names]
best_FLEX = best_FLEX_possibilities[0]
best_K = Ks[0]
#bestDL = ['Khalil Mack','Oak','DE,LB',3.5,8]
#print bestK
#print bestDL
best_DL = DLs[0]
best_LB = LBs[0]
best_DB = DBs[0]

# Compute played and best points and generate played and best team list for table generation also eff
played_points = 0
for i in range (0,11):
    played_points = played_points + plist[i][-1]
plist.append(['<b>TOTAL</b>','','',played_points])
played_team = plist[0:11]
played_team.append(plist[-1])

best_points = range(9)
best_points[0] = best_QB[3]
best_points[1] = sum([row[i] for row in best_RB for i in [3]])
best_points[2] = sum([row[i] for row in best_WR for i in [3]])
best_points[3] = best_TE[3]
best_points[4] = best_FLEX[3]
best_points[5] = best_DL[3]
best_points[6] = best_LB[3]
best_points[7] = best_DB[3]
best_points[8] = best_K[3]
best_team = [best_QB]+best_RB+best_WR+[best_FLEX]+[best_TE]+[best_LB]+[best_DL]+[best_DB]+[best_K]+[['<b>TOTAL</b>','','',sum(best_points)]]
efficiency = played_points/sum(best_points)


print plist
print '-'*79
print best_team

# Generate table
HTMLFILE = '%s - week %s.html' % (team_name,week)
f = open(HTMLFILE, 'w')

played_team_HTML = HTML.table(played_team,header_row=['Player','Team','Position','Points'])
best_team_HTML = HTML.table(best_team,header_row=['Player','Team','Position','Points'])
f.write('<div id="header" style="width:650px;text-align: center;"><p><b>'+team_name+'</p>'+'<p>Efficiency: '+str(round(100*efficiency,1))+'%</b></p>'+'</div><div id="header" style="width:650px;text-align: center;">'+'<div style="float: left">'+played_team_HTML+'</div>'+'<div style="float: right">'+best_team_HTML+'</div></div>')
f.write('<p>')

print '-'*79




