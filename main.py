import re
import requests
import datetime
from bs4 import BeautifulSoup
from python_utils import converters
import time
import zoneinfo
import tzlocal

HLTV_COOKIE_TIMEZONE = "America/Sao_Paulo"
HLTV_ZONEINFO = zoneinfo.ZoneInfo(HLTV_COOKIE_TIMEZONE)
LOCAL_TIMEZONE_NAME = tzlocal.get_localzone_name()
LOCAL_ZONEINFO = zoneinfo.ZoneInfo(LOCAL_TIMEZONE_NAME)
URL_BASE = "https://www.hltv.org/"
TEAM_MAP_FOR_RESULTS = []

PADRAO_HORA_MINUTO = r'^([01]\d|2[0-3]):([0-5]\d)$'

def _get_all_teams():
    if not TEAM_MAP_FOR_RESULTS:
        print("dentro do IF NOT")
        teams = get_parsed_page("https://www.hltv.org/stats/teams") ### MUDANDO LINK
        print("DENTRO DO _get_all_teams") ## DENTRO DO GET ALL TEAMS
        ##print(teams.find_all("td", {"class": ["teamCol-teams-overview"]}))
        for team in teams.find_all("td", {"class": ["teamCol-teams-overview"]}):
            print('teste teste')
            team = {'id': converters.to_int(team.find("a")["href"].split("/")[-2]), 'name': team.find("a").text, 'url': "https://hltv.org" + team.find("a")["href"]}
            TEAM_MAP_FOR_RESULTS.append(team)

def _findTeamId(teamName: str):
    print("dentro do FindTeamId")
    _get_all_teams()
    for team in TEAM_MAP_FOR_RESULTS:
        if team['name'] == teamName:
            return team['id']
    return None

def _padIfNeeded(numberStr: str):
    if int(numberStr) < 10:
        return str(numberStr).zfill(2)
    else:
        return str(numberStr)

def _monthNameToNumber(monthName: str):
    # Check for the input "Augu" and convert it to "August"
    # This is necessary because the input string may have been sanitized
    # by removing the "st" from the day numbers, such as "21st" -> "21"
    if monthName == "Augu":
        monthName = "August"
    return datetime.datetime.strptime(monthName, '%B').month

