import sqlite3
import numpy as np
from scipy.sparse import csc_matrix
from pagerank import powerIteration

conn = sqlite3.connect('function-calls.db')

c = conn.cursor()

c.execute("""
SELECT cfilename.name as `calling_filename`
FROM function_invocations f
       LEFT JOIN file_names cfilename on f.calling_filename = cfilename.rowid
WHERE
  f.requestname = 'XCYtdawTEVEAAB4EDbsAAAA-';
""")

res = [f[0] for f in c.fetchall()]
filenames = list(set(res))

num_encoded_filenames = np.array([filenames.index(f) for f in res])
transitions = zip(num_encoded_filenames, num_encoded_filenames[1:])

G = np.zeros(shape=(len(filenames), len(filenames)))

for i, j in transitions:
    G[j][i] += 1

for idx, v in sorted([d for d in enumerate(powerIteration(G))], key=lambda x: x[1], reverse=True):
    filename = filenames[idx]
    if 'lib\\php' not in filename and 'ClassLoader.class.php' not in filename and 'Login.class.php' not in filename and 'paths.php' not in filename and 'Registry.class.php' not in filename and 'Bootstrap.class.php' not in filename:
        print(filenames[idx], v)