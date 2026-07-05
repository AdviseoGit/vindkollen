import subprocess
print(subprocess.check_output(['git', '-C', '/data/workspace/projects/vindkollen', 'diff', 'static/intaktsdelning-vindkraft.html'], text=True))