def get_parsed_page(url, delay=0.5):
    # This fixes a blocked by cloudflare error i've encountered
    headers = {
        "referer": "https://www.hltv.org/stats",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    cookies = {
        "hltvTimeZone": HLTV_COOKIE_TIMEZONE
    }

    time.sleep(delay)

    return BeautifulSoup(requests.get(url, headers=headers, cookies=cookies).text, "lxml")

def top5teams():
    home = get_parsed_page("https://hltv.org/")
    teams = []
    for team in home.find_all("div", {"class": ["col-box rank"], }):
        
        ## print("Time: ", team) ## printa o que vem
    
        team_href = team.find_all("a")[1]["href"] ## pega o Href
        pattern = r'\/(\d+)' ## padrão 

        if re.search(pattern, team_href):
            team_id = re.search(pattern, team_href).group(1)  # Isso extrairá o número correspondente
            # print(f"O número extraído é: {team_id}")
        else:
            print("Nenhum número encontrado na string.")

        team = {'id': team_id, 'name': team.text[3:], 'url': "https://hltv.org" + team.find_all("a")[1]["href"]}
        teams.append(team)
    return teams

def top30teams():
    page = get_parsed_page("https://www.hltv.org/ranking/teams/")
    teams = page.find("div", {"class": "ranking"})
    teamlist = []
    for team in teams.find_all("div", {"class": "ranked-team standard-box"}):
        newteam = {'name': team.find('div', {"class": "ranking-header"}).select('.name')[0].text.strip(),
                   'rank': converters.to_int(team.select('.position')[0].text.strip(), regexp=True),
                   'rank-points': converters.to_int(team.find('span', {'class': 'points'}).text, regexp=True),
                   'team-id': _findTeamId(team.find('div', {"class": "ranking-header"}).select('.name')[0].text.strip()),
                   'team-url': "https://hltv.org/team/" + team.find('a', {'class': 'details moreLink'})['href'].split('/')[-1] + "/" + team.find('div', {"class": "ranking-header"}).select('.name')[0].text.strip(),
                   'stats-url': "https://www.hltv.org" + team.find('a', {'class': 'details moreLink'})['href'],
                   'team-players': []}
        for player_div in team.find_all("td", {"class": "player-holder"}):
            player = {}
            player['name'] = player_div.find('img', {'class': 'playerPicture'})['title']
            player['player-id'] = converters.to_int(player_div.select('.pointer')[0]['href'].split("/")[-2])
            player['url'] = "https://www.hltv.org" + player_div.select('.pointer')[0]['href']
            newteam['team-players'].append(player)
        teamlist.append(newteam)
    return teamlist

def top_players():
    page = get_parsed_page("https://www.hltv.org/stats")
    players = page.find_all("div", {"class": "col"})[0]
    playersArray = []
    for player in players.find_all("div", {"class": "top-x-box standard-box"}):
        playerObj = {}
        playerObj['country'] = player.find_all('img')[1]['alt']
        buildName = player.find('img', {'class': 'img'})['alt'].split("'")
        playerObj['name'] = buildName[0].rstrip() + buildName[2]
        playerObj['nickname'] = player.find('a', {'class': 'name'}).text
        playerObj['rating'] = player.find('div', {'class': 'rating'}).find('span', {'class': 'bold'}).text
        playerObj['maps-played'] = player.find('div', {'class': 'average gtSmartphone-only'}).find('span', {'class': 'bold'}).text
        playerObj['url'] = "https://hltv.org" + player.find('a', {'class': 'name'}).get('href')
        playerObj['id'] = converters.to_int(player.find('a', {'class': 'name'}).get('href').split("/")[-2])
        playersArray.append(playerObj)
    return playersArray

def get_players(teamid):
    page = get_parsed_page("https://www.hltv.org/?pageid=362&teamid=" + str(teamid))
    titlebox = page.find("div", {"class": "bodyshot-team"})
    players = []
    for player_link in titlebox.find_all("a"):
        players.append({
            'id': converters.to_int(player_link["href"].split("/")[2]),
            'nickname': player_link["title"],
            'name': player_link.find("img")['title'],
            'url': "https://hltv.org" + player_link["href"]
        })

    return players

def get_team_info(teamid):
    """
    :param teamid: integer (or string consisting of integers)
    :return: dictionary of team

    example team id: 5378 (virtus pro)
    """
    page = get_parsed_page("https://www.hltv.org/?pageid=179&teamid=" + str(teamid))

    team_info = {}
    team_info['team-name'] = page.find("div", {"class": "context-item"}).text
    
    team_info['team-id'] = _findTeamId(page.find("div", {"class": "context-item"}).text)

    match_page = get_parsed_page("https://www.hltv.org/team/" + str(teamid) +
                                 "/" + str(team_info['team-name']) + "#tab-matchesBox")
    has_not_upcomming_matches = match_page.find(
        "div", {"class": "empty-state"})
    if has_not_upcomming_matches:
        team_info['matches'] = []
    else:
        match_table = match_page.find(
            "table", {"class": "table-container match-table"})
        team_info['matches'] = _get_matches_by_team(match_table)

    current_lineup = _get_current_lineup(page.find_all("div", {"class": "col teammate"}))
    team_info['current-lineup'] = current_lineup

    historical_players = _get_historical_lineup(page.find_all("div", {"class": "col teammate"}))
    team_info['historical-players'] = historical_players

    team_stats_columns = page.find_all("div", {"class": "columns"})
    team_stats = {}

    for columns in team_stats_columns:
        stats = columns.find_all("div", {"class": "col standard-box big-padding"})

        for stat in stats:
            stat_value = stat.find("div", {"class": "large-strong"}).text
            stat_title = stat.find("div", {"class": "small-label-below"}).text
            team_stats[stat_title] = stat_value

    team_info['stats'] = team_stats

    team_info['url'] = "https://hltv.org/stats/team/" + str(teamid) + "/" + str(team_info['team-name'])

    return team_info

### Pegar infos de times brasileiros por vetor
def get_brteams_info(myteamname):

    teamname = ""
    teamid = -1
    count = 0
    myteamname_dict = {}
    myteamid_dict = {
        "furia": 8297,
        "imperial": 9455,
        "pain": 4773,
        "fluxo": 11837,
        "oddik": 11768,
        "oplano": 10994,
        "mibr": 9215
    }

    for team in myteamname:
        print(myteamname)
        print(team)

        team_info = {}

        if myteamname[count] == "imperial" or myteamname[count] == "furia" or myteamname[count] == "pain" or myteamname[count] == "fluxo" or myteamname[count] == "oddik" or myteamname[count] == "oplano" or myteamname[count] == "mibr":
            print("Time -> ", team)
            teamid = myteamid_dict[team]
            teamname = team

            page = get_parsed_page("https://www.hltv.org/team/" + str(teamid) + "/" + teamname)

            team_info["team-name"] = teamname
            team_info["team-id"] = teamid

            match_page = get_parsed_page("https://www.hltv.org/team/" + str(teamid) +
                                        "/" + str(team_info['team-name']) + "#tab-matchesBox")
            
            match_table = match_page.find("table", {"class": "table-container match-table"})
            
            n_match = []
            nearest_match = {}
            
            hora_data_jogo = match_table.find("td", {"class": "date-cell"})("span")[0].text
            

            if re.match(PADRAO_HORA_MINUTO, hora_data_jogo):
                hora_jogo_global = int(hora_data_jogo.split(":")[0])
                print("hora jogo, ", hora_jogo_global)
                minutos_jogo_global = str(hora_data_jogo.split(":")[1])
                print("minutos jogo, ", minutos_jogo_global)
                
                hora_jogo_br = str(hora_jogo_global - 5)
                hora_data_jogo_br = hora_jogo_br + ":" + minutos_jogo_global
                print("HORA JOGO BR: ", hora_data_jogo_br)

                nearest_match["hora-data-jogo"] = hora_data_jogo_br
            else:
                nearest_match["hora-data-jogo"] = hora_data_jogo
            
            campeonato = match_table.find_all("a")[0].text
            nearest_match["campeonato"] = campeonato

            time_1 = match_table.find_all("a")[1].text
            nearest_match["time_1"] = time_1

            time_1_id = teamid
            nearest_match["team-1-id"] = time_1_id

            time_2 = match_table.find_all("a")[4].text
            nearest_match["time-2"] = time_2
            time_2_href = match_table.find_all("a")[4]["href"]
            pattern = r'\/(\d+)'
            if re.search(pattern, time_2_href):
                time_2_id = re.search(pattern, time_2_href).group(1)
                nearest_match["time-2-id"] = time_2_id
            else:
                time_2_id = "0000"
                nearest_match["time-2-id"] = time_2_id

            link_jogo = match_table.find_all("a")[5]["href"]
            nearest_match["link-jogo"] = URL_BASE+link_jogo
            
            n_match.append(nearest_match)
            team_info["nearest-match"] = n_match
            
            lineup = []
            players_table = page.find("div", {"class": "bodyshot-team g-grid"})
            #print("Players Section: ", players_section)

            player_1 = players_table.find_all("a")[0]("span")[1].text
            lineup.append(player_1)
            #print("Player 1: ", player_1)

            player_2 = players_table.find_all("a")[1]("span")[1].text
            lineup.append(player_2)
            #print("Player 2: ", player_2)

            player_3 = players_table.find_all("a")[2]("span")[1].text
            lineup.append(player_3)
            #print("Player 3: ", player_3)

            player_4 = players_table.find_all("a")[3]("span")[1].text
            lineup.append(player_4)
            #print("Player 4: ", player_4)

            player_5 = players_table.find_all("a")[4]("span")[1].text
            lineup.append(player_5)
            #print("Player 5: ", player_5)

            team_info["current-lineup"] = lineup

            historical_players = _get_historical_lineup(page.find_all("div", {"class": "col teammate"}))
            team_info["historical-players"] = historical_players

            team_stats_columns = page.find_all("div", {"class": "columns"})
            team_stats = {}

            for columns in team_stats_columns:
                stats = columns.find_all("div", {"class": "col standard-box big-padding"})

                for stat in stats:
                    stat_value = stat.find("div", {"class": "large-strong"}).text
                    stat_title = stat.find("div", {"class": "small-label-below"}).text
                    team_stats[stat_title] = stat_value

            team_info["stats"] = team_stats

            team_info["url"] = "https://hltv.org/stats/team/" + str(teamid) + "/" + str(team_info['team-name'])

            count += 1
            myteamname_dict[teamname] = team_info
        
        else:
            count += 1

    return myteamname_dict
### FIM DE PEGAR AS INFOS DE TIMES NO GERAL


def _get_current_lineup(player_anchors):
    """
    helper function for function above
    :return: list of players
    """
    players = []
    for player_anchor in player_anchors[0:5]:
        player = {}
        buildName = player_anchor.find("img", {"class": "container-width"})["alt"].split('\'')
        player['country'] = player_anchor.find("div", {"class": "teammate-info standard-box"}).find("img", {"class": "flag"})["alt"]
        player['name'] = buildName[0].rstrip() + buildName[2]
        player['nickname'] = player_anchor.find("div", {"class": "teammate-info standard-box"}).find("div", {"class": "text-ellipsis"}).text
        player['maps-played'] = int(re.search(r'\d+', player_anchor.find("div", {"class": "teammate-info standard-box"}).find("span").text).group())
        player['url'] = "https://hltv.org" + player_anchor.find("div", {"class": "teammate-info standard-box"}).find("a").get("href")
        player['id'] = converters.to_int(player_anchor.find("div", {"class": "teammate-info standard-box"}).find("a").get("href").split("/")[-2])
        players.append(player)
    return players

def _get_historical_lineup(player_anchors):
    """
    helper function for function above
    :return: list of players
    """
    players = []
    for player_anchor in player_anchors[5::]:
        player = {}
        buildName = player_anchor.find("img", {"class": "container-width"})["alt"].split('\'')
        player['country'] = player_anchor.find("div", {"class": "teammate-info standard-box"}).find("img", {"class": "flag"})["alt"]
        player['name'] = buildName[0].rstrip() + buildName[2]
        player['nickname'] = player_anchor.find("div", {"class": "teammate-info standard-box"}).find("div", {"class": "text-ellipsis"}).text
        player['maps-played'] = int(re.search(r'\d+', player_anchor.find("div", {"class": "teammate-info standard-box"}).find("span").text).group())
        player['url'] = "https://hltv.org" + player_anchor.find("div", {"class": "teammate-info standard-box"}).find("a").get("href")
        player['id'] = converters.to_int(player_anchor.find("div", {"class": "teammate-info standard-box"}).find("a").get("href").split("/")[-2])
        players.append(player)
    return players

def _generate_countdown(date: str, time: str):
    timenow = datetime.datetime.now().astimezone(LOCAL_ZONEINFO).strftime('%Y-%m-%d %H:%M')
    deadline = date + " " + time
    currentTime = datetime.datetime.strptime(timenow,'%Y-%m-%d %H:%M')
    ends = datetime.datetime.strptime(deadline, '%Y-%m-%d %H:%M')
    if currentTime < ends:
        return str(ends - currentTime)
    return None

MATCH_WITH_COUNTDOWN = None
def get_matches():
    print('entrou no get_matches')
    global MATCH_WITH_COUNTDOWN
    matches = get_parsed_page("https://www.hltv.org/matches/")
    matches_list = []

    matchdays = matches.find_all("div", {"class": "upcomingMatchesSection"})
    print(len(matchdays)) ##

    for match in matchdays:
        matchDetails = match.find_all("div", {"class": "upcomingMatch removeBackground"}) ##
        date = match.find({'div': {'class': 'matchDayHeadline'}}).text.split()[-1]
        print(match.find({'div': {'class': 'matchDayHeadline'}})) ##
        for getMatch in matchDetails:
            matchObj = {}

            matchObj['url'] = "https://hltv.org" + getMatch.find("a", {"class": "match a-reset"}).get("href")
            matchObj['match-id'] = converters.to_int(getMatch.find("a", {"class": "match a-reset"}).get("href").split("/")[-2])

            if (date and getMatch.find("div", {"class": "matchTime"})):
                timeFromHLTV = datetime.datetime.strptime(date + " " + getMatch.find("div", {"class": "matchTime"}).text,'%Y-%m-%d %H:%M').replace(tzinfo=HLTV_ZONEINFO)
                timeFromHLTV = timeFromHLTV.astimezone(LOCAL_ZONEINFO)
                matchObj['date'] = timeFromHLTV.strftime('%Y-%m-%d')
                matchObj['time'] = timeFromHLTV.strftime('%H:%M')

                matchObj['countdown'] = _generate_countdown(date, getMatch.find("div", {"class": "matchTime"}).text)

                if not MATCH_WITH_COUNTDOWN and matchObj['countdown']:
                    MATCH_WITH_COUNTDOWN = converters.to_int(getMatch.find("a", {"class": "match a-reset"}).get("href").split("/")[-2])

            if getMatch.find("div", {"class": "matchEvent"}):
                matchObj['event'] = getMatch.find("div", {"class": "matchEvent"}).text.strip()
            else:
                matchObj['event'] = getMatch.find("div", {"class": "matchInfoEmpty"}).text.strip()

            if (getMatch.find_all("div", {"class": "matchTeams"})):
                matchObj['team1'] = getMatch.find_all("div", {"class": "matchTeam"})[0].text.lstrip().rstrip()
                matchObj['team1-id'] = _findTeamId(getMatch.find_all("div", {"class": "matchTeam"})[0].text.lstrip().rstrip())
                matchObj['team2'] = getMatch.find_all("div", {"class": "matchTeam"})[1].text.lstrip().rstrip()
                matchObj['team2-id'] = _findTeamId(getMatch.find_all("div", {"class": "matchTeam"})[1].text.lstrip().rstrip())
            else:
                matchObj['team1'] = None
                matchObj['team1-id'] = None
                matchObj['team2'] = None
                matchObj['team2-id'] = None

            matches_list.append(matchObj)

    return matches_list

def get_results():
    results = get_parsed_page("https://www.hltv.org/results/")

    results_list = []

    pastresults = results.find_all("div", {"class": "results-holder"})

    for result in pastresults:
        resultDiv = result.find_all("div", {"class": "result-con"})

        for res in resultDiv:
            resultObj = {}

            resultObj['url'] = "https://hltv.org" + res.find("a", {"class": "a-reset"}).get("href")
            
            resultObj['match-id'] = converters.to_int(res.find("a", {"class": "a-reset"}).get("href").split("/")[-2])

            if (res.parent.find("span", {"class": "standard-headline"})):
                dateText = res.parent.find("span", {"class": "standard-headline"}).text.replace("Results for ", "").replace("th", "").replace("rd","").replace("st","").replace("nd","")

                dateArr = dateText.split()
                
                dateTextFromArrPadded = _padIfNeeded(dateArr[2]) + "-" + _padIfNeeded(_monthNameToNumber(dateArr[0])) + "-" + _padIfNeeded(dateArr[1])
                dateFromHLTV = datetime.datetime.strptime(dateTextFromArrPadded,'%Y-%m-%d').replace(tzinfo=HLTV_ZONEINFO)
                dateFromHLTV = dateFromHLTV.astimezone(LOCAL_ZONEINFO)

                resultObj['date'] = dateFromHLTV.strftime('%Y-%m-%d')
            else:
                dt = datetime.date.today()
                resultObj['date'] = str(dt.day) + '/' + str(dt.month) + '/' + str(dt.year)

            if (res.find("td", {"class": "placeholder-text-cell"})):
                resultObj['event'] = res.find("td", {"class": "placeholder-text-cell"}).text
            elif (res.find("td", {"class": "event"})):
                resultObj['event'] = res.find("td", {"class": "event"}).text
            else:
                resultObj['event'] = None

            if (res.find_all("td", {"class": "team-cell"})):
                resultObj['team1'] = res.find_all("td", {"class": "team-cell"})[0].text.lstrip().rstrip()
                resultObj['team1score'] = converters.to_int(res.find("td", {"class": "result-score"}).find_all("span")[0].text.lstrip().rstrip())
                resultObj['team1-id'] = _findTeamId(res.find_all("td", {"class": "team-cell"})[0].text.lstrip().rstrip())
                resultObj['team2'] = res.find_all("td", {"class": "team-cell"})[1].text.lstrip().rstrip()
                resultObj['team2-id'] = _findTeamId(res.find_all("td", {"class": "team-cell"})[1].text.lstrip().rstrip())
                resultObj['team2score'] = converters.to_int(res.find("td", {"class": "result-score"}).find_all("span")[1].text.lstrip().rstrip())
            else:
                resultObj['team1'] = None
                resultObj['team1-id'] = None
                resultObj['team1score'] = None
                resultObj['team2'] = None
                resultObj['team2-id'] = None
                resultObj['team2score'] = None

            results_list.append(resultObj)

    return results_list

def _get_matches_by_team(table):
    events = table.find_all("tr", {"class": "event-header-cell"})
    event_matches = table.find_all("tbody")
    matches = []
    for i, event in enumerate(events):

        event_name = event.find("a", {"class": "a-reset"}).text
        rows = event_matches[i]("tr", {"class": "team-row"})

        for row in rows[0:len(rows)]:
            match = {}
            dateArr = (row.find(
                "td", {"class": "date-cell"}).find("span").text).split('/')

            dateTextFromArrPadded = _padIfNeeded(dateArr[2]) + "-" + _padIfNeeded(dateArr[1]) + "-" + _padIfNeeded(dateArr[0])

            dateFromHLTV = datetime.datetime.strptime(dateTextFromArrPadded,'%Y-%m-%d').replace(tzinfo=HLTV_ZONEINFO)
            dateFromHLTV = dateFromHLTV.astimezone(LOCAL_ZONEINFO)

            date = dateFromHLTV.strftime('%Y-%m-%d')
            match['date'] = date
            match['teams'] = {}

            if (row.find(
                "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-1"})):
                match['teams']["team_1"] = row.find(
                    "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-1"}).text
                match['teams']["team_1_id"] = _findTeamId(row.find( "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-1"}).text)
            else:
                match['teams']["team_1"] = None
                match['teams']["team_1_id"] = None

            if (row.find(
                "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-2"})):
                match['teams']["team_2"] = row.find(
                    "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-2"}).text
                match['teams']["team_2_id"] = _findTeamId(row.find( "td", {"class": "team-center-cell"}).find("a", {"class": "team-name team-2"}).text)
            else:
                match['teams']["team_2"] = None
                match['teams']["team_2_id"] = None

            match["confront_name"] = match['teams']["team_1"] or "TBD" + \
                " X " + match['teams']["team_2"] or "TBD"
            match["championship"] = event_name
            match_url = row.find(
                "td", {"class": "matchpage-button-cell"}).find("a")['href']
            match['match_id'] = converters.to_int(match_url.split("/")[-2])
            match['url'] = "https://www.hltv.org" + match_url
            match['time'] = get_parsed_page("https://www.hltv.org" + match_url).find(
                'div', {"class": "timeAndEvent"}).find('div', {"class": "time"}).text
            matches.append(match)

    return matches

