from Team import Team
from Game import Game
# from Player import Player
import requests
from bs4 import BeautifulSoup
from bs4 import element
import time
import os
from asciimatics.screen import Screen
import fake_useragent

base_url = 'https://nba.hupu.com/games'
line_height = 5


# Not sure how to use it efficiently
def GetStatDicTemplate():
    dict_stat_template = {}
    dict_stat_template['name'] = ''
    dict_stat_template['time'] = ''
    dict_stat_template['pos'] = ''
    dict_stat_template['shooting'] = ''
    dict_stat_template['3-point'] = ''
    dict_stat_template['ft'] = ''
    dict_stat_template['fReb'] = 0
    dict_stat_template['bReb'] = 0
    dict_stat_template['reb'] = 0
    dict_stat_template['assist'] = 0
    dict_stat_template['foul'] = 0
    dict_stat_template['steal'] = 0
    dict_stat_template['turnover'] = 0
    dict_stat_template['block'] = 0
    dict_stat_template['score'] = 0
    dict_stat_template['eff'] = ''

    return dict_stat_template


def get_header():
    location = os.getcwd() + '/agent.json'
    ua = fake_useragent.UserAgent(path=location)
    return ua.random


def ClearScreen(screen):
    for i in range(0, screen.height + 1):
        screen.move(0, i)
        screen.draw(screen.width, i, char=' ')

    screen.refresh()


def DrawBoard(screen, row, col=3, line_height=5, line_width=25):
    for i in range(0, row + 1):
        screen.move(0, i * line_height)
        screen.draw(line_width * col, i * line_height, char='-')

    for i in range(0, col + 1):
        screen.move(i * line_width, 0)
        screen.draw(i * line_width, line_height * row + 1, char='|')
    screen.refresh()
    return


def GetAllGamesList():
    headers = {"User-Agent": get_header()}
    base_r = requests.get(url=base_url, headers=headers)
    base_content = BeautifulSoup(base_r.content, features='html.parser')

    all_game_lists = base_content.find_all('div', {'class': 'list_box'})

    return all_game_lists


def GetElementsByClass(item, tag, class_name):
    if item.find_all(tag, {'class': class_name}) is not None:
        return item.find_all(tag, {'class': class_name})


def GetOneElementByClass(item, tag, class_name, default_value=''):
    if item.find(tag, {'class': class_name}) is not None:
        return item.find(tag,  {'class': class_name})
    else:
        return default_value


def GetTextOfItem(item, default_value=''):
    if item is not None and isinstance(item, element.Tag):
        return item.get_text()
    else:
        return default_value


def CheckAllGamesOver(all_game_lists):
    keywords = '已结束'
    if all(keywords in item.time for item in all_game_lists):
        return True
    else:
        return False


def GetAllGames(all_game_lists, all_games_finished):
    index = 'A'
    games_list = []
    for item in all_game_lists:
        team_vs = GetOneElementByClass(item, 'div', 'team_vs')
        team_details_div = GetElementsByClass(team_vs, 'div', 'txt')

        team_score_a = GetOneElementByClass(team_details_div[0], 'span', 'num')
        team_score_b = GetOneElementByClass(team_details_div[1], 'span', 'num')

        team_score_a = GetTextOfItem(team_score_a, '0')
        team_score_b = GetTextOfItem(team_score_b, '0')

        team_name_a = GetTextOfItem(team_details_div[0].find('a'))
        team_name_b = GetTextOfItem(team_details_div[1].find('a'))

        team_a = Team(name=team_name_a, score=team_score_a)
        team_b = Team(name=team_name_b, score=team_score_b)

        team_vs_time = GetOneElementByClass(team_vs, 'span', 'b')
        team_vs_time = GetTextOfItem(team_vs_time, '      未开始')

        games_list.append(Game(index, team_a, team_b, team_vs_time))

        index = chr(ord(index) + 1)
    return games_list


def GetDetailTable(content_table):
    table_details = []
    header_row_tr = []

    try:
        header_row_tr = content_table.find_all('tr')[0]
    except Exception:
        return table_details

    table_header = []
    for td_item in header_row_tr.find_all('td'):
        table_header.append(td_item.get_text().strip())

    table_details.append(table_header)

    for item in content_table.find_all('tr')[1:-2]:
        one_row = []
        for index, td_item in enumerate(item.find_all('td')):
            td_text = td_item.get_text().strip()
            if index == 0 and len(td_text) > 10:
                td_text = td_text[td_text.find('-') + 1:]
            one_row.append(td_text)
        table_details.append(one_row)

    return table_details


