# coding:utf-8

from collections import namedtuple
from json import loads
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Set

from xkits import Page
from xkits import Site


class IPTV_ORG_SITE(Site):
    LIFETIME = 28800  # 8 hours

    def __init__(self, url: str):
        super().__init__(base=url, lifetime=self.LIFETIME)


class IPTV_ORG_DATABASE(IPTV_ORG_SITE):

    def __init__(self, url: str):
        self.__database: Set[str] = set()
        super().__init__(url=url)

    def __len__(self) -> int:
        return len(self.__database)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__database)

    def __contains__(self, index: str) -> bool:
        return index in self.__database

    def update(self, datas: Any):
        raise NotImplementedError(f"cannot update datas: {datas}")

    def update_page(self, page: Page):
        self.update(loads(page.response.text))

    def update_index(self, indexs: Iterable[str]):
        self.__database = set(indexs)


class IPTV_ORG_M3U(IPTV_ORG_DATABASE):

    def __init__(self, url: str):
        super().__init__(url=url)

    def __iter__(self) -> Generator[Page, Any, None]:
        for index in super().__iter__():
            yield self[index]

    def __getitem__(self, index: str) -> Page:
        return self.page(f"{index}.m3u")


class IPTV_ORG_CATEGORIES(IPTV_ORG_M3U):
    CATEGORIES_URL = "https://iptv-org.github.io/iptv/categories"

    def __init__(self):
        super().__init__(url=self.CATEGORIES_URL)
        self.__categories: Dict[str, str] = {}

    @property
    def database(self) -> Dict[str, str]:
        return self.__categories

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'id': 'auto', 'name': 'Auto'}, ...]
        cate: List[str] = []
        name: List[str] = []
        for item in items:
            cate.append(item["id"])
            name.append(item["name"])
        self.__categories = dict(zip(cate, name))
        self.update_index(cate)


class IPTV_ORG_LANGUAGES(IPTV_ORG_M3U):
    LANGUAGES_URL = "https://iptv-org.github.io/iptv/languages"

    def __init__(self):
        super().__init__(url=self.LANGUAGES_URL)
        self.__languages: Dict[str, str] = {}

    @property
    def database(self) -> Dict[str, str]:
        return self.__languages

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'code': 'aaa', 'name': 'Ghotuo'}, ...]
        code: List[str] = []
        name: List[str] = []
        for item in items:
            code.append(item["code"])
            name.append(item["name"])
        self.__languages = dict(zip(code, name))
        self.update_index(code)


class IPTV_ORG_COUNTRIES(IPTV_ORG_M3U):
    COUNTRIES_URL = "https://iptv-org.github.io/iptv/countries"
    NAMEDTUPLE = namedtuple('country', ["name", "languages"])

    def __init__(self):
        super().__init__(url=self.COUNTRIES_URL)
        self.__countries: Dict[str, IPTV_ORG_COUNTRIES.NAMEDTUPLE] = {}

    @property
    def database(self) -> Dict[str, NAMEDTUPLE]:
        return self.__countries

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'name': 'Afghanistan', 'code': 'AF', 'languages': ['prs', 'pus', 'tuk'], 'flag': '🇦🇫'}, ...]
        tuples: List[IPTV_ORG_COUNTRIES.NAMEDTUPLE] = []
        code: List[str] = []
        for item in items:
            code.append(item["code"])
            tuples.append(self.NAMEDTUPLE(name=item["name"], languages=item["languages"]))  # noqa:E501
        self.__countries = dict(zip(code, tuples))
        self.update_index(code)


