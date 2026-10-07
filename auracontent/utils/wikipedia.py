import os
import re
import time
import requests
from constants import WIKI_API_URL


class WikidataChecker:
    API_URL = WIKI_API_URL
    HEADERS = {
        "User-Agent": os.getenv(
            "WIKIMEDIA_CONTACT",
            "auraContentPipeline/1.0 (contact non configure)"
        )
    }
    CACHE = {}
    MIN_DELAY_BETWEEN_CALLS = 0.6

    @classmethod
    def _throttled_get(cls, params, max_retries=2):
        for attempt in range(max_retries + 1):
            time.sleep(cls.MIN_DELAY_BETWEEN_CALLS)
            try:
                r = requests.get(cls.API_URL, params=params, headers=cls.HEADERS, timeout=10)
                if r.status_code == 429:
                    wait = 3 * (attempt + 1)
                    print(f"⏳ Wikidata 429, attente {wait}s avant retry...")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                return r
            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    print(
                        f"⚠️ Wikidata erreur reseau (abandon apres {max_retries + 1} tentatives) :{e}"
                        )
                    return None
                time.sleep(2)
        return None

    @classmethod
    def _search_entity_ids(cls, location_name, limit=3):
        params = {
            "action": "wbsearchentities",
            "search": location_name,
            "language": "fr",
            "format": "json",
            "limit": limit,
            "type": "item",
        }
        r = cls._throttled_get(params)
        if r is None:
            return []
        try:
            results = r.json().get("search", [])
            return [item.get("id") for item in results if item.get("id")]
        except Exception as e:
            print(f"⚠️ Wikidata (parsing recherche) erreur pour '{location_name}' : {e}")
            return []

    @classmethod
    def _get_country_for_entity(cls, entity_id):
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "claims",
            "format": "json",
        }
        r = cls._throttled_get(params)
        if r is None:
            return None
        try:
            entities = r.json().get("entities", {})
            entity = entities.get(entity_id, {})
            claims = entity.get("claims", {})
            country_claims = claims.get("P17")
            if not country_claims:
                return None
            country_entity_id = (
                country_claims[0]
                .get("mainsnak", {})
                .get("datavalue", {})
                .get("value", {})
                .get("id")
            )
            if not country_entity_id:
                return None
            return cls._resolve_entity_label(country_entity_id)
        except Exception as e:
            print(f"⚠️ Wikidata (parsing pays) erreur pour '{entity_id}' : {e}")
            return None

    @classmethod
    def _resolve_entity_label(cls, entity_id):
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "labels",
            "languages": "fr|en",
            "format": "json",
        }
        r = cls._throttled_get(params)
        if r is None:
            return None
        try:
            entities = r.json().get("entities", {})
            entity = entities.get(entity_id, {})
            labels = entity.get("labels", {})
            label = labels.get("fr") or labels.get("en")
            if label:
                return label.get("value")
        except Exception as e:
            print(f"⚠️ Wikidata (parsing label) erreur : {e}")
            return None

    @classmethod
    def get_real_country(cls, location_name, hint_country=None):
        if not location_name:
            return None

        cache_key = f"{location_name.strip().lower()}|{(hint_country or '').lower()}"
        if cache_key in cls.CACHE:
            return cls.CACHE[cache_key]

        entity_ids = cls._search_entity_ids(location_name, limit=3)
        if not entity_ids:
            cls.CACHE[cache_key] = None
            return None

        candidates_countries = []
        for entity_id in entity_ids:
            country = cls._get_country_for_entity(entity_id)
            candidates_countries.append(country)

            if hint_country and country and _countries_match(hint_country, country):
                cls.CACHE[cache_key] = country
                return country

        result = next((c for c in candidates_countries if c), None)
        cls.CACHE[cache_key] = result
        return result


def _normalize_country_text(text):
    return re.sub(r"[^a-z]", "", str(text or "").lower())


def _countries_match(declared, real):
    if not declared or not real:
        return True
    d = _normalize_country_text(declared)
    r = _normalize_country_text(real)
    return d == r or d in r or r in d
