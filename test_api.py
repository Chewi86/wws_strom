import getpass
import json
import urllib.parse
import urllib.request

BASE_URL = "https://api.wws.tarifdynamik.de"


def get_auth_token(username, password):
    """Holt das Bearer-Token über den exakten /tokens/ Endpunkt."""
    login_url = f"{BASE_URL}/tokens/"

    # Genau die Parameter aus der Swagger-Dokumentation:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
    ).encode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    req = urllib.request.Request(
        login_url, data=payload, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            # Laut Doku wird 'access_token' zurückgeliefert
            token = data.get("access_token") or data.get("token")
            return token
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Fehler beim Login: {e.code} {e.reason}")
        try:
            err_body = e.read().decode("utf-8")
            print(f"   Details: {err_body}")
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"\n❌ Fehler beim Verbindungsaufbau: {e}")
        return None

def fetch_energy_prices(token):
    """Holt die aktuellsten Preise (Day-Ahead / Zukunft) über den /latest Endpunkt."""
    prices_url = f"{BASE_URL}/public/energyprices/latest"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(prices_url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        print(f"\n❌ Fehler beim Abrufen: HTTP {e.code}")
        try:
            print("   Details:", e.read().decode("utf-8"))
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"\n❌ Fehler beim Verbindungsaufbau: {e}")
        return None


def main():
    print("=" * 55)
    print(" WestfalenWIND / Tarifdynamik API Test (OAuth2 /tokens)")
    print("=" * 55)

    username = input("E-Mail / Benutzername: ").strip()
    password = getpass.getpass("Passwort: ").strip()

    print("\n🔑 Starte Login-Prozess über /tokens/ ...")
    token = get_auth_token(username, password)

    if not token:
        print("\n⚠️ Login fehlgeschlagen. Bitte Zugangsdaten prüfen.")
        return

    print(f"\n✅ Login erfolgreich! Token erhalten: {token[:25]}...\n")

    print("📊 Rufe Energiepreise ab...")
    prices_data = fetch_energy_prices(token)

    if prices_data and "data" in prices_data:
        entries = prices_data["data"]
        print(f"✅ {len(entries)} Preis-Datensätze erfolgreich empfangen!\n")

        print("--- ERSTE 5 STUNDENEINTRÄGE ---")
        for item in entries[:102]:
            start = item.get("start")
            tariff = item.get("tariff_name")
            price = item.get("price_ct_kwh")
            is_smart = item.get("is_smart")
            print(
                f"Zeit: {start} | Tarif: {tariff} | Preis: {price} ct/kWh | Smart: {is_smart}"
            )
    else:
        print("Erhaltenes Ergebnis:", prices_data)


if __name__ == "__main__":
    main()