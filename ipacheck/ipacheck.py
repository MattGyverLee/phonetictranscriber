from ipapy import UNICODE_TO_IPA
from ipapy import is_valid_ipa
from ipapy.ipachar import IPAConsonant
from ipapy.ipachar import IPAVowel
from ipapy.ipastring import IPAString
import re
import unicodedata

s_uni_raw = u"ʔtʰn̥əˈkiːn èʔæˌkænˈθɑ.lə.d͡ʒi"
s_uni = unicodedata.normalize("NFD", s_uni_raw)
s_uni2 = u"ʔtʰn̥əkinèʔækænθɑləd͡ʒi"
s_uni_ns = s_uni.replace(" ", "")
s_ipa = IPAString(unicode_string=s_uni)
s_ipa_ns = IPAString(unicode_string=s_uni.replace(" ", ""))
s_ipa_consonants = s_ipa.consonants
s_ipa_vowels = s_ipa.vowels


cvPat = ""
for char in s_ipa_ns:
    if char.is_consonant:
        cvPat += "C"
    elif char.is_vowel:
        cvPat += "V"
    elif char.is_diacritic:
        cvPat += "D"
    elif char.is_tone:
        cvPat += "T"
    elif char.is_length:
        cvPat += "L"
    elif char.is_suprasegmental:
        cvPat += "S"
    elif char.is_length:
        cvPat += "L"
    else:
        cvPat += "X"

aftercuts = []
tempCV = re.findall(r"C[^V]*|V[^C]*", cvPat)
subbies = []
subbiesRep = []
limits = []
csegs = []
vsegs = []
end = 1
i = 0
while i < len(s_ipa_ns.ipa_chars):
    if s_ipa_ns.ipa_chars[i].is_consonant:
        segment = s_ipa_ns.ipa_chars[i].unicode_repr
        while not s_ipa_ns.ipa_chars[end].is_vowel:
            end += 1
            segment += s_ipa_ns.ipa_chars[end-1].unicode_repr
        limits.append([i, end])
        i = end+1
        csegs += segment
        segment = ""
    if s_ipa_ns.ipa_chars[i].is_vowel:
        segment = s_ipa_ns.ipa_chars[i].unicode_repr
        while not s_ipa_ns.ipa_chars[end].is_consonant:
            end += 1
            segment += s_ipa_ns.ipa_chars[end-1].unicode_repr
        limits.append([i, end-1])
        i = end
        vsegs += segment
        segment = ""
print(limits)
""" for sub in s_ipa_ns.ipa_chars:
    if sub.isConsonant:
        print(sub.unicode_repr)
    elif
    sub.unicode_repr """
for sub in re.finditer(r"C[^V\r\n]*[^VC\r\n]*|V[^C\r\n]*[^VC\r\n]*", cvPat):
    indexes = sub.regs[0]
    startIndex = int(indexes[0])
    stopIndex = int(indexes[1])
    subString = s_uni_ns[startIndex:stopIndex]
    subbies.append(subString)
    subbiesRep.append(cvPat[startIndex:stopIndex])

print(subbies)

""" for i in range(1, len(cvPat)):
    print(i)
    if cvPat[i] == "C":
        if cvPat[i+1] in "CTDX":
            i += 1
        else:
            aftercuts.append(i)
    elif cvPat[i] == "V":
        if cvPat[i+1] in "VTDX":
            continue
        else:
            aftercuts.append(i)
    elif char.is_tone:
        cvPat += "T"
    elif char.is_diacritic:
        cvPat += "D"
    else:
        cvPat += "X"
 """

print(s_ipa_ns)
print(cvPat)
