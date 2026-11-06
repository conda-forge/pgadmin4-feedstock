import os
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig

web = Path("frontend/web").resolve()
env = dict(os.environ, NODE_ENV="production", NODE_OPTIONS="--max-old-space-size=4096")
yarn = shutil.which("yarn")
assert yarn is not None, "yarn is required to build the missing web assets"
subprocess.run([yarn, "install", "--immutable"], cwd=web, env=env, check=True)
subprocess.run([yarn, "run", "webpacker"], cwd=web, env=env, check=True)

wheel, = Path.cwd().glob("pgadmin4-*-py3-none-any.whl")
subprocess.run(
    [sys.executable, "-m", "pip", "install", str(wheel),
     "--no-deps", "--no-build-isolation", "-vv"],
    check=True,
)
package = Path(sysconfig.get_path("purelib")) / "pgadmin4"
shutil.copytree(web / "pgadmin/static/js/generated",
                package / "pgadmin/static/js/generated", dirs_exist_ok=True)
shutil.copyfile(Path(os.environ["RECIPE_DIR"]) / "conda_entry.py",
                package / "conda_entry.py")

# rattler-build generates portable noarch launchers from the entry points.
for name in ("pgadmin4", "pgadmin4-cli"):
    for suffix in ("", ".exe", "-script.py"):
        (Path(sysconfig.get_path("scripts")) / (name + suffix)).unlink(missing_ok=True)
