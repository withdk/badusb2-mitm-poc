# Basic script to play with possible alphabets for data exfil.
# Taken from: http://stackoverflow.com/questions/7074051/what-is-the-best-way-to-generate-all-possible-three-letter-strings

import itertools

dict=['C','N','S']
for i in itertools.product(dict, repeat = 3):
	print i
