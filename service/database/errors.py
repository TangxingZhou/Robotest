from enum import Enum


class DatabaseAPIErrors(Enum):
    ErrLoginInstanceSuspend = 'Instance has been suspended'
    ErrLoginDBPlatformFailed = 'Wrong username or password'
    ErrIPHasNoAccess = "Host '.*' is not allowed to connect to this instance_"
    ErrSubsDBExists = "Subscription DB exists"
