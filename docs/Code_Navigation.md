
# @ Notation
I envision a system where the character combination `#@` may be used to quickly find certain aspects of code. The `#@` symbol may be followed by pre-defined commands for filtering. In VSCode, the key command `shift + command + f` brings the user to the project search window. They may make a search in the entire codebase for `#@` symbols as a basic tag. Following key phrases indicate certain areas, and they may view the results to quickly find all references of that type.  
*This works with my workflow in python, since I don't use @ very often - all systems subject to change and experimentation*

### `#@revisit`
This means that at some point this part of code should be revisited at some point. An overview of all pending tasks may quickly be found for the entire codebase. If a revisit for a particular user(s) is wanted, the syntax `#@revisit-Andy` or `@re-Andy` may suffice. A grouping may look like: `#@revisit-Andy @re-AlterEgo @re-Nemesis`  
The use of short-tags allows more flexibility. For example: `@LEAD@re-Andy`indicates that user `Andy` is the most important person to see and review that portion of code. A search of all `@LEAD` results in a quick summary of all leadership decisions. A subset query is `@LEAD@re` showing all LEAD revisitations of code.

# Random Tid-Bits (to grow)
### To count lines of python code in project folder
find . -type f -name "*.py" | xargs wc -l