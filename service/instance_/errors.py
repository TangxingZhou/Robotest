from enum import Enum


class InstanceAPIErrors(Enum):
    ErrLoginInstanceSuspend = 'Instance has been suspended'
    ErrLoginDBPlatformFailed = 'Wrong username or password'
    ErrParamInvalid = 'Invalid Params'
    ErrMaxInstanceCountExceeded = 'Max instance_ count exceeded'
    ErrInstanceNotBelongToUid = 'Instance does not belong to current uid'
