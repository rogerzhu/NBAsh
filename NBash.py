from asciimatics.effects import Effect
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.event import KeyboardEvent
import sys
from models.Team import Team
from models.Game import Game
# from Player import Player
import requests
from bs4 import BeautifulSoup
from utilities.helpers import get_header, GetElementsByClass, ClearScreen
from utilities.helpers import GetOneElementByClass, GetTextOfItem

base_url = 'https://nba.hupu.com/games'
line_height = 5
choice = ''
all_game_lists = None
games = None


class AllGameView(Effect):
    def __init__(self, screen, **kwargs):
        super(AllGameView, self).__init__(screen, **kwargs)
        global all_game_lists
        global games
        all_game_lists = self._GetAllGamesList()
        games = self._GetAllGames(all_game_lists)
        self._num_of_games = len(games)
        self._all_games_finished = False

    def process_event(self, event):
        global choice
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key in range(ord('a'), ord('a') + self._num_of_games) or\
               key in range(ord('A'), ord('A') + self._num_of_games):
                choice = chr(key)
            return event
        else:
            return event

    def reset(self):
        ClearScreen(self._screen)
        self._all_games_finished = False
        return

    def _update(self, frame_no):
        global games
        if (frame_no - 1) % 60 == 0:
            if self._all_games_finished is False:
                ClearScreen(self._screen)
                all_game_lists = self._GetAllGamesList()
                games = self._GetAllGames(all_game_lists)
                self._all_games_finished = self._CheckAllGamesOver()
            else:
                pass
            self._GoLive(int(frame_no / 60) + 1)
        return

    @property
    def stop_frame(self):
        return self._stop_frame

    def _GoLive(self, progress_count):
        global choice
        instructions = '请输入查看的场次: '
        copy_right = '本工具所有数据都来自于虎扑(https://www.hupu.com/)'

        row_number = int(self._num_of_games / 3) + 1
        if self._num_of_games % 3 == 0:
            row_number = row_number - 1
        self._DrawBoard(row_number, 3)
        row = 0
        col = 0

        for game in games:
            self._DrawOneGame(game, row * line_height + 1, col * 25 + 1)
            col = (col + 1) % 3
            if col == 0:
                row = row + 1

        if progress_count % 2 == 0:
            self._screen.print_at('*********', 0, (row + 1) * line_height + 5)
        else:
            self._screen.print_at('         ', 0, (row + 1) * line_height + 5)
        self._screen.print_at(
            instructions + str(choice), 0, (row + 1) * line_height + 3)

        self._screen.print_at(
            copy_right, 0, self._screen.height - 1)

    def _DrawBoard(self, row, col=3, line_height=5, line_width=25):
        for i in range(0, row + 1):
            self._screen.move(0, i * line_height)
            self._screen.draw(line_width * col, i * line_height, char='-')

        for i in range(0, col + 1):
            self._screen.move(i * line_width, 0)
            self._screen.draw(i * line_width, line_height * row + 1, char='|')

        return

    def _GetAllGamesList(self):
        headers = {"User-Agent": get_header()}
        base_r = requests.get(url=base_url, headers=headers)
        base_content = BeautifulSoup(base_r.content, features='html.parser')

        all_game_lists = base_content.find_all('div', {'class': 'list_box'})

        return all_game_lists

    def _GetAllGames(self, all_game_lists):
        index = 'A'
        games_list = []
        for item in all_game_lists:
            team_vs = GetOneElementByClass(item, 'div', 'team_vs')
            team_details_div = GetElementsByClass(team_vs, 'div', 'txt')

            team_score_a = GetOneElementByClass(
                team_details_div[0], 'span', 'num')
            team_score_b = GetOneElementByClass(
                team_details_div[1], 'span', 'num')

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

    def _CheckAllGamesOver(self):
        keywords = '已结束'
        all_game_lists = games
        if all(keywords in item.time
               for item in all_game_lists if item.time is not None):
            return True
        else:
            return False

    def _DrawOneGame(self, game, row, col):
        self._screen.print_at(str(game.index), int(25 / 2) + col, row)
        row = row + 1

        team_vs_names = '      {0} vs {1}'.format(
            game.teamA.name, game.teamB.name)
        self._screen.print_at(team_vs_names, col, row)
        row = row + 1

        team_vs_scores = '      {0}  vs  {1}'.format(
            game.teamA.score, game.teamB.score)
        prefix_blank = '      '
        str_versus = '  vs  '
        self._screen.print_at(prefix_blank, col, row)

        if int(game.teamA.score) > int(game.teamB.score):
            self._screen.print_at(
                            game.teamA.score, col + len(prefix_blank), row,
                            colour=self._screen.COLOUR_GREEN)
            col_len = len(prefix_blank) + len(game.teamA.score)
            str_tmp = '{0}{1}'.format(str_versus, game.teamB.score)
            self._screen.print_at(str_tmp, col + col_len, row)
        elif int(game.teamA.score) < int(game.teamB.score):
            str_tmp = '{0}{1}'.format(game.teamA.score, str_versus)
            self._screen.print_at(str_tmp, col + len(prefix_blank), row)
            col_len = len(prefix_blank) + len(str_tmp)
            self._screen.print_at(game.teamB.score, col + col_len, row,
                                  colour=self._screen.COLOUR_GREEN)
        else:
            self._screen.print_at(team_vs_scores, col, row)
        row = row + 1

        team_vs_time = '   {0}'.format(game.time.strip())
        self._screen.print_at(team_vs_time, col, row)
        row = row + 1


