# Module loading file
# Add the lines with YOURMODULE, your module should also be present
# in the module loader path (best is in './modules')
#
# Skeleton:
# __import__("YOURMODULE", globals(), locals(), [])
# mod_list = ["mantis", "YOURMODULE"]
import sys
sys.path.append('./modules')

__import__("roulette", globals(), locals(), [])
__import__("as", globals(), locals(), [])


mod_list = [ "roulette", "mantis" ]
