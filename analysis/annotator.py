# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
from pathlib import Path

SCANNER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<scanner>
    <serialization active="true" />
    <uuid>f8c961f9-496b-45bd-b177-a86b1f60a226</uuid>
    <path>{}/annotator-out/{}/0</path>
    <processor>
        <LOMBOK active="true" />
    </processor>
    <annotations />
</scanner>
"""
CHECKER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<serialization>
    <path>{}/annotator-out/{}/0</path>
</serialization>
"""

VERSION = '1.3.9-TAINT-SNAPSHOT'
# core-reactive, http and http-netty are not included in the list (CF crashes)
MODULES = ['aop', 'context', 'core', 'core-processor', 'http-client', 'http-client-core', 'http-server-netty', 'inject',
           'jackson-core', 'jackson-databind', 'json-core']
REPO = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip().decode('utf-8')
ANNOTATOR_JAR = "{}/.m2/repository/edu/ucr/cs/riple/annotator/annotator-core/{}/annotator-core-{}.jar".format(
    str(Path.home()), VERSION, VERSION)
UCRT_VERSION = '0.1-alpha-3-SNAPSHOT'

def prepare(dir, module):
    os.makedirs(dir, exist_ok=True)
    with open('{}/paths.tsv'.format(dir), 'w') as o:
        o.write("{}\t{}\n".format('{}/checker.xml'.format(dir), '{}/scanner.xml'.format(dir)))
    with open('{}/scanner.xml'.format(dir), 'w') as o:
        o.write(SCANNER.format(REPO, module))
    with open('{}/checker.xml'.format(dir), 'w') as o:
        o.write(CHECKER.format(REPO, module))


def run_annotator(module):
    if module not in MODULES:
        raise Exception("Invalid module: {}".format(module))
    out_dir = '{}/annotator-out/{}'.format(REPO, module)
    prepare(out_dir, module)
    commands = []
    commands += ["java", "-jar", ANNOTATOR_JAR]
    commands += ['-d', out_dir]
    commands += ['-bc', 'cd {} && ANNOTATOR_TYPE_ARG=true ANNOTATOR_POLY=true ANNOTATOR_LIBRARY=true UCRT_VERSION={} ./gradlew {}:compileJava --rerun-tasks'.format(REPO, UCRT_VERSION, module)]
    commands += ['-cp', '{}/paths.tsv'.format(out_dir)]
    commands += ['-i', 'edu.ucr.Initializer']
    commands += ['-n', 'edu.ucr.cs.riple.taint.ucrtainting.qual.RUntainted']
    commands += ['-cn', 'UCRTaint']
    commands += ["--depth", "25"]
    # Uncomment to see build output
    # commands += ['-rboserr']
    # Comment to inject root at a time
    commands += ['-ch']
    # Uncomment to disable cache
    commands += ['-dc']
    # Uncomment to disable outer loop
    # commands += ['-dol']
    # Uncomment to disable parallel processing
    # commands += ['--disable-parallel-processing']
    print(commands)
    subprocess.call(commands)


TO_RUN = MODULES
TO_RUN = ['http-server-netty']
## Uncomment to run all modules
# TO_RUN = MODULES
for module in TO_RUN:
    run_annotator(module)