class IPTV_ORG_REGIONS(IPTV_ORG_M3U):
    REGIONS_URL = "https://iptv-org.github.io/iptv/regions"
    NAMEDTUPLE = namedtuple('region', ["name", "countries"])

    def __init__(self):
        super().__init__(url=self.REGIONS_URL)
        self.__regions: Dict[str, IPTV_ORG_REGIONS.NAMEDTUPLE] = {}

    @property
    def database(self) -> Dict[str, NAMEDTUPLE]:
        return self.__regions

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'code': 'AFR', 'name': 'Africa', 'countries': ['AO', 'BF', 'BI', 'BJ', 'BW', 'CD', 'CF', 'CG', 'CI', 'CM', 'CV', 'DJ', 'DZ', 'EG', 'EH', 'ER', 'ET', 'GA', 'GH', 'GM', 'GN', 'GQ', 'GW', 'KE', 'KM', 'LR', 'LS', 'LY', 'MA', 'MG', 'ML', 'MR', 'MU', 'MW', 'MZ', 'NA', 'NE', 'NG', 'RE', 'RW', 'SC', 'SD', 'SH', 'SL', 'SN', 'SO', 'SS', 'ST', 'SZ', 'TD', 'TF', 'TG', 'TN', 'TZ', 'UG', 'YT', 'ZA', 'ZM', 'ZW']}, ...]
        tuples: List[IPTV_ORG_REGIONS.NAMEDTUPLE] = []
        code: List[str] = []
        for item in items:
            code.append(item["code"])
            tuples.append(self.NAMEDTUPLE(name=item["name"], countries=item["countries"]))  # noqa:E501
        self.__regions = dict(zip(code, tuples))
        self.update_index(code)


class IPTV_ORG_SUBDIVISIONS(IPTV_ORG_DATABASE):
    SUBDIVISIONS_URL = "https://iptv-org.github.io/iptv/subdivisions"
    NAMEDTUPLE = namedtuple('subdivision', ["name", "code"])

    def __init__(self):
        super().__init__(url=self.SUBDIVISIONS_URL)
        self.__subdivisions: Dict[str, IPTV_ORG_SUBDIVISIONS.NAMEDTUPLE] = {}

    @property
    def database(self) -> Dict[str, NAMEDTUPLE]:
        return self.__subdivisions

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'country': 'AD', 'name': 'Andorra la Vella', 'code': 'AD-07'}, ...]
        tuples: List[IPTV_ORG_SUBDIVISIONS.NAMEDTUPLE] = []
        country: List[str] = []
        for item in items:
            country.append(item["country"])
            tuples.append(self.NAMEDTUPLE(name=item["name"], code=item["code"]))  # noqa:E501
        self.__subdivisions = dict(zip(country, tuples))
        self.update_index(country)


class IPTV_ORG_BLOCKLIST(IPTV_ORG_DATABASE):
    BLOCKLIST_URL = "https://iptv-org.github.io/iptv/blocklist"

    def __init__(self):
        super().__init__(url=self.BLOCKLIST_URL)
        self.__blocklist: Dict[str, str] = {}

    @property
    def database(self) -> Dict[str, str]:
        return self.__blocklist

    def update(self, items: List[Dict[str, str]]):
        # noqa:E501, like: [{'channel': '21Sextury.us', 'ref': 'https://github.com/iptv-org/iptv/issues/15723'}, ...]
        channel: List[str] = []
        ref: List[str] = []
        for item in items:
            channel.append(item["channel"])
            ref.append(item["ref"])
        self.__blocklist = dict(zip(channel, ref))
        self.update_index(channel)


class IPTV_ORG_API(IPTV_ORG_SITE):
    API_URL = "https://iptv-org.github.io/api"

    def __init__(self):
        super().__init__(url=self.API_URL)
        self.__subdivisions = IPTV_ORG_SUBDIVISIONS()
        self.__categories = IPTV_ORG_CATEGORIES()
        self.__blocklist = IPTV_ORG_BLOCKLIST()
        self.__languages = IPTV_ORG_LANGUAGES()
        self.__countries = IPTV_ORG_COUNTRIES()
        self.__regions = IPTV_ORG_REGIONS()

    @property
    def subdivisions(self) -> IPTV_ORG_SUBDIVISIONS:
        return self.__subdivisions

    @property
    def categories(self) -> IPTV_ORG_CATEGORIES:
        return self.__categories

    @property
    def blocklist(self) -> IPTV_ORG_BLOCKLIST:
        return self.__blocklist

    @property
    def languages(self) -> IPTV_ORG_LANGUAGES:
        return self.__languages

    @property
    def countries(self) -> IPTV_ORG_COUNTRIES:
        return self.__countries

    @property
    def regions(self) -> IPTV_ORG_REGIONS:
        return self.__regions

    def refresh(self) -> None:
        self.subdivisions.update_page(self.page("subdivisions.json"))
        self.categories.update_page(self.page("categories.json"))
        self.blocklist.update_page(self.page("blocklist.json"))
        self.languages.update_page(self.page("languages.json"))
        self.countries.update_page(self.page("countries.json"))
        self.regions.update_page(self.page("regions.json"))
