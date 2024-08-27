from typing import Optional
from vcon.civic_address import CivicAddress
from datetime import datetime


class Party:
    def __init__(self,
                 tel: Optional[str] = None,
                 stir: Optional[str] = None,
                 mailto: Optional[str] = None,
                 name: Optional[str] = None,
                 validation: Optional[str] = None,
                 gmlpos: Optional[str] = None,
                 civicaddress: Optional[CivicAddress] = None,
                 uuid: Optional[str] = None,
                 role: Optional[str] = None,
                 contact_list: Optional[str] = None,
                 meta: Optional[dict] = None) -> None:
        """
        Initialize a new Party object.

        :param tel: Telephone number of the party
        :type tel: str | None
        :param stir: STIR identifier of the party
        :type stir: str | None
        :param mailto: Email address of the party
        :type mailto: str | None
        :param name: Display name of the party
        :type name: str | None
        :param validation: Validation information of the party
        :type validation: str | None
        :param gmlpos: GML position of the party
        :type gmlpos: str | None
        :param civicaddress: Civic address of the party
        :type civicaddress: CivicAddress | None
        :param uuid: UUID of the party
        :type uuid: str | None
        :param role: Role of the party
        :type role: str | None
        :param contact_list: Contact list of the party
        :type contact_list: str | None
        """
        # copy the values that are not None
        # TODO: should we allow changing the values of the object?
        #       for now, we just use the values that are not None
        #       and ignore the other values
        #       (this is also how the old code worked)
        for key, value in locals().items():
            if value is not None:
                setattr(self, key, value)

    def to_dict(self):
        # copy the attributes that are not None
        # TODO: should we allow changing the values of the object?
        #       for now, we just use the values that are not None
        #       and ignore the other values
        #       (this is also how the old code worked)
        party_dict = {}
        for key, value in self.__dict__.items():
            # Don't include self in the dict
            if value is not None and key != "self":
                party_dict[key] = value
        return party_dict


class PartyHistory:
    def __init__(self, party: int, event: str, time: datetime):
        """
        Initialize a new PartyHistory object.

        :param party: Index of the party
        :type party: int
        :param event: Event type (e.g. "join", "leave")
        :type event: str
        :param time: Time of the event
        :type time: datetime
        """
        self.party = party
        self.event = event
        self.time = time
        
    def to_dict(self):
        return {
            "party": self.party,
            "event": self.event,
            "time": self.time
        }
