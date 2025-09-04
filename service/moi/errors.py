from enum import Enum


class WorkspaceAPIErrors(Enum):
    ErrLoginInstanceSuspend = 'Instance has been suspended'
    ErrLoginDBPlatformFailed = 'Wrong username or password'
    ErrParamInvalid = 'Invalid Params'
    ErrMaxInstanceCountExceeded = 'Max instance count exceeded'
    ErrServer = 'Internal Server Error'
