# Python interpreter
Always run python through uv.

# Linter
This repo has very strict linter.
- Do not loosen it - you are not allowed to configure it at all.
- Do not silence problems - fix them
- After code changes run `make check` to validate linter is 100% green and all tests pass.

## File size limit
We have linter limiting files to be no more than 200 lines. 
It means that when approaching the limit - plan logical file decomposition refactoring. 
NEVER try to save lines by re-formatting - decompose the file.
NEVER try to compact code - decompose the file.
NEVER use suboptimal, but more compact solutions just to fit in 200 lines - decompose the file and use the optimal solution.
NEVER try to make several things in one line to save space - decompose the file.
It is just a strong signal for refactoring. In fact, the optimal length is below 180. So the file above 180 lines is already a weak signal for refactoring.

# Concurrent modifications
If you notice that some files are unexpectedly modified (not by you) - do not rever these changes,
probably the user is working on the same file. If it is blocking you - stop and contact the user to sync. Or if these changes are not breaking for you - proceed. But never revert unexpected changes!

# Comments policy
Keep comments and docstrings clean - do not document obvious things, do not keep temporary comments and docstrings.

# No legacy policy
Always do full refactoring - do not leave any legacy code for "backward compatibility." Remove code which is not needed anymore.

# No fallbacks policy
Always fail fast in any unexpected situation - do not try to add any silent fallbacks or defaults. Fail loudly in any unexpected situation.
