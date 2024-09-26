from enum import Enum


class AdminAPIErrors(Enum):
    ErrLoginInstanceSuspend = 'Instance has been suspended'
    ErrLoginDBPlatformFailed = 'Wrong username or password'
    ErrParamInvalid = 'Invalid Params'
    ErrMaxInstanceCountExceeded = 'Max instance_ count exceeded'
