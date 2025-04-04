# Changelog

## bugfix/error_overload - 4/4/25
    - the setInterval function in error_handling.js was causing too much traffic to the server and most likely was the cause of crash the portal-django docker container experienced on 4/3/25

### Changed

### Added
    - This CHANGELOG.md file (https://common-changelog.org/#12-guiding-principles)
    - portal.apps.error_handling.decorators.py file which contains the @handle_error decorator
        • This decorator gets any errors that may occur in the loading of a view function, filters them by type, and creates and returns the appropriate django message

### Removed
    - Class AerpawError and functions from error_handling.js because:
        • the setInterval function was causing too much traffic to the server and most likely crashed the portal-django docker container
        • only errors from threads need to be checked for on an interval

### Fixed



