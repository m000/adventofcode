#!/usr/bin/env python3
import re
import sys
import datetime
from pprint import pprint
INPUT = 'd04-input.txt'

line_re = re.compile(r'\[(?P<ts>[^x]+)\] (.* #(?P<id>\d+) )?.*(?P<action>(wakes|asleep|begins))')
time_fmt = '%Y-%m-%d %H:%M'

# ------------------------------------------------

events = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.search(line.strip())
        if m is None:
            print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
            sys.exit(1)
        e = m.groupdict()
        e['id'] = int(e['id']) if e['id'] is not None else None
        e['ts'] = datetime.datetime.strptime(e['ts'], time_fmt)
        assert(e['id'] is None or e['action'] == 'begins')
        events.append(e)
events.sort(key = lambda e: e['ts'])

# ------------------------------------------------

guards = {}
dt = datetime.timedelta(minutes=1)
for e in events:
        if e['action'] == 'begins':
            guard_id = e['id']
            if guard_id not in guards:
                guards[guard_id] = 60 * [0,]
        elif e['action'] == 'asleep':
            asleep_ts = e['ts']
            asleep_id = guard_id
        elif e['action'] == 'wakes':
            wake_ts = e['ts']
            assert(asleep_id == guard_id)
            assert(wake_ts > asleep_ts)
            while asleep_ts < wake_ts:
                guards[guard_id][asleep_ts.minute] += 1
                asleep_ts += dt

# ------------------------------------------------

# part 1
sleepy_guard_id = max(guards, key=lambda key: sum(guards[key]))
sleepy_guard_minute = max(enumerate(guards[sleepy_guard_id]), key=lambda it: it[1])
print('%d * %d = %d' % (sleepy_guard_id, sleepy_guard_minute[0], sleepy_guard_id*sleepy_guard_minute[0]))

# ------------------------------------------------

# part 2
sleepiest_minutes = { k: max(enumerate(v), key=lambda it: it[1])[0] for k, v in guards.items() }
consistently_sleepy_guard_id = max(sleepiest_minutes, key=lambda key: guards[key])
print('%d * %d = %d' % (
    consistently_sleepy_guard_id,
    sleepiest_minutes[consistently_sleepy_guard_id],
    consistently_sleepy_guard_id * sleepiest_minutes[consistently_sleepy_guard_id]
))

# vim:sts=4:sw=4:et:
