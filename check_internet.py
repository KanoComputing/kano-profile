import subprocess
import sys


def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

cmd = 'fping -c 10 -p 30ms -qs 8.8.8.8'

o, e = run(cmd)
lines = [line.strip() for line in e.splitlines()]

for l in lines:
    if 'alive' in l:
        if l == '1 alive':
            sys.stdout.write('0')
            sys.exit(0)

sys.stdout.write('1')
sys.exit(1)




