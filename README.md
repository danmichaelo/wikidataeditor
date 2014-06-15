Basic Python Wikidata-editor adhering to PEP8 and making use of quality libraries such as `Requests`.

Example:

```python
import sys
from wikidataeditor import Site
wd = Site('MyAwesomeTool/0.1 (+http://tools.wmflabs.org/myawesometool)')  # Specifying our user-agent

if not wd.login('username', 'verysecretpassword'):
	print 'Login failed'
	sys.exit(1)

item = wd.item('Q5')
for claim in item.claims('P31'):
	print claim

```