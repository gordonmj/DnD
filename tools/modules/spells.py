#! /usr/bin/env python3

import tkinter as tk
from math import sqrt
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import helpers as h
import GUIbasics as gui
import interface as iface
import tkUtility as util
import classes as c
import dice

longdescription = """{name}
{lvschool}
Casting time: {cast}
Range: {range}
Components: {comp}
Duration: {dur}
{desc}
"""


class LongEffectDisplay(gui.Section):
    def __init__(self, container, text):
        gui.Section.__init__(self, container)
        self.L = tk.Label(self.f, text=text, width=30, wraplength=200)
        self.draw_static()

    def draw_static(self):
        self.L.grid(row=0, column=0)

    def update(self, dummy, text):
        self.L['text'] = text


class NumberDisplay(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.values = []
        self.entries = []
        self.labels = []
        self.incs = []
        self.decs = []
        for i in range(1, len(character.max_spell_slots)):
            self.values.append(tk.StringVar())
            self.entries.append(tk.Entry(self.f,
                                         textvariable=self.values[i - 1],
                                         width=2))
            self.labels.append(tk.Label(self.f, text=i))
            self.incs.append(tk.Button(self.f, text='+',
                                       command=lambda x=i: self.change(x, 1)))
            self.decs.append(tk.Button(self.f, text='-',
                                       command=lambda x=i: self.change(x, -1)))
        self.rest = tk.Button(self.f, text='Long Rest', command=self.long_rest)
        ############
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        for i in range(len(self.character.spell_slots) - 1):
            self.labels[i].grid(row=i, column=0)
            self.entries[i].grid(row=i, column=1)
            self.incs[i].grid(row=i, column=2)
            self.decs[i].grid(row=i, column=3)
        self.rest.grid(row=len(self.character.spell_slots), column=4)

    def draw_dynamic(self):
        slots = self.character.spell_slots_get('*')[1:]
        for i, num in enumerate(slots):
            self.values[i].set(str(num))

    def long_rest(self):
        if (len(self.entries) < len(self.character.max_spell_slots)):
            self.draw_static()
        self.character.rest('long')
        self.draw_dynamic()

    def change(self, level, num):
        curr = self.character.spell_slots_get(level)
        self.character.spell_slots_set(level, curr + num)
        self.draw_dynamic()


class SpellDisplay(gui.Section):
    def __init__(self, container, handler, output, numbers):
        gui.Section.__init__(self, container, bd=2, relief='sunken')
        self.handler = handler
        self.output = output
        self.numbers = numbers
        #####
        levelnamemap = ['cantrip', '1st-level', '2nd-level', '3rd-level',
                        '4th-level', '5th-level', '6th-level', '7th-level',
                        '8th-level', '9th-level']
        self.namelevel = tk.Frame(self.f)
        self.nameL = tk.Label(self.namelevel, text=self.handler.name)
        args = (levelnamemap[self.handler.level], self.handler.school)
        lev = '{} {}'.format(*(reversed(args) if self.handler.level == 0
                               else args))
        self.leveltype = tk.Label(self.namelevel, text=lev)
        self.timeanddisplay = tk.Frame(self.f)
        bct = self.handler.casting_time
        ct = bct + (' (R: +10 minutes)' if self.handler.isritual else '')
        self.castingtime = tk.Label(self.timeanddisplay,
                                    text=ct)
        info = longdescription.format(name=self.handler.name,
                                      lvschool=lev,
                                      cast=self.handler.casting_time,
                                      range=self.handler.range,
                                      comp=self.handler.components,
                                      dur=self.handler.duration,
                                      desc=self.handler.effect)
        self.moreinfo = gui.InfoButton(self.timeanddisplay, info,
                                       title=self.handler.name)
        self.range = tk.Label(self.f, text=self.handler.range)
        d = self.handler.duration.capitalize() + (' (C)' if
                                                  self.handler.isconcentration
                                                  else '')
        self.duration = tk.Label(self.f, text=d)
        self.buttons = tk.Frame(self.f)
        self.CAST = tk.Button(self.buttons, text='Cast', command=self.cast)
        if (self.handler.isritual):
            self.RITUAL = tk.Button(self.buttons, text='Cast as Ritual',
                                    command=self.ritual_cast)
        ######
        self.draw_static()

    def __lt__(self, other):
        # Expects other to be a SpellDisplay, it's only used for sorting
        # return self.handler.level < other.handler.level
        return self.handler.level < other.handler.level

    def __str__(self):
        return str(self.handler)

    def draw_static(self):
        self.namelevel.grid(row=0, column=0)
        self.nameL.grid(row=0, column=0)
        self.leveltype.grid(row=0, column=1)
        #######
        self.timeanddisplay.grid(row=1, column=0)
        self.castingtime.grid(row=0, column=0)
        self.moreinfo.grid(row=0, column=1)
        #######
        self.range.grid(row=2, column=0)
        self.duration.grid(row=3, column=0)
        self.buttons.grid(row=4, column=0)
        self.CAST.grid(row=0, column=0)
        if (self.handler.isritual):
            self.RITUAL.grid(row=0, column=1)

    def cast(self):
        try:
            effect = self.handler.cast()
        except c.OutOfSpells as e:
            effect = str(e)
        self.output.update(h.shorten(effect), effect)
        self.numbers.draw_dynamic()

    def ritual_cast(self):
        effect = self.handler.ritual_cast()
        self.output.update(h.shorten(effect), effect)


class SpellSection(gui.Section):
    def __init__(self, container, jf, character, numbers, output):
        gui.Section.__init__(self, container, width=500, height=500)
        # self.thisf = tk.Frame(self.f, bg='green')
        self.character = character
        self.displays = {}
        self.numbers = numbers
        self.effects = output
        # self.numbers = NumberDisplay(self.f, self.character)
        self.handler = c.SpellsPrepared(jf, character)
        for obj in self.handler.objects():
            self.displays[obj.name] = SpellDisplay(self.f, obj, self.effects,
                                                   self.numbers)
        self.draw_static()
        self.draw_dynamic()

    def __iter__(self):
        return (display for display in self.displays)

    def draw_static(self):
        # self.thisf.grid(row=0, column=0)
        # self.numbers.grid(row=0, column=1)
        pass

    def draw_dynamic(self):
        s = int(sqrt(len(self.displays)))
        if (s):
            for (i, d) in enumerate(sorted(self.displays.values())):
                d.grid(row=i % s, column=i // s)
            i = len(self.displays)

    def prepare(self, name):
        success = self.handler.prepare(name)
        if (success):
            self.displays[name] = SpellDisplay(self.f, self.handler[name],
                                               self.effects, self.numbers)
            self.draw_dynamic()

    def unprepare(self, name):
        success = self.handler.unprepare(name)
        if (success):
            self.displays[name].f.destroy()
            del self.displays[name]
            self.draw_dynamic()

    def always_prepare(self, name):
        success = self.handler.prepare(name, True)
        if (success):
            self.displays[name] = SpellDisplay(self.f, self.handler[name],
                                               self.effects, self.numbers)
            self.draw_dynamic()
        else:
            print('Failed to prepare ' + name)


class module(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.numbers = NumberDisplay(self.f, character)
        self.numbers.rest.destroy()
        self.excessblock = tk.Frame(self.f)
        self.effects = LongEffectDisplay(self.excessblock, '')
        self.roll = dice.module(self.excessblock, character)
        self.detail = SpellSection(self.f, character.record, character,
                                   self.numbers, self.effects)
        self.prepare = tk.Button(self.excessblock, text='Prepare a spell',
                                 command=self.prepare_start)
        np = str(len(self.detail.handler.prepared_today))
        self.numprepared = tk.Label(self.excessblock,
                                    text='Spells prepared today: ' + np)
        self.unprepare = tk.Button(self.excessblock, text='Unprepare a spell',
                                   command=self.unprepare_start)
        self.permaprepare = tk.Button(self.excessblock,
                                      text='Permanently prepare a spell\n'
                                      '(CANNOT BE UNDONE WITHOUT\nMANUALLY '
                                      'EDITING THE FILE)',
                                      command=self.always_prepare_start)
        self.draw_static()

    def draw_static(self):
        self.detail.grid(row=0, column=0)
        self.excessblock.grid(row=0, column=1)
        self.effects.grid(row=0, column=0)
        self.roll.grid(row=1, column=0)
        self.prepare.grid(row=2, column=0)
        self.numprepared.grid(row=3, column=0)
        self.unprepare.grid(row=4, column=0)
        self.permaprepare.grid(row=5, column=0)
        self.numbers.grid(row=0, column=2)

    def draw_dynamic(self):
        self.numbers.draw_dynamic()

    def prepare_start(self):
        self.toprepare = {}
        gui.Query(self.toprepare, self.prepare_end, 'Spell to prepare?')

    def prepare_end(self):
        name = self.toprepare['Spell to prepare?']
        self.detail.prepare(name)
        np = str(len(self.detail.handler.prepared_today))
        self.numprepared.config(text='Spells prepared today: ' + np)

    def unprepare_start(self):
        self.tounprepare = {}
        p = [n for n in self.detail.handler.prepared_today]
        gui.Query(self.tounprepare, self.unprepare_end,
                  ['Spell to unprepare?', p])

    def unprepare_end(self):
        name = self.tounprepare['Spell to unprepare?']
        self.detail.unprepare(name)
        np = str(len(self.detail.handler.prepared_today))
        self.numprepared.config(text='Spells prepared today: ' + np)

    def always_prepare_start(self):
        self.toprepare = {}
        gui.Query(self.toprepare, self.always_prepare_end,
                  'Spell to always prepare?')

    def always_prepare_end(self):
        name = self.toprepare['Spell to always prepare?']
        self.detail.always_prepare(name)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        self.charactername = {}
        self.excessblock = tk.Frame(self.f)
        # self.effects = gui.EffectPane(self.f, '', '')
        self.effects = LongEffectDisplay(self.excessblock, '')
        self.roll = dice.DiceRoll(self.excessblock)
        self.prepare = tk.Button(self.excessblock, text='Prepare a spell',
                                 command=self.prepare_start)
        np = str(len(self.detail.handler.prepared_today))
        self.numprepared = tk.Label(self.excessblock,
                                    text='Spells prepared today: ' + np)
        self.unprepare = tk.Button(self.excessblock, text='Unprepare a spell',
                                   command=self.unprepare_start)
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.writequit,
                              fg='red')
        self.begin_start()

    def draw_static(self):
        self.handler.grid(row=0, column=0)
        # self.effects.grid(row=0, column=1)
        self.excessblock.grid(row=0, column=1)
        self.effects.grid(row=0, column=0)
        self.roll.grid(row=1, column=0)
        self.prepare.grid(row=2, column=0)
        self.numprepared.grid(row=3, column=0)
        self.unprepare.grid(row=4, column=0)
        self.numbers.grid(row=0, column=2)
        self.QUIT.grid(row=1, column=3)

    def begin_start(self):
        gui.Query(self.charactername, self.begin_end, 'Character name?')
        self.container.withdraw()

    def begin_end(self):
        name = self.charactername['Character name?']
        filename = 'character/{}.character'.format(h.clean(name))
        self.record = iface.JSONInterface(filename)
        self.character = c.Character(self.record)
        self.numbers = NumberDisplay(self.f, self.character)
        self.handler = SpellSection(self.f, self.record, self.character,
                                    self.numbers, self.effects)
        self.prepare = tk.Button(self.excessblock, text='Prepare a spell',
                                 command=self.detail.prepare_start)
        self.unprepare = tk.Button(self.excessblock, text='Unprepare a spell',
                                   command=self.detail.unprepare_start)
        self.container.deiconify()
        self.draw_static()

    def unprepare_start(self):
        self.tounprepare = {}
        gui.Query(self.tounprepare, self.unprepare_end, 'Spell to unprepare?')

    def unprepare_end(self):
        name = self.tounprepare['Spell to unprepare?']
        self.detail.unprepare(name)
        np = str(len(self.detail.handler.prepared_today))
        self.numprepared.config(text='Spells prepared today: ' + np)

    def writequit(self):
        self.character.write()
        self.container.destroy()


if (__name__ == '__main__'):
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
