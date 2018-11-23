# -*- coding: utf-8 -*-
import hiredis
import re
from datetime import datetime, timedelta
from selection import XpathSelector
from weblib.html import strip_tags
from lxml.html import fromstring


def html_to_string(html):
    doc = XpathSelector(fromstring(html))
    return doc.text()


def html_to_list(html):
    return [s.strip() for s in strip_tags(html, normalize_space=False,
                                          convert_br=True).split('\n')]


time_rex = re.compile(
    '(:?(?P<d>\d+) days?)?\s*(:?(?P<h>\d+) hours?)?\s*(:?(?P<m>\d+) minutes?)?\s*(:?(?P<s>\d+) seconds?)?')


def string_to_seconds(s):
    res = time_rex.search(s).groupdict()
    days = int(res.get('d') or 0)
    hours = int(res['h'] or 0)
    minutes = int(res['m'] or 0)
    seconds = int(res['s'] or 0)
    td = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return td


def parse_rigstat_online(html):
    doc = XpathSelector(fromstring(html))
    data = dict()
    data['timestamp'] = datetime.now()
    data['rigs'] = []
    data['title'] = doc.select('//title').text()
    for row in doc.select('//table[contains(@class, "table-sm")]/tbody/tr'):
        ethos_version = row.select('.//td[2]/span[1]').text()
        driver = html_to_string(row.select('.//td[2]/span[2]').attr('title'))
        driver = driver.split()[-1]
        miner_raw = html_to_string(row.select('.//td[2]/span[3]').attr('title')).split()
        if len(miner_raw) == 3:
            miner = miner_raw[1]
            miner_version = miner_raw[2]
        else:
            miner = miner_raw[1]
            miner_version = ''
        gpus_cell = row.select('.//td[3]')
        gpus_ok, gpus_total = gpus_cell.text().split('/')
        gpu_list = html_to_list(gpus_cell.select('./span').attr('title'))
        name = row.select('.//td[4]').text()
        rig_info = strip_tags(row.select('.//td[4]/a').attr('title'), normalize_space=False,
                              convert_br=True).strip()
        ip = row.select('.//td[6]/a').attr('href').replace('http://', '')
        last_report = strip_tags(row.select('.//td[7]/span').attr('title'))
        uptime = strip_tags(row.select('.//td[8]/span').attr('title'))
        miner_uptime = strip_tags(row.select('.//td[9]/span').attr('title'))
        hashes = strip_tags(row.select('.//td[11]/span').attr('title')).split()
        hashes = [float(s) for s in hashes]
        temps = [int(s) for s in row.select('.//td[12]').text().split()]
        power_tune = [int(s) for s in row.select('.//td[13]').text().split()]
        try:
            volts = [float(s) for s in row.select('.//td[14]').text().split()]
        except ValueError:
            volts = ()
        wattage = [int(s) for s in row.select('.//td[15]').text().split()]
        fans = [int(s) for s in row.select('.//td[16]').text().split()]
        clocks_core = [float(s) for s in row.select('.//td[17]').text().split()]
        clocks_mem = [float(s) for s in row.select('.//td[18]').text().split()]
        rig = dict(ethos_version=ethos_version, miner=miner, miner_version=miner_version,
                   driver=driver, gpus_ok=gpus_ok, gpus_total=gpus_total, gpu_list=gpu_list,
                   name=name, rig_info=rig_info, ip=ip,  hashes=hashes, hashes_total=sum(hashes),
                   last_report=last_report, uptime=uptime, miner_uptime=miner_uptime,
                   last_report_seconds=string_to_seconds(last_report).total_seconds(),
                   uptime_seconds=string_to_seconds(uptime).total_seconds(),
                   miner_uptime_seconds=string_to_seconds(miner_uptime).total_seconds(),
                   temps=temps, power_tune=power_tune, volts=volts, wattage=wattage,
                   fans=fans, clocks_core=clocks_core, clocks_mem=clocks_mem)
        data['rigs'].append(rig)
    return data
