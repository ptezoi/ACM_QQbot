import re
import json
import time
import urllib3

from web_operation.operation import *
from oj_api.contest import Contest


def get_con(url):
    headers = {  # 定义请求头字典
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    }
    http_ = urllib3.PoolManager()
    res = http_.request('GET', url, headers=headers)
    return res.data.decode()


class ATC(Contest):
    async def get_contest(self):
        with open('./oj_json/contests.json', 'r', encoding='utf-8') as f:
            contest_data = json.load(f)
        contest_list = []
        if contest_data:
            for contest in contest_data:
                if contest['source'] == 'AtCoder':
                    contest['contestName'] = contest['name']
                    start_time = int(time.mktime(time.strptime(
                        contest['start_time'], "%Y-%m-%dT%H:%M:%S+00:00"))) + 8 * 3600
                    contest['startTime'] = start_time
                    end_time = int(time.mktime(time.strptime(
                        contest['end_time'], "%Y-%m-%dT%H:%M:%S+00:00"))) + 8 * 3600
                    contest['endTime'] = end_time
                    durationSeconds = contest['endTime'] - contest['startTime']
                    if durationSeconds <= 18000 and contest['startTime'] >= int(time.time()):
                        contest_list.append([contest, durationSeconds])
        return contest_list

    async def get_contest_info(self):
        contest_list = await self.get_contest()
        contest_len = len(contest_list)
        if contest_len == 0:
            return "最近没有比赛~"
        if contest_len > 3:
            contest_len = 3
        res = '找到最近的 {} 场ATC比赛为：\n'.format(contest_len)
        for i in range(contest_len):
            next_contest, durationSeconds = contest_list[i][0], contest_list[i][1]
            res += await self.format_atc_contest(next_contest, durationSeconds)
        return res.rstrip('\n')

    async def get_next_contest(self):
        contest_list = await self.get_contest()
        if not contest_list:
            return "最近没有比赛~", 32536700000, 0
        next_contest, durationSeconds = contest_list[0][0], contest_list[0][1]
        res = await self.format_atc_contest(next_contest, durationSeconds)
        return res.rstrip('\n'), int(next_contest['startTime']), durationSeconds

    async def get_recent_info(self):
        recent, _, _ = await self.get_next_contest()
        return "ATC比赛还有15分钟就开始啦，没有报名的尽快报名~\n" + recent

    async def format_atc_contest(self, next_contest, durationSeconds):
        res = "比赛名称：{}\n" \
              "开始时间：{}\n" \
              "持续时间：{}\n" \
              "比赛地址：{}\n".format(
            next_contest['contestName'],
            time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(int(next_contest['startTime']))),
            "{}小时{:02d}分钟".format(
                durationSeconds // 3600, durationSeconds % 3600 // 60),
            next_contest['link']
        )
        return res

    async def get_rating(self, name):
        url = "https://atcoder.jp/users/" + name
        html = await get_html(url)
        r = r'<th class="no-break">Rating<\/th><td><span class=(.*?)>(.*?)<\/span>'
        results = re.findall(r, html, re.S)
        try:
            return results[0][1]
        except:
            return -1

    async def update_local_contest(self):
        url1 = "https://atcoder.jp/contests/"
        q = get_con(url1)
        par = r"<a href=(.*?)</a>"
        pos1 = q.find("Upcoming Contests")
        pos2 = q.find("Recent Contests")
        txt = q[pos1: pos2]
        txt2 = re.findall(par, txt)
        atc_json = [
            {
                "source": "AtCoder",
                "name": "",
                "link": "",
                "contest_id": "",
                "start_time": "",
                "end_time": "",
                "hash": ""
            },
            {
                "source": "AtCoder",
                "name": "",
                "link": "",
                "contest_id": "",
                "start_time": "",
                "end_time": "",
                "hash": ""
            },
            {
                "source": "AtCoder",
                "name": "",
                "link": "",
                "contest_id": "",
                "start_time": "",
                "end_time": "",
                "hash": ""
            }
        ]
        for i in range(5):
            if i % 2 == 0:
                con_url = "https://atcoder.jp/contests/" + re.findall(r"/contests/(.*)", txt2[i + 1])[0][0: 6]
                name = (re.findall(r"/contests/(.*)", txt2[i + 1])[0])[
                       8: len((re.findall(r"/contests/(.*)", txt2[i + 1])[0]))]
                t_id = (re.findall(r"/contests/(.*)", txt2[i + 1])[0])[0: 6]
                st = re.findall(r"var startTime = moment(.*;)", get_con(con_url))
                ed = re.findall(r"var endTime = moment(.*;)", get_con(con_url))
                hash = f"fby_ak_ioi%%%tql{i}"
                atc_json[i // 2]["name"] = name
                atc_json[i // 2]["link"] = con_url
                atc_json[i // 2]["contest_id"] = t_id
                atc_json[i // 2]["start_time"] = st[0][2: len(st[0]) - 3]
                atc_json[i // 2]["end_time"] = ed[0][2: len(ed[0]) - 3]
                atc_json[i // 2]["hash"] = hash
                with open('./oj_json/contests.json', "w") as f:
                    json.dump(atc_json, f, indent=4)
        return True


if __name__ == '__main__':
    name = "guke"
