from typing import Optional


class CivicAddress:
    def __init__(self,
                 country: Optional[str],
                 a1: Optional[str],
                 a2: Optional[str],
                 a3: Optional[str],
                 a4: Optional[str],
                 a5: Optional[str],
                 a6: Optional[str],
                 prd: Optional[str],
                 pod: Optional[str],
                 sts: Optional[str],
                 hno: Optional[str],
                 hns: Optional[str],
                 lmk: Optional[str],
                 loc: Optional[str],
                 flr: Optional[str],
                 nam: Optional[str],
                 pc: Optional[str]):
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

    def to_dict(self) -> dict[str, str | None]:
        """
        Convert the CivicAddress object to a dictionary.

        :return: A dictionary of the object's attributes
        :rtype: dict[str, str | None]
        """
        return {
            "country": self.country,
            "a1": self.a1,
            "a2": self.a2,
            "a3": self.a3,
            "a4": self.a4,
            "a5": self.a5,
            "a6": self.a6,
            "prd": self.prd,
            "pod": self.pod,
            "sts": self.sts,
            "hno": self.hno,
            "hns": self.hns,
            "lmk": self.lmk,
            "loc": self.loc,
            "flr": self.flr,
            "nam": self.nam,
            "pc": self.pc
        }
