# Chore: Replace Print Statements with Python Logging

## Chore Description
Replace all print statements in the server code with proper Python logging using appropriate log levels. The logging system should:
- Preserve the exact same log output messages
- Ensure all output is written to standard out (stdout)
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Provide better control over log verbosity and formatting
- Enable future extensibility for log configuration (e.g., file logging, external log aggregation)

This chore improves code maintainability and follows Python best practices for production applications.

## Relevant Files

### Existing Files to Modify

- **`app/server/agent.py`** (Lines: 83, 98, 109, 124, 158, 178, 195-196)
  - Contains 8 print statements in agent tool wrapper functions
  - These are informational messages about tool invocations
  - Should use INFO level logging

- **`app/server/tools.py`** (Lines: 103, 116, 159, 179, 213, 313, 404)
  - Contains 6 print statements in error handling blocks
  - Line 404 contains a `safe_print` function definition used in code execution
  - Error messages should use ERROR level logging
  - The `safe_print` function needs special handling as it's part of the RestrictedPython sandbox

- **`app/server/agent_api.py`** (Lines: 137, 144, 263, 300, 353, 362, 368, 376)
  - Contains 8 print statements in error/warning handling
  - Mix of error messages and warnings
  - Should use ERROR for errors and WARNING for warnings

- **`app/server/db_utils.py`** (Lines: 117, 183, 219, 242)
  - Contains 4 print statements in error handling blocks
  - All are error messages that should use ERROR level logging

### New Files

No new files need to be created. All changes will be made to existing files.

## Step by Step Tasks

### 1. Configure Logging in Main Application Entry Point
- Add logging configuration in `app/server/agent_api.py` near the top of the file (after imports)
- Configure logging to:
  - Use INFO level as default
  - Format messages with timestamp, level, module name, and message
  - Output to stdout (console) using StreamHandler
  - Set format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- Add logger instance for the module: `logger = logging.getLogger(__name__)`

### 2. Add Logging Import and Logger to Each Module
- Add `import logging` to the imports section of each file:
  - `app/server/agent.py`
  - `app/server/tools.py`
  - `app/server/db_utils.py`
- Add logger instance near top of each file (after imports): `logger = logging.getLogger(__name__)`

### 3. Replace Print Statements in `app/server/agent.py`
- Replace all 8 print statements with `logger.info()` calls
- These are informational messages about tool calls, so INFO level is appropriate
- Preserve exact message content
- Lines to update: 83, 98, 109, 124, 158, 178, 195, 196

### 4. Replace Print Statements in `app/server/tools.py`
- Replace print statements in exception handlers with `logger.error()` calls
- Lines to update: 103, 116, 159, 179, 213, 313
- **Special handling for line 404 (`safe_print` function)**:
  - This function is used in the RestrictedPython sandbox for code execution
  - Keep the function but update its implementation to use logging
  - Use `logger.info()` inside the function to maintain sandbox security while using proper logging

### 5. Replace Print Statements in `app/server/agent_api.py`
- Replace error-related print statements with `logger.error()` calls (lines: 137, 144, 300, 376)
- Replace warning-related print statements with `logger.warning()` calls (lines: 263, 353, 362, 368)
- Preserve exact message content including f-string formatting

### 6. Replace Print Statements in `app/server/db_utils.py`
- Replace all 4 print statements with `logger.error()` calls
- These are all error messages in exception handlers
- Lines to update: 117, 183, 219, 242
- Preserve exact message content

### 7. Test the Changes
- Start the server and verify logs appear correctly in stdout
- Trigger various code paths to ensure all logging statements work
- Verify log format includes timestamp, level, and message
- Confirm no print statements remain in the codebase

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions
- `cd app/server && grep -r "print(" *.py | grep -v "safe_print"` - Verify no print statements remain (except safe_print definition)
- `cd app/server && python -c "import agent, tools, agent_api, db_utils; print('All imports successful')"` - Verify all modules import without errors
- `cd app/server && grep -r "import logging" *.py` - Verify logging is imported in all modified files
- `cd app/server && grep -r "logger = logging.getLogger" *.py` - Verify logger instances are created in all modified files

## Notes

**Important Considerations:**
1. **Log Levels**: Use appropriate log levels based on message severity:
   - INFO: Informational messages about tool invocations
   - WARNING: Non-critical issues that don't prevent execution
   - ERROR: Error conditions in exception handlers

2. **Logging Configuration**: The logging configuration should be set up once in `agent_api.py` as the main entry point. All other modules will inherit this configuration.

3. **Standard Out**: By default, Python's logging StreamHandler outputs to stderr. We need to explicitly configure it to use stdout to match the requirement.

4. **RestrictedPython Sandbox**: The `safe_print` function in `tools.py` is part of the code execution sandbox. It should be updated to use logging while maintaining security boundaries.

5. **Message Preservation**: All log messages must preserve exact content from original print statements to maintain observability and debugging capabilities.

6. **Future Extensibility**: This logging setup provides a foundation for future enhancements such as:
   - Log rotation and file-based logging
   - Different log levels for different environments (dev/staging/prod)
   - Integration with external logging services (CloudWatch, DataDog, etc.)
   - Structured logging (JSON format) for better parsing

7. **Testing**: Since there are no existing tests, manual testing is required. Start the server and trigger various endpoints to verify logs are working correctly.
