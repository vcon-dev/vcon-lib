from typing import Optional
from typing import Optional

class CivicAddress:
    def __init__(self,
                 country: Optional[str] = None,
                 a1: Optional[str] = None,
                 a2: Optional[str] = None,
                 a3: Optional[str] = None,
                 a4: Optional[str] = None,
                 a5: Optional[str] = None,
                 a6: Optional[str] = None,
                 prd: Optional[str] = None,
                 pod: Optional[str] = None,
                 sts: Optional[str] = None,
                 hno: Optional[str] = None,
                 hns: Optional[str] = None,
                 lmk: Optional[str] = None,
                 loc: Optional[str] = None,
                 flr: Optional[str] = None,
                 nam: Optional[str] = None,
                 pc: Optional[str] = None):
        """
        Initialize a new CivicAddress object.

        :param country: Country code (ISO 3166-1 alpha-2)
        :type country: str
        :param a1: Administrative area 1 (e.g. state or province)
        :type a1: str
        :param a2: Administrative area 2 (e.g. county or municipality)
        :type a2: str
        :param a3: Administrative area 3 (e.g. city or town)
        :type a3: str
        :param a4: Administrative area 4 (e.g. neighborhood or district)
        :type a4: str
        :param a5: Administrative area 5 (e.g. postal code)
        :type a5: str
        :param a6: Administrative area 6 (e.g. building or floor)
        :type a6: str
        :param prd: Premier (e.g. department or suite number)
        :type prd: str
        :param pod: Post office box identifier
        :type pod: str
        :param sts: Street name
        :type sts: str
        :param hno: House number
        :type hno: str
        :param hns: House name
        :type hns: str
        :param lmk: Landmark name
        :type lmk: str
        :param loc: Location name
        :type loc: str
        :param flr: Floor
        :type flr: str
        :param nam: Name of the location
        :type nam: str
        :param pc: Postal code
        :type pc: str
        """
        self.country = country
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self.a6 = a6
        self.prd = prd
        self.pod = pod
        self.sts = sts
        self.hno = hno
        self.hns = hns
        self.lmk = lmk
        self.loc = loc
        self.flr = flr
        self.nam = nam
        self.pc = pc

    def to_dict(self) -> dict[str, Optional[str]]:
        """
        Convert the CivicAddress object to a dictionary.

        The dictionary keys are the attribute names of the object, and the
        values are the attribute values.

        :return: A dictionary of the object's attributes
        :rtype: dict[str, Optional[str]]
        """
        return {attr: getattr(self, attr) for attr in dir(self) if not attr.startswith("_") and getattr(self, attr) is not None and not callable(getattr(self, attr))}

