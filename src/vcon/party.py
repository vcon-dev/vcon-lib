from typing import Optional
from vcon.civic_address import CivicAddress
from datetime import datetime


class Party:
    """
    A class representing a party (participant) in a vCon conversation.
    
    A party represents a participant in the conversation with various contact
    and identification information. Parties can be callers, agents, or any
    other participants in the conversation.
    
    Supported contact methods:
    - tel: Telephone number
    - mailto: Email address
    - sip: SIP URI for VoIP communication
    - did: Decentralized Identifier for blockchain-based identity
    
    Contact information:
    - name: Display name of the party
    - jCard: vCard format contact information (RFC 7095)
    - timezone: Party's timezone for temporal context
    
    Location and validation:
    - civicaddress: Civic address information (GEOPRIV format)
    - gmlpos: GML position coordinates
    - validation: Validation information for the party
    
    Additional metadata:
    - uuid: Unique identifier for the party
    - role: Role in the conversation (e.g., "caller", "agent")
    - stir: STIR identifier for secure telephony
    - contact_list: Reference to contact list
    - meta: Additional metadata
    
    New in vCon 0.4.0:
    - sip: SIP URI for the party
    - did: Decentralized Identifier
    - jCard: vCard format contact information
    - timezone: Party's timezone
    """
    def __init__(
        self,
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
        meta: Optional[dict] = None,
        sip: Optional[str] = None,
        did: Optional[str] = None,
        jCard: Optional[dict] = None,
        timezone: Optional[str] = None,
        **kwargs
    ) -> None:
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
        :param sip: SIP URI for the party
        :type sip: str | None
        :param did: Decentralized Identifier
        :type did: str | None
        :param jCard: vCard format contact information
        :type jCard: dict | None
        :param timezone: Party's timezone
        :type timezone: str | None
        :param kwargs: Additional attributes to be set on the party
        """
        # copy the named parameters that are not None
        for key, value in locals().items():
            if value is not None and key not in ("self", "kwargs"):
                setattr(self, key, value)

        # copy any additional kwargs
        for key, value in kwargs.items():
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
                # Handle CivicAddress objects by calling their to_dict method
                if hasattr(value, 'to_dict') and callable(value.to_dict):
                    party_dict[key] = value.to_dict()
                else:
                    party_dict[key] = value
        return party_dict
