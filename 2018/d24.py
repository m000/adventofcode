#!/usr/bin/env python3
import sys
import re
import copy
from pprint import pprint

INPUTS = ['d24-input.txt', 'd24-input-example.txt', 'd24-input-test.txt']
DEBUG = False
INPUT = INPUTS[2] if DEBUG else INPUTS[0]

section_re = re.compile('([\w\s]+):')
units_re = re.compile(r'(?P<count>\d+) units .* (?P<hp>\d+) hit points( \((?P<resistances>[\w\s,;]+)\))?.* does (?P<dmg>\d+) (?P<dmg_type>\w+) damage .* initiative (?P<initiative>\d+)')

# ------------------------------------------------
# classes modelling the game
# ------------------------------------------------
class Unit:
    def __init__(self, m):
        self.hp = int(m['hp'])
        self.dmg = int(m['dmg'])
        self.dmg_type = m['dmg_type']
        self.initiative = int(m['initiative'])
        self.weak = []
        self.immune = []

        if m['resistances'] is not None:
            for res in m['resistances'].split(';'):
                res_level, _, res_type = res.partition(' to ')
                res_level = getattr(self, res_level.strip())
                res_level.extend(map(str.strip, res_type.split(',')))

    def __repr__(self):
        wk = ' weak%s' % self.weak if self.weak else ''
        im = ' immune%s' % self.immune if self.immune else ''
        return '<hp[%d] dmg[%d:%s] init[%d]%s%s>' % (
                    self.hp, self.dmg, self.dmg_type,
                    self.initiative, wk, im
                )

    def __str__(self):
        wk = ' weak:%s' % self.weak if self.weak else ''
        im = ' immune:%s' % self.immune if self.immune else ''
        return 'hp[%d] dmg[%d:%s] init[%d]%s%s' % (
                    self.hp, self.dmg, self.dmg_type,
                    self.initiative, wk, im
                )

class Group:
    def __init__(self, u, count):
        self.u = u
        self.count = count
        self.army = None
        self.n = -1
        self.damage = 0

    def __str__(self):
        return '%d - %4dx<%s>' % (self.effective_power, self.count, self.u)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        if self.effective_power != other.effective_power:
            return self.effective_power < other.effective_power
        if self.u.initiative != other.u.initiative:
            return self.u.initiative < other.u.initiative

    def effective_damage(self, other):
        if self.u.dmg_type in other.u.immune:
            return 0
        elif self.u.dmg_type in other.u.weak:
            return 2*self.effective_power
        else:
            return self.effective_power

    def select_target(self, oppgroups):
        if not oppgroups:
            return None
        else:
            damage = [(i, (self.effective_damage(g), g.effective_power, g.u.initiative))
                for i, g in enumerate(oppgroups)]
            damage.sort(key=lambda t: t[1])
            idx, selection = damage.pop()
            if selection[0] > 0:
                return oppgroups.pop(idx)
            else:
                return None

    def attack(self, defender):
        defender.damage = self.effective_damage(defender)
        defender.killed = min(defender.count, defender.damage // defender.u.hp)
        defender.count -= defender.killed

    @property
    def effective_power(self):
        return self.count * (self.u.dmg + self.army.boost)

class Army:
    def __init__(self, name):
        self.name = name
        self.groups = []
        self.selections = []
        self.next_group_n = 1
        self.boost = 0

    def __str__(self):
        return '%s Army [%d groups, %d units, %d power, %d boost]:\n\t%s' % (
                self.name, len(self.groups), self.units,
                sum([g.effective_power for g in self.groups]), self.boost,
                "\n\t".join(['%02d. %s' % (g.n, g) for g in self.groups]))

    def __repr__(self):
        return str(self)

    def add_group(self, g):
        g.army = self
        g.n = self.next_group_n
        self.groups.append(g)
        self.next_group_n += 1

    def select_targets(self, oparmy):
        mygroups = sorted(self.groups, reverse=True)
        opgroups = oparmy.groups.copy()
        self.selections = [(g, g.select_target(opgroups)) for g in mygroups]

    def remove_dead(self):
        for g in self.groups:
            g.damage = 0
            g.killed = 0
        self.groups = [g for g in self.groups if g.count > 0]

    @property
    def units(self):
        return sum([g.count for g in self.groups])

    @property
    def defeated(self):
        return not self.groups

    @classmethod
    def remove_dead_all(self, armies):
        for a in armies:
            a.remove_dead()

    @classmethod
    def print_all(self, armies):
        for a in armies:
            print(a)

    @classmethod
    def attack_all(self, armies):
        attacks = []
        killed = {}
        eliminated = {}

        for a in armies:
            killed[a.name] = 0
            eliminated[a.name] = []
            for attacker, defender in a.selections:
                attacks.append((attacker.u.initiative, attacker, defender))

        if DEBUG:
            print('')
        attacks.sort(reverse=True)
        for initiative, attacker, defender in attacks:
            if defender is None: continue
            attacker.attack(defender)
            killed[defender.army.name] += defender.killed
            if not defender.count > 0:
                eliminated[defender.army.name].append(defender.n)
            if DEBUG:
                print('%s[%02d] -> %s[%02d] (%d damage, %d killed)' % (
                    attacker.army.name, attacker.n, defender.army.name, defender.n,
                    defender.damage, defender.killed))

        if DEBUG:
            print('')
            for a in killed:
                print('%s: %d killed, eliminated %s' % (
                    a, killed[a], eliminated[a]))

    @classmethod
    def battle(self, armies):
        assert(len(armies) == 2)
        battle_round = 0
        while not (armies[0].defeated or armies[1].defeated):
            if DEBUG:
                print(70*'-')
                print('Round %d' % (battle_round))
                Army.print_all(armies)
            armies[0].select_targets(armies[1])
            armies[1].select_targets(armies[0])
            Army.attack_all(armies)
            Army.remove_dead_all(armies)
            if DEBUG:
                print('')
            battle_round += 1
        Army.print_all(armies)

# ------------------------------------------------
# part 2
# ------------------------------------------------
with open(INPUT) as f:
    armies_init = []
    for ln, l in enumerate(f):
        m = section_re.match(l)
        if m is not None:
            armies_init.append(Army(m.group(1)))
            continue

        # note: resistances in units_re is OPTIONAL
        m = units_re.match(l)
        if m is not None:
            u = Unit(m)
            armies_init[-1].add_group(Group(u, int(m['count'])))
            continue

        print('Skipped line %d: %s' % (ln, l.strip()), file=sys.stderr)

# ------------------------------------------------
# part 1
# ------------------------------------------------
# make a single run
armies = copy.deepcopy(armies_init)
Army.battle(armies)

# ------------------------------------------------
# part 2
# ------------------------------------------------
# we use binary search to make the program run a tad faster
# the required information are printed in the last iteration
boosted = 0
boost_range = [0, 10000]
assert('Immune' in armies_init[boosted].name)
while boost_range[0] + 1 != boost_range[1]:
    print(70*'-')
    armies = copy.deepcopy(armies_init)
    m = boost_range[0] + (boost_range[1] - boost_range[0]) // 2
    armies[boosted].boost = m

    Army.battle(armies)
    if DEBUG:
        outcome = 'lost' if armies[boosted].defeated else 'won'
        print(boost_range, armies[boosted].boost, outcome)

    if armies[boosted].defeated:
        boost_range[0] = m
    else:
        boost_range[1] = m

# vim:sts=4:sw=4:et:

