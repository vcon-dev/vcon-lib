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
    
    New in vCon 0.3.0:
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


class PartyHistory:
    """
    A class representing party history events in a vCon dialog.
    
    Party history tracks when parties join, leave, or change state during
    a conversation. This is useful for understanding the flow of multi-party
    conversations where participants may not all join and leave at the same time.
    
    Supported event types (vCon 0.3.0 specification):
    - join: When the party joins the dialog
    - drop: When the party drops out of the dialog
    - hold: When the party is put on hold
    - unhold: When the party is taken off hold
    - mute: When the party is muted
    - unmute: When the party is taken off mute
    
    Attributes:
        party (int): Index of the party in the parties array
        event (str): Type of event (must be one of VALID_EVENTS)
        time (datetime): Time when the event occurred (serialized as ISO 8601)
    
    The time field is automatically serialized to ISO 8601 format when
    converted to dictionary representation.
    """
    # Valid event types for party history (from specification)
    VALID_EVENTS = [
        "join",      # when the party joins the dialog
        "drop",      # when the party drops out of the dialog
        "hold",      # when the party is put on hold
        "unhold",    # when the party is taken off hold
        "mute",      # when the party is muted
        "unmute"     # when the party is taken off mute
    ]

    def __init__(self, party: int, event: str, time: datetime):
        """
        Initialize a new PartyHistory object.

        :param party: Index of the party
        :type party: int
        :param event: Event type (e.g. "join", "drop", "hold", "unhold", 
                     "mute", "unmute")
        :type event: str
        :param time: Time of the event
        :type time: datetime
        """
        # Validate event type
        if event not in PartyHistory.VALID_EVENTS:
            raise ValueError(
                f"Invalid event '{event}'. "
                f"Must be one of: {PartyHistory.VALID_EVENTS}"
            )
        
        self.party = party
        self.event = event
        self.time = time

    def to_dict(self):
        # Handle time field which can be datetime or string
        if hasattr(self.time, 'isoformat'):
            time_value = self.time.isoformat()
        else:
            time_value = self.time
        return {
            "party": self.party, 
            "event": self.event, 
            "time": time_value
        }
