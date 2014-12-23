#!/usr/bin/python3

import time
import signal
import tempfile
import subprocess

inputs = ['inet', 'ip']

def int2str(i):
  res = ''
  while i >= 1:
    r = i % 1000
    i = int(i / 1000)
    if i >= 1:
      res = "'%03d%s" % (r, res)
    else:
      res = "%i%s" % (r, res)
  return res

class Timeout(Exception):
  pass

def timeout_handler(signum, frame):
  """Handler for timeout. Raises 'Timeout' exception"""
  raise Timeout("Timeout")

signal.signal(signal.SIGALRM, timeout_handler)

def launch(cmd, timeout = 0):
  """Launches a command in a bash shell"""
  res = {'time': 0, 'timeouted': False, 'stdout': None, 'stderr': None, 'ret': 0}
  if timeout != 0:
    signal.alarm(timeout)
  try:
    with tempfile.NamedTemporaryFile(delete = False) as fout:
      with tempfile.NamedTemporaryFile(delete = False) as ferr:
        start_time = time.time()
        proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr, shell=True)
        res['ret'] = proc.wait()
        signal.alarm(0)
        res['time'] = time.time() - start_time
        res['stdout'] = fout
        res['stderr'] = ferr
  except Timeout:
    res['timeouted'] = True
    res['time'] = timeout
    subprocess.Popen('bash -c "CPIDS=$(pgrep -P %i) >/dev/null 2>&1; (sleep 1 && kill -KILL $CPIDS &) >/dev/null 2>&1; kill -TERM $CPIDS >/dev/null 2>&1"' % proc.pid, shell=True)
  signal.alarm(0)
  res['time'] *= 1000
  return res

print("* Compiling the different binaries")
launch('gcc -O3 diam.c -o diam')
launch('cd community && make')
launch('mkdir tmp/')

print('* Creating binary versions of our inputs')
for infile in inputs:
  print('  - %s' % (infile))
  launch('./community/convert -i %s -o tmp/%s.bin' % (infile, infile))

print('* Generating communities')
for infile in inputs:
  print('  - %s' % (infile))
  launch('./community/community -l -1 tmp/%s.bin > tmp/%s.tree' % (infile, infile))

print('* Reordering by communities')
for infile in inputs:
  print('  - %s' % (infile))
  print('    # Parsing file')
  f = open('tmp/%s.tree' % (infile), 'r')
  lines = f.readlines()
  f.close()
  res = []
  i = -1
  last = 1
  for line in lines:
    node, commu = line.split(' ')
    commu = commu[:-1]
    if int(node) < int(last):
      i += 1
      res.append({})
    last = node
    res[i][node] = commu
  n = len(res[0]) - 1
  nodes = list(range(n))
  print('    # Communitizing %i nodes' % (n))
  for i in range(len(nodes)):
    for j in range(len(res)):
      try:
        nodes[i] = res[j][str(nodes[i])]
      except:
        break
  print('    # Renumber with these new %i communities' % (len(set(nodes))))
  listkeys = [[ind for ind, v in enumerate(nodes) if v == val] for val in list(set(nodes))]
  listkeys = [item for sublist in listkeys for item in sublist]
  listvalues = [0] * n
  for idx, newval in enumerate(listkeys):
    listvalues[newval] = idx
  print('    # Parsing original graph file')
  f = open(infile, 'r')
  lines = f.readlines()
  f.close()
  print('      + Getting degrees')
  degrees = [0] * n
  for idx, line in enumerate(lines[1:(n + 1)]):
    degrees[listvalues[idx]] = int(line.split(' ')[1][:-1])
  print('      + Getting links')
  links = [[listvalues[int(elem)] for elem in line[:-1].split(' ')] for line in lines[(n + 1):]]
  print('    # Printing a new graph file to match this reordering')
  f = open("tmp/%s.renumbered" % (infile), 'w')
  f.write("%i\n" % (n))
  for idx, i in enumerate(degrees):
    f.write("%i %i\n" % (idx, i))
  for a, b in links:
    f.write("%i %i\n" % (a, b))
  f.close()

print('* Evaluating performance (Let it some time to run)')
for infile in inputs:
  print('  - %s' % (infile))
  res = launch('./diam -diam 20 2 < %s' % (infile))
  print('    # Diam unordered : %s ms' % (int2str(res['time'])))
  with open(res['stdout'].name, 'r') as f:
    idx = 1
    for line in f.readlines():
      if line[0:4] == 'TIME':
        print('      - Iteration %i : %s ms' % (idx, int2str(int(line[5:-1]))))
        idx += 1
  res = launch('./diam -diam 20 2 < tmp/%s.renumbered' % (infile))
  print('    # Diam reordered : %s ms' % (int2str(res['time'])))
  with open(res['stdout'].name, 'r') as f:
    idx = 1
    for line in f.readlines():
      if line[0:4] == 'TIME':
        print('      - Iteration %i : %s ms' % (idx, int2str(int(line[5:-1]))))
        idx += 1
  launch('./community/convert -i tmp/%s.renumbered -o tmp/%s.renumbered.bin' % (infile, infile))
  res = launch('./community/community -l -1 tmp/%s.bin' % (infile))
  print('    # Community unordered : %s ms' % (int2str(res['time'])))
  res = launch('./community/community -l -1 tmp/%s.renumbered.bin' % (infile))
  print('    # Community reordered : %s ms' % (int2str(res['time'])))

print('* Cleaning')
launch('rm -f diam')
launch('cd community && make clean')
launch('rm -rf tmp')
