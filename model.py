
import unicodedata
from functools import partial
from os.path import expanduser, join
from io import StringIO
from pkg_resources import resource_filename
from numpy import zeros
from panphon.featuretable import FeatureTable
from panphon.distance import Distance


class Vocabulary (object):

    def __init__ (self, iterable=None):
        self.table = dict()
        self.elements = []
        if iterable:
            for elt in iterable:
                self.intern(elt)

    def intern (self, elt):
        if elt in self.table:
            return self.table[elt]
        else:
            id = len(self.elements)
            self.elements.append(elt)
            self.table[elt] = id

    def string_to_id (self, elt):
        return self.table[elt]

    def id_to_string (self, id):
        return self.elements[id]

    def items (self):
        return enumerate(self.elements)

    def __iter__ (self):
        return iter(self.elements)


def debug_string (s):
    with StringIO() as out:
        out.write('<')
        for (i,c) in enumerate(s):
            if i > 0: out.write(' ')
            out.write(hex(ord(s[i])))
            out.write(' ')
            out.write(s[i])
        out.write('>')
        return out.getvalue()

def debug_phones (phones):
    with StringIO() as out:
        out.write('[')
        for (i,s) in enumerate(phones):
            if i > 0: out.write(' ')
            out.write(debug_string(s))
        out.write(']')
        return out.getvalue()


class Model (object):

    def __init__ (self):
        self.tie_character = '\u0361'
        self.etilde = '\u1ebd'
        self.data_dir = expanduser('~/work')
        self.resource_dir = expanduser('~/archive/2019/main/cmu_workshop/phontran')
        self.panphon_data_dir = resource_filename('panphon.featuretable', 'data')
        self.feature_table = FeatureTable()
        self.panphon_distance = Distance()
        self.gp_pairs = self.load_gp_pairs()
        self.a_phones = self.load_acoustic_phones()

    def iter_gp_pairs (self):
        with open(join(self.data_dir, 'map.txt')) as f:
            for line in f:
                yield line.strip().split(',')
    
    def untie (self, s):
        if self.tie_character in s:
            return s.replace(self.tie_character, '')
        else:
            return s
    
    def to_phones (self, s):
        f = self.feature_table
        s = self.untie(s)
        s = unicodedata.normalize('NFD', s)
        return [unicodedata.normalize('NFD', m.group('all'))
                for m in f.seg_regex.finditer(s)]

    def to_phone (self, s):
        phones = self.to_phones(s)
        if len(phones) != 1:
            raise Exception('Not a single phone: %s' % repr(s))
        return phones[0]

    def load_gp_pairs (self):
        return [(g, self.to_phones(p))
                for (g,p) in self.iter_gp_pairs()]
                   
    def p_vocabulary (self):
        return Vocabulary(phone
                          for (_, phones) in self.gp_pairs
                          for phone in phones)

    def phone_to_vector (self, phone):
        f = self.feature_table
        return f.fts(phone).numeric()

    def get_distance (self, phone1, phone2):
        d = self.panphon_distance
        return d.min_edit_distance(partial(d.weighted_deletion_cost, gl_wt=0.25),
                                   partial(d.weighted_insertion_cost, gl_wt=0.25),
                                   d.weighted_substitution_cost,
                                   [[]],
                                   [self.phone_to_vector(phone1)],
                                   [self.phone_to_vector(phone2)])

    def iter_acoustic_phones (self):
        with open(join(self.resource_dir, 'acoustic.txt')) as f:
            for (i, line) in enumerate(f):
                s = line.strip()
                phones = self.to_phones(s)
                #print(i, s, debug_string(s), debug_phones(phones))
                yield phones

    def load_acoustic_phones (self):
        return list(self.iter_acoustic_phones())

    def a_vocabulary (self):
        return Vocabulary(phone
                          for phone_list in self.a_phones
                          for phone in phone_list)


    def make_examples (self):
        return Examples(self)


def print_distances_to (tgt):
    m = Model()
    tgt = m.to_phone(tgt)
    for (d, phone) in sorted((m.get_distance(phone, tgt), phone)
                             for phone in m.p_vocabulary()):
        print(phone, d)

#print_distances_to('a')
#print()
#print_distances_to('t')

def print_pronunciation_phones ():
    m = Model()
    v = m.p_vocabulary()
    for (i, phone) in v.items():
        print(i, debug_string(phone))

def print_acoustic_phones ():
    m = Model()
    v = m.a_vocabulary()
    for (i, phone) in v.items():
        print(i, debug_string(phone))


def print_all_phones ():
    
    print('P')
    print_pronunciation_phones()
    
    print()
    print('A')
    print_acoustic_phones()


def bad_segmentation ():
    
    m = Model()
    s = '\u0062\u031e'
    
    f = m.feature_table
    s = m.untie(s)
    print(debug_string(s))
    s = unicodedata.normalize('NFD', s)
    print('normalized:', debug_string(s))
    for m in f.seg_regex.finditer(s):
        s = m.group('all')
        print('group:', debug_string(s))
        s = unicodedata.normalize('NFD', s)
        print('group,normed:', debug_string(s))


class Examples (object):

    def __init__ (self, model=None):
        dir = expanduser('~/work/ipa_samples/ojibwe')
        self.model = model or Model()
        self.filenames = [join(dir, name) for name in
                          ('Aaniin-Idamang_000000_00002789_00009030.txt',
                           'Aaniin-Idamang_000001_00009059_00015480.txt',
                           'Aaniin-Idamang_000002_00016319_00019919.txt',
                           'Aaniin-Idamang_000003_00020670_00024180.txt',
                           'Aaniin-Idamang_000004_00024210_00027270.txt',
                           'Aaniin-Idamang_000005_00027900_00029700.txt',
                           'Aaniin-Idamang_000006_00029700_00031110.txt',
                           'Aaniin-Idamang_000007_00031440_00034050.txt',
                           'Aaniin-Idamang_000008_00034560_00037920.txt',
                           'Aaniin-Idamang_000009_00038730_00045990.txt',
                           'Aaniin-Idamang_000010_00046260_00051660.txt',
                           'Aaniin-Idamang_000011_00051900_00054390.txt',
                           'Aaniin-Idamang_000012_00054990_00058620.txt',
                           'Aaniin-Idamang_000013_00059190_00065910.txt',
                           'Aaniin-Idamang_000014_00065970_00067320.txt',
                           'Aaniin-Idamang_000015_00067590_00069690.txt',
                           'Aaniin-Idamang_000016_00069690_00074040.txt',
                           'Aaniin-Idamang_000017_00074280_00077880.txt')]


    def __len__ (self):
        return len(self.filenames)

    def load_raw_input (self, i):
        with open(self.filenames[i]) as f:
            return f.read()

    def iter_input_phones (self, i):
        s = self.load_raw_input(i)
        print(i, repr(s))
        for word in s.split():
            for phone in self.model.to_phones(word):
                print(debug_string(phone))
                yield phone
    
    def load_input (self, i):
        return list(self.iter_input_phones(i))



class State (object):

    pass    



def print_distance_distribution ():
    
    dist = {}
    
    m = Model()
    for a in m.a_vocabulary():
        for p in m.p_vocabulary():
            d = m.get_distance(a, p)
            if d in dist:
                dist[d] += 1
            else:
                dist[d] = 1
    
    cum = 0
    for d in sorted(dist.keys()):
        cum += dist[d]
        print(d, dist[d], cum)
    