def GetScoreInSection(live_content):
    score_in_section_table = GetOneElementByClass(
        live_content, 'table', 'itinerary_table')
    score_in_section_away_table = GetOneElementByClass(
        score_in_section_table, 'tr', 'away_score')
    score_in_section_home_table = GetOneElementByClass(
        score_in_section_table, 'tr', 'home_score')

    away_score_list = ['0', '0', '0', '0']
    home_score_list = ['0', '0', '0', '0']
    away_index = 0
    home_index = 0
    for item in score_in_section_away_table.find_all('td')[1:-1]:
        away_score_list[away_index] = item.get_text().strip()
        away_index += 1

    for item in score_in_section_home_table.find_all('td')[1:-1]:
        home_score_list[home_index] = item.get_text().strip()
        home_index += 1

    return away_score_list, home_score_list


def GetOneGameDetails(all_game_lists, str_index):
    table_details = {}
    index = ord(str_index) - ord('A')
    score_live = GetOneElementByClass(all_game_lists[index], 'a', 'd')

    score_live_r = requests.get(score_live['href'])
    score_live_content = BeautifulSoup(score_live_r.content,
                                       features='html.parser')

    score_live_content_core = GetOneElementByClass(
        score_live_content, 'div', 'gamecenter_content_l')
    score_live_content_core_table_away = score_live_content_core.find(
        'table', {'id': 'J_away_content'})  # special one
    score_live_content_core_table_home = score_live_content_core.find(
        'table', {'id': 'J_home_content'})  # special one

    if score_live_content_core_table_away is None or \
       score_live_content_core_table_home is None:
        return table_details

    table_details_away = GetDetailTable(score_live_content_core_table_away)
    table_details_home = GetDetailTable(score_live_content_core_table_home)

    score_in_section_away, score_in_section_home = GetScoreInSection(
        score_live_content)

    table_details['away_player_details'] = table_details_away
    table_details['home_player_details'] = table_details_home
    table_details['away_section_scores'] = score_in_section_away
    table_details['home_section_scores'] = score_in_section_home

    return table_details


def DrawScoresInDetailsPage(screen, game, col_width_away_total, start_row):
    game_info_a = '{0}:{1}'.format(game.teamA.name, game.teamA.score)
    screen.print_at(game_info_a, int(col_width_away_total / 2), start_row)

    game_info_b = '{0}:{1}'.format(game.teamB.name, game.teamB.score)
    screen.print_at(game_info_b, int(col_width_away_total * 3 / 2), start_row)

    screen.print_at(game.time.strip(), col_width_away_total, start_row)

    return


def DrawScoreInSection(screen, score_in_sections, start_col_index, start_row):
    section_index = 1
    screen.print_at('节次', start_col_index - 5, start_row + 2)
    screen.print_at('比分', start_col_index - 5, start_row + 3)
    for item in score_in_sections:
        screen.print_at(str(section_index), start_col_index, start_row + 2)
        screen.print_at(item, start_col_index, start_row + 3)
        start_col_index += 3
        section_index += 1

    return


def DrawOneGameDetailsCore(screen, table_items, width_list,
                           col_width_total, row, col=0):
    col_width_away_total = 0
    valid_list_width = [x for x in width_list if x != 0]

    for item in table_items:
        col_index = 0
        valid_index = 0
        col_width_away_total = 0
        for row_item in item:
            if width_list[col_index] == 0:
                pass
            else:
                col_coord = valid_index * valid_list_width[valid_index] + 1
                if valid_index > 0:
                    col_coord = valid_list_width[0] + \
                        (valid_index - 1) * valid_list_width[valid_index] + 1
                if col_width_total != 0:
                    col_coord += col_width_total

                screen.print_at(row_item, col_coord, row)
                col_width_away_total += valid_list_width[valid_index]

                valid_index = valid_index + 1
            col_index = col_index + 1
        row = row + 1

    col_width_away_total += 1
    return col_width_away_total


def DrawScoreDetailsWholePageCore(screen, game, details_table, col_width_list,
                                  start_row, start_col=0):
    col_width_away_total = DrawOneGameDetailsCore(
                        screen, details_table['away_player_details'],
                        col_width_list, 0, start_row, start_col)

    DrawOneGameDetailsCore(
        screen, details_table['home_player_details'],
        col_width_list, col_width_away_total,
        start_row, start_col)

    DrawScoresInDetailsPage(screen, game, col_width_away_total, 0)

    DrawScoreInSection(screen, details_table['away_section_scores'],
                       int(col_width_away_total / 2),
                       0)
    DrawScoreInSection(screen, details_table['home_section_scores'],
                       int(col_width_away_total * 3 / 2),
                       0)
    return


def DrawOneGameDetailsFullMode(screen, game, details_table,
                               start_row, start_col=0):
    col_len = len(details_table['away_player_details'][0])
    if col_len == 0:
        return
    col_width_list = [18, 0, 5]
    for i in range(len(col_width_list), col_len):
        col_width_list.append(5)

    DrawScoreDetailsWholePageCore(screen, game, details_table,
                                  col_width_list, start_row, start_col)
    return