class GameDetailsView(Effect):
    def __init__(self, screen, **kwargs):
        super(GameDetailsView, self).__init__(screen, **kwargs)
        self._one_game_finished = False

    def reset(self):
        self._one_game_finished = False
        pass

    def _update(self, frame_no):
        global choice
        global games
        if (frame_no - 1) % 60 == 0:
            if self._one_game_finished is False:
                ClearScreen(self._screen)
                one_game_details_table =\
                    self._GetOneGameDetails(choice.upper())
                if len(one_game_details_table) != 0:
                    if '结束' in games[ord(choice.upper()) - ord('A')].time:
                        self._one_game_finished = True
                    self._DrawOneGameDetails(
                        games[ord(choice.upper()) - ord('A')],
                        one_game_details_table, 0)
                else:
                    self._screen.print_at('比赛未开始', 0, 0)

    @property
    def stop_frame(self):
        pass

    def _GetOneGameDetails(self, str_index):
        global all_game_lists
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

        table_details_away = self._GetDetailTable(
            score_live_content_core_table_away)
        table_details_home = self._GetDetailTable(
            score_live_content_core_table_home)

        score_in_section_away, score_in_section_home = self._GetScoreInSection(
            score_live_content)

        table_details['away_player_details'] = table_details_away
        table_details['home_player_details'] = table_details_home
        table_details['away_section_scores'] = score_in_section_away
        table_details['home_section_scores'] = score_in_section_home

        return table_details

    def _GetScoreInSection(self, live_content):
        score_in_section_table = GetOneElementByClass(
            live_content, 'table', 'itinerary_table')
        score_in_section_away_table = GetOneElementByClass(
            score_in_section_table, 'tr', 'away_score')
        score_in_section_home_table = GetOneElementByClass(
            score_in_section_table, 'tr', 'home_score')

        section_counts = len(score_in_section_away_table.find_all('td')[1:-1])
        away_score_list = ['0' for n in range(section_counts)]
        home_score_list = ['0' for n in range(section_counts)]

        away_index = 0
        home_index = 0
        for item in score_in_section_away_table.find_all('td')[1:-1]:
            away_score_list[away_index] = item.get_text().strip()
            away_index += 1

        for item in score_in_section_home_table.find_all('td')[1:-1]:
            home_score_list[home_index] = item.get_text().strip()
            home_index += 1

        return away_score_list, home_score_list

    def _GetDetailTable(self, content_table):
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

    def _DrawScoresInDetailsPage(self, game,
                                 col_width_away_total, start_row):
        game_info_a = '{0}:{1}'.format(
            game.teamA.name, game.teamA.score)
        self._screen.print_at(
            game_info_a, int(col_width_away_total / 2), start_row)

        game_info_b = '{0}:{1}'.format(
            game.teamB.name, game.teamB.score)
        self._screen.print_at(
            game_info_b, int(col_width_away_total * 3 / 2), start_row)

        self._screen.print_at(
            game.time.strip(), col_width_away_total, start_row)

        return

    def _DrawScoreInSection(self, score_in_sections,
                            start_col_index, start_row):
        section_index = 1
        self._screen.print_at('节次', start_col_index - 5, start_row + 2)
        self._screen.print_at('比分', start_col_index - 5, start_row + 3)
        for item in score_in_sections:
            self._screen.print_at(
                str(section_index), start_col_index, start_row + 2)
            self._screen.print_at(item, start_col_index, start_row + 3)
            start_col_index += 3
            section_index += 1

        return

    def _DrawOneGameDetailsCore(self, table_items, width_list,
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
                                    (valid_index - 1) * \
                                    valid_list_width[valid_index] + 1
                    if col_width_total != 0:
                        col_coord += col_width_total

                    self._screen.print_at(row_item, col_coord, row)
                    col_width_away_total += valid_list_width[valid_index]

                    valid_index = valid_index + 1
                col_index = col_index + 1
            row = row + 1

        col_width_away_total += 1
        return col_width_away_total

    def _DrawOneGameDetailsFullMode(self, game, details_table,
                                    start_row, start_col=0):
        col_len = len(details_table['away_player_details'][0])
        if col_len == 0:
            return
        col_width_list = [18, 0, 5]
        for i in range(len(col_width_list), col_len):
            col_width_list.append(5)

        col_width_away_total = self._DrawOneGameDetailsCore(
                            details_table['away_player_details'],
                            col_width_list, 0, start_row, start_col)

        self._DrawOneGameDetailsCore(
            details_table['home_player_details'],
            col_width_list, col_width_away_total,
            start_row, start_col)

        self._DrawScoresInDetailsPage(game, col_width_away_total, 0)

        self._DrawScoreInSection(details_table['away_section_scores'],
                                 int(col_width_away_total / 2), 0)
        self._DrawScoreInSection(details_table['home_section_scores'],
                                 int(col_width_away_total * 3 / 2), 0)
        return

    def _DrawOneGameDetailsSimpleMode(self, game, details_table,
                                      start_row, start_col=0):
        col_len = len(details_table['away_player_details'][0])
        if col_len == 0:
            return
        col_width_list = [18, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(col_width_list), col_len):
            col_width_list.append(5)

        col_width_away_total = self._DrawOneGameDetailsCore(
                            details_table['away_player_details'],
                            col_width_list, 0, start_row, start_col)

        self._DrawOneGameDetailsCore(
            details_table['home_player_details'],
            col_width_list, col_width_away_total,
            start_row, start_col)

        self._DrawScoresInDetailsPage(game, col_width_away_total, 0)
        self._DrawScoreInSection(details_table['away_section_scores'],
                                 int(col_width_away_total / 2), 0)
        self._DrawScoreInSection(details_table['home_section_scores'],
                                 int(col_width_away_total * 3 / 2), 0)

        return

    def _DrawOneGameDetails(self, game, details_table, start_row, start_col=0):
        row_index = start_row + 6
        col_index = start_col
        if self._screen.width > 190:
            self._DrawOneGameDetailsFullMode(
                game, details_table, row_index, col_index)
        else:
            self._DrawOneGameDetailsSimpleMode(
                game, details_table, row_index, col_index)

        return


def demo(screen):
    scenes = []
    effects = [
        AllGameView(screen)
    ]
    scenes.append(Scene(effects, -1))

    effects = [
        GameDetailsView(screen)
    ]
    scenes.append(Scene(effects, -1))

    screen.play(scenes, stop_on_resize=True)


while True:
    try:
        Screen.wrapper(demo)
        sys.exit(0)
    except ResizeScreenError:
        pass
