#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Gammu <http://wammu.eu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
python-gammu - Test script to test several Gammu operations
(usually using dummy driver, but it depends on config)
'''

from __future__ import print_function
import gammu
import sys
if len(sys.argv) != 2:
    print('This requires one parameter with location of config file!')
    sys.exit(1)

state_machine = gammu.StateMachine()
state_machine.ReadConfig(Filename=sys.argv[1])
state_machine.Init()


def GetAllMemory(memory_type):
    status = state_machine.GetMemoryStatus(Type=memory_type)

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextMemory(Start=True, Type=memory_type)
            start = False
        else:
            entry = state_machine.GetNextMemory(
                Location=entry['Location'], Type=memory_type
            )
        remain = remain - 1

        print()
        print(('%-15s: %d' % ('Location', entry['Location'])))
        for v in entry['Entries']:
            if v['Type'] in ('Photo'):
                print(('%-15s: %s...' % (v['Type'], repr(v['Value'])[:30])))
            else:
                print((
                    '%-15s: %s' % (v['Type'], str(v['Value']).encode('utf-8'))
                ))


def GetAllCalendar():
    status = state_machine.GetCalendarStatus()

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextCalendar(Start=True)
            start = False
        else:
            entry = state_machine.GetNextCalendar(Location=entry['Location'])
        remain = remain - 1

        print()
        print(('%-20s: %d' % ('Location', entry['Location'])))
        print(('%-20s: %s' % ('Type', entry['Type'])))
        for v in entry['Entries']:
            print(('%-20s: %s' % (v['Type'], str(v['Value']).encode('utf-8'))))


def Battery():
    status = state_machine.GetBatteryCharge()

    for x in status:
        if status[x] != -1:
            print(("%20s: %s" % (x, status[x])))


def GetAllSMS():
    status = state_machine.GetSMSStatus()

    remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    start = True

    while remain > 0:
        if start:
            sms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            sms = state_machine.GetNextSMS(
                Location=sms[0]['Location'], Folder=0
            )
        remain = remain - len(sms)

    return sms


def PrintSMSHeader(message, folders):
    print()
    print('%-15s: %s' % ('Number', message['Number'].encode('utf-8')))
    print('%-15s: %s' % ('Date', str(message['DateTime'])))
    print('%-15s: %s' % ('State', message['State']))
    print('%-15s: %s %s (%d)' % (
        'Folder',
        folders[message['Folder']]['Name'].encode('utf-8'),
        folders[message['Folder']]['Memory'].encode('utf-8'),
        message['Folder']
    ))
    print('%-15s: %s' % ('Validity', message['SMSC']['Validity']))


def PrintAllSMS(sms, folders):
    for m in sms:
        PrintSMSHeader(m, folders)
        print('\n%s' % m['Text'].encode('utf-8'))


def LinkAllSMS(sms, folders):
    data = gammu.LinkSMS([[msg] for msg in sms])

    for x in data:
        v = gammu.DecodeSMS(x)

        m = x[0]
        PrintSMSHeader(m, folders)
        loc = []
        for m in x:
            loc.append(str(m['Location']))
        print('%-15s: %s' % ('Location(s)', ', '.join(loc)))
        if v is None:
            print('\n%s' % m['Text'].encode('utf-8'))
        else:
            for e in v['Entries']:
                print()
                print('%-15s: %s' % ('Type', e['ID']))
                if e['Bitmap'] is not None:
                    for bmp in e['Bitmap']:
                        print('Bitmap:')
                        for row in bmp['XPM'][3:]:
                            print(row)
                    print()
                if e['Buffer'] is not None:
                    print('Text:')
                    print(e['Buffer'].encode('utf-8'))
                    print()


def GetAllTodo():
    status = state_machine.GetToDoStatus()

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextToDo(Start=True)
            start = False
        else:
            entry = state_machine.GetNextToDo(Location=entry['Location'])
        remain = remain - 1

        print()
        print('%-15s: %d' % ('Location', entry['Location']))
        print('%-15s: %s' % ('Priority', entry['Priority']))
        for v in entry['Entries']:
            print('%-15s: %s' % (v['Type'], str(v['Value']).encode('utf-8')))


def GetSMSFolders():
    folders = state_machine.GetSMSFolders()
    for i, folder in enumerate(folders):
        print('Folder %d: %s (%s)' % (
            i,
            folder['Name'].encode('utf-8'),
            folder['Memory'].encode('utf-8')
        ))
    return folders


def DateTime():
    dt = state_machine.GetDateTime()
    print(dt)
    state_machine.SetDateTime(dt)
    return dt


if __name__ == '__main__':
    smsfolders = GetSMSFolders()
    GetAllMemory('ME')
    GetAllMemory('SM')
    GetAllMemory('MC')
    GetAllMemory('RC')
    GetAllMemory('DC')
    Battery()
    GetAllCalendar()
    GetAllTodo()
    smslist = GetAllSMS()
    PrintAllSMS(smslist, smsfolders)
    LinkAllSMS(smslist, smsfolders)
    DateTime()