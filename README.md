# Sterownik pieca CO dla Home Assistanta / Boiler Controller for Home Assistant

## PL

Integracja łączy się ze sterownikiem **bezpośrednio po sieci domowej** (HTTP, `boiler.local`). Nie używa serwera MQTT ani internetu.

**Instalacja przez HACS**
1. HACS → menu (⋮) → *Własne repozytoria* → wklej adres tego repozytorium GitHub, kategoria *Integracja*.
2. Pobierz „Sterownik pieca CO”, uruchom ponownie Home Assistanta.
3. Jeśli sterownik jest w tej samej sieci WiFi co Home Assistant, pojawi się w *Ustawienia → Urządzenia i usługi* jako wykryty. Kliknij *Skonfiguruj*. Jeśli nie, dodaj integrację ręcznie i wpisz `boiler.local` lub adres IP sterownika.

**Co dostajesz:** stan (zatrzymany / auto / ręczny / alarm), temperatury (piec, woda, ślimak, pokój, spaliny), dmuchawa, zużyty opał, alarm, pompy i ślimak; przełączniki: praca, tryb ręczny, sterowanie pokojowe; nastawy: piec, CWU, pokój, maks. temperatura pieca w trybie pokojowym.

**Uwaga:** lokalne API sterownika nie ma hasła, więc używaj go tylko w zaufanej sieci domowej.

## EN

The integration talks to the controller **directly over your home network** (HTTP, `boiler.local`). It does not use the MQTT server or the internet.

**Install with HACS**
1. HACS → menu (⋮) → *Custom repositories* → paste this GitHub repository URL, category *Integration*.
2. Download "Boiler Controller", restart Home Assistant.
3. If the controller is on the same WiFi network as Home Assistant it shows up as discovered under *Settings → Devices & services*. Click *Configure*. Otherwise add the integration manually and enter `boiler.local` or the controller's IP address.

**Entities:** state (stopped / auto / manual / alarm), temperatures (boiler, water, auger, room, flue gas), blower, fuel used, alarm, pumps and auger; switches: running, manual mode, room control; setpoints: boiler, hot water, room, max boiler temperature in room mode.

**Note:** the controller's local API has no password, so use it only on a trusted home network.