def DrawOneGameDetailsSimpleMode(screen, game, details_table,
                                 start_row, start_col=0):
    col_len = len(details_table['away_player_details'][0])
    if col_len == 0:
        return
    col_width_list = [18, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(col_width_list), col_len):
        col_width_list.append(5)

    DrawScoreDetailsWholePageCore(screen, game, details_table,
                                  col_width_list, start_row, start_col)

    return


def DrawOneGameDetails(screen, game, details_table, start_row, start_col=0):
    row_index = start_row + 6
    col_index = start_col
    if screen.width > 190:
        DrawOneGameDetailsFullMode(
            screen, game, details_table, row_index, col_index)
    else:
        DrawOneGameDetailsSimpleMode(
            screen, game, details_table, row_index, col_index)

    screen.refresh()
    return


def DrawOneGames(screen, game, row, col):
    screen.print_at(str(game.index), int(25 / 2) + col, row)
    row = row + 1

    team_vs_names = '      {0} vs {1}'.format(game.teamA.name, game.teamB.name)
    screen.print_at(team_vs_names, col, row)
    row = row + 1

    team_vs_scores = '      {0}  vs  {1}'.format(
        game.teamA.score, game.teamB.score)
    prefix_blank = '      '
    str_versus = '  vs  '
    screen.print_at(prefix_blank, col, row)

    if int(game.teamA.score) > int(game.teamB.score):
        screen.print_at(game.teamA.score, col + len(prefix_blank), row,
                        colour=screen.COLOUR_GREEN)
        col_len = len(prefix_blank) + len(game.teamA.score)
        str_tmp = '{0}{1}'.format(str_versus, game.teamB.score)
        screen.print_at(str_tmp, col + col_len, row)
    elif int(game.teamA.score) < int(game.teamB.score):
        str_tmp = '{0}{1}'.format(game.teamA.score, str_versus)
        screen.print_at(str_tmp, col + len(prefix_blank), row)
        col_len = len(prefix_blank) + len(str_tmp)
        screen.print_at(game.teamB.score, col + col_len, row,
                        colour=screen.COLOUR_GREEN)
    else:
        screen.print_at(team_vs_scores, col, row)
    row = row + 1

    team_vs_time = '   {0}'.format(game.time.strip())
    screen.print_at(team_vs_time, col, row)
    row = row + 1

    screen.refresh()
    return


def GoLive(screen):
    all_games_finished = False
    one_game_finished = False
    all_game_lists = GetAllGamesList()
    num_of_games = len(GetAllGames(all_game_lists, all_games_finished))
    progress_count = 0
    one_game_details_table = []
    instructions = '请输入查看的场次: '
    copy_right = '本工具所有数据都来自于虎扑(https://www.hupu.com/)'

    is_detail = False
    choice = ''

    while True:
        if not all_games_finished:
            all_game_lists = GetAllGamesList()
        games = GetAllGames(all_game_lists, all_games_finished)
        all_games_finished = CheckAllGamesOver(games)

        if not is_detail:
            if not all_games_finished:
                ClearScreen(screen)
            one_game_finished = False
            row_number = int(num_of_games / 3) + 1
            if num_of_games % 3 == 0:
                row_number = row_number - 1
            DrawBoard(screen, row_number, 3, line_height)
            row = 0
            col = 0

            for game in games:
                DrawOneGames(screen, game, row * line_height + 1, col * 25 + 1)
                col = (col + 1) % 3
                if col == 0:
                    row = row + 1

            progress = '*' * progress_count
            progress_count = (progress_count + 1) % 10
            screen.print_at(progress, 0, (row + 1) * line_height + 5)

            ev = screen.get_key()

            if ev in range(ord('a'), ord('a') + num_of_games):
                is_detail = True
                choice = chr(ev)

            screen.print_at(
                instructions + choice, 0, (row + 1) * line_height + 3)

            screen.print_at(
                copy_right, 0, screen.height - 1)

            screen.refresh()
            if not all_games_finished:
                time.sleep(3)
            else:
                time.sleep(1)
        else:
            if not one_game_finished:
                ClearScreen(screen)
                one_game_details_table = GetOneGameDetails(
                    all_game_lists, choice.upper())

            if len(one_game_details_table) != 0:
                if '已结束' in games[ord(choice) - ord('a')].time:
                    one_game_finished = True
                DrawOneGameDetails(
                    screen, games[ord(choice) - ord('a')],
                    one_game_details_table, 0)
            else:
                screen.print_at('比赛未开始', 0, 0)

            ev = screen.get_key()
            if ev in (ord('Q'), ord('q')):
                is_detail = False
                choice = ''
                ClearScreen(screen)

            screen.print_at('按q返回上层界面: ', 0, screen.height - 1)
            screen.refresh()
            if not one_game_finished:
                time.sleep(5)
            else:
                time.sleep(1)

    return


if __name__ == '__main__':
    Screen.wrapper(GoLive)
