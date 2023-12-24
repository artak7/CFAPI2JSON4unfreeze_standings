import requests, hashlib, json, random, time, codecs #, locale
# locale.setlocale(locale.LC_ALL, 'Russian')

formats = ['neoSaris', 'S4RIS']
methods = ['contest.status', 'contest.standings']

class CFAPI2JSON:
    def __init__(self, data):
        self.format = data['format']
        self.format_id = data['format_id']
        self.is_private = data['is_private'] == "true"
        self.group_code = data['group_code']
        self.contest_id = int(data['contest_id'])
        self.as_manager = data['as_manager']
        self.api_key = data['api_key']
        self.api_secret = data['api_secret']
        self.frozen_time = int(data['frozen_time'])

    def build_params(self, method):
        if not self.is_private:
            params_req = f'contestId={self.contest_id}'
            return params_req
        
        rand = str(random.randint(0, 999999) + 100000)
        current_time = str(int(time.time()))
        param = f''
        if method == "contest.status":
            param = f'&asManager={self.as_manager}'
        str_params = f'apiKey={self.api_key}{param}&contestId={self.contest_id}&groupCode={self.group_code}&time={current_time}'
        str_req  = f'{rand}/{method}?{str_params}#{self.api_secret}'
        hash = hashlib.sha512(str_req.encode()).hexdigest()
        api_sig = rand + hash
        params_req = f'{str_params}&apiSig={api_sig}'
        return params_req

    def get_data(self, method):
        url = 'https://codeforces.net/api/'
        params = self.build_params(method)
        str_sub = requests.get(f'{url}{method}?{params}').json()
        return str_sub

    def get_submissions(self, duration):
        method = 'contest.status'
        str_sub = self.get_and_write_codeforces_API_data(method)
        str_sub = sorted(list(str_sub['result']), key=lambda sub: sub['relativeTimeSeconds']) #not necessary
        map_sub = []
        # sub_team_names = set()
        for sub in str_sub:
            time_sub = sub['relativeTimeSeconds'] // 60
            if sub['author']['participantType'] == 'CONTESTANT' and not sub['author']['ghost'] and time_sub <= duration:
                team_name = sub['author']['members'][0].get('name') or f'NO_TEAM_NAME_'+sub['author']['members'][0].get('handle') or sub['author'].get('teamName')
                # sub_team_names.add(team_name)

                template = [
                    {
                        'timeSubmitted': time_sub, 
                        'contestantName': team_name,
                        'problemIndex': sub['problem']['index'],
                        'verdict': sub['verdict']
                    },
                    {
                        'contestant': team_name,
                        'problemLetter': sub['problem']['index'],
                        'timeMinutesFromStart': time_sub,
                        'success': sub['verdict'] == 'OK'
                    }
                ]
                map_sub.append(template[self.format_id])
        
        return map_sub #, sub_team_names

    def get_contest_data(self):
        method = 'contest.standings'
        str_data = self.get_and_write_codeforces_API_data(method)
        get_contestants_names_func = lambda row: row['party']['members'][0].get('name') or f'NO_TEAM_NAME_'+row['party']['members'][0].get('handle') or row['party'].get('teamName')
        duration = str_data['result']['contest']['durationSeconds'] // 60
        if self.format == 'neoSaris':
            problem_func = lambda problem: {'index': problem['index'], 'name': problem['name']}
            contestants_func = lambda row: {'id': row[0], 'name': row[1]}
        else:
            self.frozen_time = duration - self.frozen_time
            problem_func = lambda problem: problem['index']
            contestants_func = lambda row: row[1]

        contestants_names = set(map(get_contestants_names_func, str_data['result']['rows']))
        # contestants_names = sub_team_names.union(contestants_names)
        return {
            'contestData': {
                'duration': duration,
                'frozenTimeDuration': self.frozen_time,
                'name': str_data['result']['contest']['name'],
                'type': str_data['result']['contest']['type']
            },
            'problems': list(map(problem_func, str_data['result']['problems'])),
            'contestants': list(map(contestants_func, enumerate(contestants_names)))
        }

    def create_JSON(self):
        contest_data = self.get_contest_data()
        duration = contest_data['contestData']['duration']
        submissions = self.get_submissions(duration)
        
        if self.format == 'neoSaris':
            contest_data['contestData']['type'] = 'ICPC'
            neoSaris_JSONobject = {
                'contestMetadata': contest_data['contestData'],
                'problems': contest_data['problems'],
                'contestants': contest_data['contestants'],
                'verdicts': {
                    'accepted': ["OK", "PARTIAL"],
                    'wrongAnswerWithPenalty': [
                    "FAILED",
                    "RUNTIME_ERROR",
                    "WRONG_ANSWER",
                    "PRESENTATION_ERROR",
                    "TIME_LIMIT_EXCEEDED",
                    "MEMORY_LIMIT_EXCEEDED",
                    "IDLENESS_LIMIT_EXCEEDED",
                    "SECURITY_VIOLATED",
                    "CRASHED",
                    "INPUT_PREPARATION_CRASHED",
                    "CHALLENGED",
                    "REJECTED",
                    "SKIPPED",
                    ],
                    'wrongAnswerWithoutPenalty': ["COMPILATION_ERROR"],
                },
                'submissions': submissions
            }

            return neoSaris_JSONobject
        else:
            S4RIS_JSONobject = {
                'contestName': contest_data['contestData']['name'],
                'freezeTimeMinutesFromStart': contest_data['contestData']['frozenTimeDuration'],
                'problemLetters': contest_data['problems'],
                'contestants': contest_data['contestants'],
                'runs': submissions
            }
            return S4RIS_JSONobject

    def write(self, json_obj, file):
        json_str = json.dumps(json_obj, indent = 4, ensure_ascii=False)
        f = codecs.open(file, 'w', encoding='utf-16')
        f.write(json_str)
        f.close()

    def get_and_write_codeforces_API_data(self, method):
        json_obj = self.get_data(method)
        self.write(json_obj, 'CodeforcesAPI_'+method+'.json')
        return json_obj

def read_data(file):
    f = open(file, 'r')
    data = json.load(f)
    f.close()
    return data
    
# main
# init_data = {
#     "format": "S4RIS",
#     # "format": "neoSaris",
#     "is_private": "false",
#     "group_code": "",
#     "contest_id": "1900",
#     "as_manager": "true",
#     "api_key": "",
#     "api_secret": "",
#     # "all_time_duration": "300",
#     "frozen_time": "60"
# }

init_data = read_data('settings.txt')
init_data['format_id'] = formats.index(init_data['format'])
new_json = CFAPI2JSON(init_data)
json_obj = new_json.create_JSON()
new_json.write(json_obj, 'Olymp_'+init_data['format']+'_logs.json')