def get_results_by_date(start_date, end_date):
    # Dates like yyyy-mm-dd  (iso)
    results_list = []
    offset = 0
    # Loop through all stats pages
    while True:
        url = "https://www.hltv.org/stats/matches?startDate="+start_date+"&endDate="+end_date+"&offset="+str(offset)

        results = get_parsed_page(url)

        # Total amount of results of the query
        amount = int(results.find("span", attrs={"class": "pagination-data"}).text.split("of")[1].strip())

        # All rows (<tr>s) of the match table
        pastresults = results.find("tbody").find_all("tr")

        # Parse each <tr> element to a result dictionary
        for result in pastresults:
            team_cols = result.find_all("td", {"class": "team-col"})
            t1 = team_cols[0].find("a").text
            t1_id = _findTeamId(team_cols[0].find("a").text)
            t2 = team_cols[1].find("a").text
            t2_id = _findTeamId(team_cols[1].find("a").text)
            t1_score = int(team_cols[0].find_all(attrs={"class": "score"})[0].text.strip()[1:-1])
            t2_score = int(team_cols[1].find_all(attrs={"class": "score"})[0].text.strip()[1:-1])
            map = result.find(attrs={"class": "statsDetail"}).find(attrs={"class": "dynamic-map-name-full"}).text
            event = result.find(attrs={"class": "event-col"}).text
            dateText = result.find(attrs={"class": "date-col"}).find("a").find("div").text
            url = "https://hltv.org" + result.find(attrs={"class": "date-col"}).find("a").get("href")
            match_id = converters.to_int(url.split("/")[-2])
            dateArr = dateText.split("/")
            # TODO: yes, this shouldn't be hardcoded, but I'll be very surprised if this API is still a thing in 21XX
            startingTwoDigitsOfYear = "20"
            dateTextFromArrPadded = startingTwoDigitsOfYear + _padIfNeeded(dateArr[2]) + "-" + _padIfNeeded(dateArr[1]) + "-" + _padIfNeeded(dateArr[0])

            dateFromHLTV = datetime.datetime.strptime(dateTextFromArrPadded,'%Y-%m-%d').replace(tzinfo=HLTV_ZONEINFO)
            dateFromHLTV = dateFromHLTV.astimezone(LOCAL_ZONEINFO)

            date = dateFromHLTV.strftime('%Y-%m-%d')

            result_dict = {"match-id": match_id, "team1": t1, "team1-id": t1_id, "team2": t2, "team2-id": t2_id, "team1score": t1_score,
                           "team2score": t2_score, "date": date, "map": map, "event": event, "url": url}

            # Add this pages results to the result list
            results_list.append(result_dict)

        # Get the next 50 results (next page) or break
        if offset < amount:
            offset += 50
        else:
            break

    return results_list

