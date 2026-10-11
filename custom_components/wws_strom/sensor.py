# """Sensor-Plattform für WestfalenWIND Stromtarif & Messwerte."""

# from __future__ import annotations

# from datetime import datetime, timedelta, timezone
# import json
# import logging
# import urllib.error
# import urllib.parse
# import urllib.request

# from homeassistant.components.sensor import (
    # SensorDeviceClass,
    # SensorEntity,
    # SensorStateClass,
# )
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.device_registry import DeviceInfo
# from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.helpers.update_coordinator import (
    # CoordinatorEntity,
    # DataUpdateCoordinator,
    # UpdateFailed,
# )

# from .const import (
    # AUTH_ENDPOINT,
    # CONF_PASSWORD,
    # CONF_USERNAME,
    # DOMAIN,
    # MEASUREMENTS_ENDPOINT,
    # PRICES_ENDPOINT,
# )

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(
    # hass: HomeAssistant,
    # entry: ConfigEntry,
    # async_add_entities: AddEntitiesCallback,
# ) -> None:
    # """Richtet die Sensoren auf Basis des Config Entries ein."""
    # username = entry.data[CONF_USERNAME]
    # password = entry.data[CONF_PASSWORD]

    # coordinator = WWSDataUpdateCoordinator(hass, username, password)
    # await coordinator.async_config_entry_first_refresh()

    # async_add_entities([
        # WWSPriceSensor(coordinator),
        # WWSMeasurementSensor(coordinator),
    # ], True)


# class WWSDataUpdateCoordinator(DataUpdateCoordinator):
    # """Koordinator zum periodischen Abrufen der Preissignale und Messwerte."""

    # def __init__(self, hass: HomeAssistant, username: str, password: str):
        # super().__init__(
            # hass,
            # _LOGGER,
            # name="WWS Strom Data Coordinator",
            # update_interval=timedelta(minutes=15),
        # )
        # self.username = username
        # self.password = password
        # self.token = None

    # def _get_token(self) -> str:
        # """Holt ein neues Bearer Token von der /tokens/ Route."""
        # payload = urllib.parse.urlencode({
            # "grant_type": "password",
            # "username": self.username,
            # "password": self.password,
        # }).encode("utf-8")

        # headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            # "Accept": "application/json",
        # }

        # req = urllib.request.Request(AUTH_ENDPOINT, data=payload, headers=headers, method="POST")
        # with urllib.request.urlopen(req, timeout=10) as response:
            # res_data = json.loads(response.read().decode("utf-8"))
            # return res_data.get("access_token") or res_data.get("token")

    # def _fetch_data(self, token: str) -> dict:
        # """Holt die Preissignale (heute + morgen) sowie die heutigen Messwerte."""
        # headers = {
            # "Authorization": f"Bearer {token}",
            # "Accept": "application/json",
        # }

        # # Zeitfenster: Heute 00:00 Uhr bis morgen 23:59 Uhr
        # now = datetime.now(timezone.utc)
        # start_today = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        # end_tomorrow = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

        # # 1. Preise mit explizitem Datumsbereich abrufen
        # # Falls PRICES_ENDPOINT auf /latest steht, wird der Basis-Endpunkt /public/energyprices/ verwendet
        # base_prices_endpoint = PRICES_ENDPOINT.replace("/latest", "")
        # price_params = urllib.parse.urlencode({
            # "start": start_today,
            # "end": end_tomorrow,
            # "aggregation_timezone": "Europe/Berlin",
        # })
        # prices_url = f"{base_prices_endpoint}?{price_params}"

        # try:
            # req_prices = urllib.request.Request(prices_url, headers=headers, method="GET")
            # with urllib.request.urlopen(req_prices, timeout=10) as response:
                # prices_data = json.loads(response.read().decode("utf-8"))
        # except Exception as err:
            # _LOGGER.warning("Fehler beim Abruf mit Datumsfilter, nutze /latest Fallback: %s", err)
            # req_prices = urllib.request.Request(PRICES_ENDPOINT, headers=headers, method="GET")
            # with urllib.request.urlopen(req_prices, timeout=10) as response:
                # prices_data = json.loads(response.read().decode("utf-8"))

        # # 2. Heutige Messwerte abfragen
        # measure_params = urllib.parse.urlencode({
            # "resolution": "DAY",
            # "start": start_today,
            # "end": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            # "aggregation_timezone": "Europe/Berlin",
        # })

        # measurements_url = f"{MEASUREMENTS_ENDPOINT}?{measure_params}"
        # req_measure = urllib.request.Request(measurements_url, headers=headers, method="GET")

        # measurements_data = {}
        # try:
            # with urllib.request.urlopen(req_measure, timeout=10) as response:
                # measurements_data = json.loads(response.read().decode("utf-8"))
        # except Exception as err:
            # _LOGGER.warning("Messwerte konnten nicht geladen werden: %s", err)

        # return {
            # "prices": prices_data,
            # "measurements": measurements_data,
        # }

    # async def _async_update_data(self):
        # """Aktualisiert die Daten im Executor-Thread."""

        # def _update():
            # try:
                # if not self.token:
                    # self.token = self._get_token()

                # try:
                    # return self._fetch_data(self.token)
                # except urllib.error.HTTPError as e:
                    # if e.code == 401:  # Token abgelaufen
                        # self.token = self._get_token()
                        # return self._fetch_data(self.token)
                    # raise

            # except Exception as err:
                # raise UpdateFailed(f"Fehler bei WWS-API Abruf: {err}") from err

        # return await self.hass.async_add_executor_job(_update)


# def _extract_list(raw_data) -> list:
    # """Hilfsfunktion: Extrahiert Listen unabhängig davon, ob die API ein List oder Dict zurückgibt."""
    # if isinstance(raw_data, list):
        # return raw_data
    # if isinstance(raw_data, dict):
        # return raw_data.get("data", raw_data.get("prices", []))
    # return []


# class WWSPriceSensor(CoordinatorEntity, SensorEntity):
    # """Haupt-Sensor für den aktuellen Strompreis und Smart-Tarif Zustand."""

    # _attr_icon = "mdi:currency-eur"
    # _attr_native_unit_of_measurement = "ct/kWh"

    # def __init__(self, coordinator: WWSDataUpdateCoordinator):
        # super().__init__(coordinator)
        # self._attr_name = "WWS Aktueller Strompreis"
        # self._attr_unique_id = f"wws_current_electricity_price_{coordinator.username}"

    # @property
    # def device_info(self) -> DeviceInfo:
        # return DeviceInfo(
            # identifiers={(DOMAIN, self.coordinator.username)},
            # name="WestfalenWIND Strom",
            # manufacturer="WestfalenWIND",
            # model="WWS Hochstift Smart",
        # )

    # @property
    # def native_value(self) -> float | None:
        # """Liefert den Preis der aktuell laufenden Stunde."""
        # current_entry = self._get_current_entry()
        # if current_entry and "price_ct_kwh" in current_entry:
            # return float(current_entry["price_ct_kwh"])
        # return None

    # @property
    # def extra_state_attributes(self) -> dict:
        # """Liefert is_smart, Tarifname und die Preisprognose."""
        # current_entry = self._get_current_entry()
        # prices_data = self.coordinator.data.get("prices", {}) if self.coordinator.data else {}
        # raw_list = _extract_list(prices_data)

        # is_smart = False
        # tariff_name = "Unbekannt"

        # if current_entry:
            # tariff_name = current_entry.get("tariff_name", "STANDARD")
            # is_smart = (
                # current_entry.get("is_smart") is True
                # or tariff_name == "SMART"
            # )

        # return {
            # "is_smart": is_smart,
            # "tariff_name": tariff_name,
            # "forecast": raw_list,
        # }

    # def _get_current_entry(self) -> dict | None:
        # """Ermittelt den aktuellen Stundeneintrag aus den Preisdaten."""
        # prices_data = self.coordinator.data.get("prices", {}) if self.coordinator.data else {}
        # data_list = _extract_list(prices_data)
        # if not data_list:
            # return None

        # now = dt_util.now()

        # for entry in data_list:
            # if not isinstance(entry, dict):
                # continue
            # try:
                # start_dt = dt_util.parse_datetime(entry["start"])
                # end_dt = dt_util.parse_datetime(entry["end"])

                # if start_dt and end_dt and start_dt <= now < end_dt:
                    # return entry
            # except (ValueError, KeyError, TypeError):
                # continue

        # # WICHTIG: Wenn die aktuelle Stunde nicht enthalten ist, None zurückgeben (kein data_list[0]!)
        # return None


# class WWSMeasurementSensor(CoordinatorEntity, SensorEntity):
    # """Sensor für den heutigen Energieverbrauch (aus der Smart-Meter-Messung)."""

    # _attr_device_class = SensorDeviceClass.ENERGY
    # _attr_state_class = SensorStateClass.TOTAL_INCREASING
    # _attr_native_unit_of_measurement = "kWh"

    # def __init__(self, coordinator: WWSDataUpdateCoordinator):
        # super().__init__(coordinator)
        # self._attr_name = "WWS Energieverbrauch Heute"
        # self._attr_unique_id = f"wws_energy_consumption_today_{coordinator.username}"

    # @property
    # def device_info(self) -> DeviceInfo:
        # return DeviceInfo(
            # identifiers={(DOMAIN, self.coordinator.username)},
            # name="WestfalenWIND Strom",
            # manufacturer="WestfalenWIND",
            # model="WWS Hochstift Smart",
        # )

    # @property
    # def native_value(self) -> float | None:
        # """Summiert den Verbrauch des heutigen Tages."""
        # m_data = self.coordinator.data.get("measurements", {}) if self.coordinator.data else {}
        # data_list = _extract_list(m_data)

        # if not data_list:
            # return None

        # total_kwh = sum(float(item.get("energy_kwh", 0)) for item in data_list if isinstance(item, dict))
        # return round(total_kwh, 3)

    # @property
    # def extra_state_attributes(self) -> dict:
        # """Gibt auch die angefallenen Gesamtkosten in EUR aus."""
        # m_data = self.coordinator.data.get("measurements", {}) if self.coordinator.data else {}
        # data_list = _extract_list(m_data)

        # total_cost_eur = sum(float(item.get("cost_eur", 0)) for item in data_list if isinstance(item, dict))

        # return {
            # "cost_today_eur": round(total_cost_eur, 2),
            # "raw_measurements": data_list,
        # }
        
        
"""Sensor-Plattform für WestfalenWIND Stromtarif & Messwerte."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    AUTH_ENDPOINT,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    MEASUREMENTS_ENDPOINT,
    PRICES_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet die Sensoren auf Basis des Config Entries ein."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    coordinator = WWSDataUpdateCoordinator(hass, username, password)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        WWSPriceSensor(coordinator),
        WWSMeasurementSensor(coordinator),
    ], True)


class WWSDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordinator zum periodischen Abrufen der Preissignale und Messwerte."""

    def __init__(self, hass: HomeAssistant, username: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name="WWS Strom Data Coordinator",
            update_interval=timedelta(minutes=15),
        )
        self.username = username
        self.password = password
        self.token = None

    def _get_token(self) -> str:
        """Holt ein neues Bearer Token von der /tokens/ Route."""
        payload = urllib.parse.urlencode({
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        req = urllib.request.Request(AUTH_ENDPOINT, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("access_token") or res_data.get("token")

    def _fetch_data(self, token: str) -> dict:
        """Holt Preissignale sowie heutige Messwerte."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        # 1. Neueste Preise abrufen
        try:
            req_prices = urllib.request.Request(PRICES_ENDPOINT, headers=headers, method="GET")
            with urllib.request.urlopen(req_prices, timeout=10) as response:
                prices_data = json.loads(response.read().decode("utf-8"))
        except Exception as err:
            _LOGGER.warning("Fehler beim Abruf der Strompreise: %s", err)
            prices_data = []

        # 2. Heutige Messwerte abfragen (Start heute 00:00 bis jetzt)
        now = datetime.now(timezone.utc)
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        measure_params = urllib.parse.urlencode({
            "resolution": "DAY",
            "start": start_today,
            "end": end_now,
            "aggregation_timezone": "Europe/Berlin",
        })

        measurements_url = f"{MEASUREMENTS_ENDPOINT}?{measure_params}"
        req_measure = urllib.request.Request(measurements_url, headers=headers, method="GET")

        measurements_data = {}
        try:
            with urllib.request.urlopen(req_measure, timeout=10) as response:
                measurements_data = json.loads(response.read().decode("utf-8"))
        except Exception as err:
            _LOGGER.warning("Messwerte konnten nicht geladen werden: %s", err)

        return {
            "prices": prices_data,
            "measurements": measurements_data,
        }

    async def _async_update_data(self):
        """Aktualisiert die Daten im Executor-Thread."""

        def _update():
            try:
                if not self.token:
                    self.token = self._get_token()

                try:
                    return self._fetch_data(self.token)
                except urllib.error.HTTPError as e:
                    if e.code == 401:  # Token abgelaufen
                        self.token = self._get_token()
                        return self._fetch_data(self.token)
                    raise

            except Exception as err:
                raise UpdateFailed(f"Fehler bei WWS-API Abruf: {err}") from err

        return await self.hass.async_add_executor_job(_update)


def _extract_list(raw_data) -> list:
    """Hilfsfunktion: Extrahiert Listen unabhängig davon, ob die API ein List oder Dict zurückgibt."""
    if isinstance(raw_data, list):
        return raw_data
    if isinstance(raw_data, dict):
        return raw_data.get("data", raw_data.get("prices", []))
    return []


class WWSPriceSensor(CoordinatorEntity, SensorEntity):
    """Haupt-Sensor für den aktuellen Strompreis und Smart-Tarif Zustand."""

    _attr_icon = "mdi:currency-eur"
    _attr_native_unit_of_measurement = "ct/kWh"

    def __init__(self, coordinator: WWSDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_name = "WWS Aktueller Strompreis"
        self._attr_unique_id = f"wws_current_electricity_price_{coordinator.username}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.username)},
            name="WestfalenWIND Strom",
            manufacturer="WestfalenWIND",
            model="WWS Hochstift Smart",
        )

    @property
    def native_value(self) -> float | None:
        """Liefert den Preis der aktuell laufenden Stunde."""
        current_entry = self._get_current_entry()
        if current_entry and "price_ct_kwh" in current_entry:
            return float(current_entry["price_ct_kwh"])
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Liefert is_smart, Tarifname und die vollständige Preisprognose."""
        current_entry = self._get_current_entry()
        prices_data = self.coordinator.data.get("prices", {}) if self.coordinator.data else {}
        raw_list = _extract_list(prices_data)

        is_smart = False
        tariff_name = "Unbekannt"

        if current_entry:
            tariff_name = current_entry.get("tariff_name", "STANDARD")
            is_smart = (
                current_entry.get("is_smart") is True
                or tariff_name == "SMART"
            )

        return {
            "is_smart": is_smart,
            "tariff_name": tariff_name,
            "forecast": raw_list,
        }

    def _get_current_entry(self) -> dict | None:
        """Ermittelt den aktuellen Stundeneintrag unter Berücksichtigung der Zeitzone."""
        prices_data = self.coordinator.data.get("prices", {}) if self.coordinator.data else {}
        data_list = _extract_list(prices_data)
        if not data_list:
            return None

        now = dt_util.now()

        for entry in data_list:
            if not isinstance(entry, dict):
                continue
            try:
                start_dt = dt_util.parse_datetime(entry["start"])
                end_dt = dt_util.parse_datetime(entry["end"])

                if start_dt and end_dt and start_dt <= now < end_dt:
                    return entry
            except (ValueError, KeyError, TypeError):
                continue

        return None


class WWSMeasurementSensor(CoordinatorEntity, SensorEntity):
    """Sensor für den heutigen Energieverbrauch (Smart Meter)."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, coordinator: WWSDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_name = "WWS Energieverbrauch Heute"
        self._attr_unique_id = f"wws_energy_consumption_today_{coordinator.username}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.username)},
            name="WestfalenWIND Strom",
            manufacturer="WestfalenWIND",
            model="WWS Hochstift Smart",
        )

    @property
    def native_value(self) -> float | None:
        """Summiert den Verbrauch des heutigen Tages in kWh."""
        m_data = self.coordinator.data.get("measurements", {}) if self.coordinator.data else {}
        data_list = _extract_list(m_data)

        if not data_list:
            return None

        total_kwh = sum(float(item.get("energy_kwh", 0)) for item in data_list if isinstance(item, dict))
        return round(total_kwh, 3)

    @property
    def extra_state_attributes(self) -> dict:
        """Gibt die angefallenen Gesamtkosten in EUR sowie Rohdaten aus."""
        m_data = self.coordinator.data.get("measurements", {}) if self.coordinator.data else {}
        data_list = _extract_list(m_data)

        total_cost_eur = sum(float(item.get("cost_eur", 0)) for item in data_list if isinstance(item, dict))

        return {
            "cost_today_eur": round(total_cost_eur, 2),
            "raw_measurements": data_list,
        }