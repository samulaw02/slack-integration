from pydantic import BaseModel
import typing
import dataclasses
from dataclasses import dataclass
import datetime





@dataclass
class CallPostAuthorizeRes:
    status: bool
    protected_data: typing.Dict
    consent_user: str
    metadata: typing.Dict


@dataclass
class GetUsersPageReq:
    page_token: typing.Optional[str] = None



@dataclass
class UserMailData:
    is_enabled: typing.Optional[bool] = None
    emails_sent: typing.Optional[int] = None
    spam_emails_received: typing.Optional[int] = None
    emails_received: typing.Optional[int] = None
    reason: typing.Optional[str] = None


@dataclass
class UserName:
    givenName: str
    familyName: str
    fullName: str


@dataclass
class UserEmail:
    address: str
    primary: typing.Optional[bool] = None


@dataclass(order=True)
class FileDTO:
    container_name: str
    file_name: str
    file_type: typing.Optional[str] = None


@dataclass
class IntGroupData:
    group_id: str
    group_name: str
    role: str
    type: str
    status: str
    delivery_settings: str


@dataclass
class UserRecord:
    org_id: str
    int_name: str
    user_id: str
    primary_email: str
    is_admin: bool
    admin_extra_info: typing.Dict
    suspended: bool
    archived: bool
    org_unit_path: str
    is_enrolled_in_2_sv: bool
    is_enforced_in_2_sv: bool
    name: UserName
    emails: typing.List[UserEmail]
    mail_data: UserMailData
    password_strength: typing.Optional[str] = None
    password_length_compliance: typing.Optional[str] = None
    record_creation_time: typing.Optional[datetime.datetime] = None
    record_last_update_time: typing.Optional[datetime.datetime] = None
    last_login_time: typing.Optional[datetime.datetime] = None
    creation_time: typing.Optional[datetime.datetime] = None
    last_mail_fetch: typing.Optional[datetime.datetime] = None
    groups: typing.List[str] = dataclasses.field(default_factory=list)
    recovery_email: typing.Optional[str] = dataclasses.field(default=None)
    user_photo: typing.Optional[FileDTO] = None
    int_groups: typing.List[IntGroupData] = dataclasses.field(default_factory=list)
    extra_data: typing.Dict = dataclasses.field(default_factory=dict)


@dataclass
class GetUsersPageRes:
    users: typing.List[UserRecord]
    page_token: typing.Optional[str] = None



@dataclass
class GetAppsReq:
    org_id: str
    user: UserRecord
    # this was added in order to make it possible to call slack api
    page_token: typing.Optional[str] = None



@dataclass
class AppRecord:
    org_id: str
    int_name: str
    user_name: str
    user_id: str
    client_id: str
    display_text: str
    native_app: bool
    scopes: typing.List[str]
    is_grant_app: bool
    record_creation_time: typing.Optional[datetime.datetime] = None
    record_last_update_time: typing.Optional[datetime.datetime] = None
    user_key: typing.Optional[str] = None
    verified: typing.Optional[bool] = None



@dataclass
class GetAppsRes:
    apps: typing.List[AppRecord]
    page_token: typing.Optional[str] = None