def get_match_countdown(match_id):
    url = "https://www.hltv.org/matches/" + str(match_id) + "/page"
    match_page = get_parsed_page(url)
    timeAndEvent = match_page.find("div", {"class": "timeAndEvent"})
    date = timeAndEvent.find("div", {"class": "date"}).text
    time = timeAndEvent.find("div", {"class": "time"}).text
    dateArr = date.replace("th of","").replace("rd of","").replace("st of","").replace("nd of","").split()
    dateTextFromArrPadded = _padIfNeeded(dateArr[2]) + "-" + _padIfNeeded(_monthNameToNumber(dateArr[1])) + "-" + _padIfNeeded(dateArr[0])

    dateFromHLTV = datetime.datetime.strptime(dateTextFromArrPadded,'%Y-%m-%d').replace(tzinfo=HLTV_ZONEINFO)
    dateFromHLTV = dateFromHLTV.astimezone(LOCAL_ZONEINFO)

    date = dateFromHLTV.strftime('%Y-%m-%d')

    return _generate_countdown(date, time)

if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter()
    

    """
    pp.pprint('get_matches')
    pp.pprint(get_matches())
    
    pp.pprint('top5')
    pp.pprint(top5teams())
    """

    pp.pprint('INFOS TIMES BR')
    pp.pprint(get_brteams_info(["mibr", "imperial"]))
    
    """
    pp.pprint('get_team_info')
    pp.pprint(get_team_info('8297'))
   
    pp.pprint('top30')
    pp.pprint(top30teams())

    pp.pprint('top_players')
    pp.pprint(top_players())

    pp.pprint('get_players')
    pp.pprint(get_players('6665'))

    pp.pprint('get_team_info')
    pp.pprint(get_team_info('6665'))

    pp.pprint('get_matches')
    pp.pprint(get_matches())

    pp.pprint('get_results')
    pp.pprint(get_results())

    pp.pprint('get_results_by_date')
    today_iso = datetime.datetime.today().isoformat().split('T')[0]
    pp.pprint(get_results_by_date(today_iso, today_iso))

    pp.pprint('get_match_countdown')
    pp.pprint(get_match_countdown(MATCH_WITH_COUNTDOWN))
    """
