---
name: videogyar-kozzetetel
description: A videógyár közzétételi állomása — leírás fejezetekkel és kötelező licencmegjelölésekkel (leiras.py), cím és borító, YouTube-feltöltés és ütemezés a YouTube Data API-val (OAuth, kvóta, korlátozások), gépi tartalom jelölése, végefőcím. Kifelé ható lépés: CSAK a felhasználó kimondott jóváhagyásával. Használd, ha leírást, címet vagy borítót kell készíteni, ha a felhasználó a rendszerből szeretne feltölteni vagy ütemezni, vagy ha a YouTube-kapcsolatot kell beállítani.
---

# Közzététel: leírás, cím, borító, feltöltés

**Ez az egyetlen állomás, ami kifelé hat.** Feltöltés, ütemezés, cím- vagy borítócsere, lejátszási
listába tétel csak a felhasználó kimondott jóváhagyása után. Előtte mutasd meg pontosan, mi fog
történni: a fájl, a cím, a leírás, a borító, a láthatóság és az időpont.

## 1. Leírás

```
python eszkozok/leiras.py epizodok/001_proba
```

Az `out/leiras.txt`-be írja: a `szoveg.json` címe és bevezetője (`leiras` mező), a fejezetek a jelenetek
hosszából (a `cim` mezőkből), és a `gyar.json` `kreditek` listájának sorai.

- **Fejezetek:** a YouTube akkor mutatja, ha az első 0:00-nál kezdődik, legalább három van, és mindegyik
  legalább 10 másodperces. Ha intró van az elején, a fejezetek eltolódnak (`--intro <mp>`).
- **Kötelező megjelölések:** ha a hangmotor vagy a zene licence megjelölést kér (pl. „Hang: X”, „Zene:
  Y, licenc Z”), az a `gyar.json` `kreditek` listájába kerül, és a leírás elejére. Ez a licenc
  feltétele lehet, nem udvariasság.
- A leírás első két sora a legfontosabb (ennyi látszik kinyitás nélkül): miről szól, kinek.

## 2. Cím és borító

A cím és a borító a felhasználó csatornájának ügye; ha van YouTube Analytics-adata, abból dolgozz.
Általános tapasztalatok, amikből ki lehet indulni:
- A cím a **néző kérdése vagy problémája** legyen, ne a funkció neve. Ha a videó egy ismert eszközről
  szól, a neve a cím elején legyen, ne zárójelben a végén.
- Kerüld a szakszót, ha a néző nem ismeri; és mindig legyen igaz arra, ami a videóban van.
- A borító: egy fő tárgy, 2–4 szó, nagy betű, kontraszt; tévén és telefonon is olvasható (lásd
  `videogyar-kep`, 6. pont). Két egymást követő borító ne hasonlítson egymásra.
- A videó első 10–15 másodperce váltsa be, amit a cím és a borító ígér (ne intróval kezdj).

## 3. Feltöltés a rendszerből (ha a felhasználó kéri)

Ha a felhasználó nem kéri, a rendszer csak előkészít: `out/vegleges.mp4`, `out/leiras.txt`, `borito.jpg`,
és ő tölti fel a YouTube Studióban. Ez teljesen jó megoldás.

Ha kéri, a YouTube Data API v3 kell:

1. **Google Cloud-projekt** a felhasználó fiókjával; a *YouTube Data API v3* engedélyezése.
2. **OAuth-hozzájárulási képernyő** és egy *Desktop app* típusú OAuth-kliens. A kliens azonosítója és
   titka a `.env`-be kerül, soha a kódba.
   - Ha a hozzájárulási képernyő „Testing” állapotú, a frissítő token néhány nap múlva lejárhat. Saját
     használatra a „Production” állapot a megoldás (a nem ellenőrzött alkalmazásra figyelmeztetést a
     felhasználó maga fogadja el).
3. **Jogosultságok** (scope): feltöltéshez `youtube.upload`; borítóhoz, listához, módosításhoz `youtube`.
   Csak annyit kérj, amennyi kell.
4. **Első bejelentkezés** egy kis szkripttel (pl. `google-auth-oauthlib`, helyi visszahívással); a
   frissítő token a `.env`-be kerül. **Egy token egy csatorna:** ha több csatorna van, külön `.env`,
   külön beszédes név, és soha ne keverd őket.
5. **Feltöltés:** `videos.insert`, folytatható (resumable) feltöltéssel. Ütemezéshez
   `status.privacyStatus = "private"` és `status.publishAt` (ISO 8601, UTC). Állítsd be a nyelvet,
   a kategóriát és a „gyerekeknek szól” nyilatkozatot (`selfDeclaredMadeForKids`).
6. **Borító:** `thumbnails.set` (1280×720, 2 MB alatt); egyéni borítóhoz a csatornának ellenőrzöttnek
   kell lennie.
7. **Visszaellenőrzés:** a feltöltés után olvasd vissza a videó adatait (cím, láthatóság, időpont), és
   írd meg a felhasználónak a linket.

Fontos korlátok (a feltöltés előtt mondd el a felhasználónak):
- **Kvóta:** alapból napi 10 000 egység, és egy feltöltés ebből sokat visz el. Nézd meg a kvótatáblát.
- **Auditálatlan API-projekt:** a Google szabálya szerint a nem auditált, újonnan létrehozott projektből
  feltöltött videók privát módba zárva maradhatnak, amíg a projekt át nem megy egy ellenőrzésen. Nézd
  meg a YouTube API Services aktuális szabályait. Ha ez gond, a feltöltés maradjon kézi.
- **Végefőcím** és néhány beállítás API-ból nem állítható; ezt a Studióban kell megcsinálni (kézzel,
  vagy ha az AI-eszközöd tud böngészőt vezérelni, azzal, a felhasználó szeme előtt).
- **Gépi vagy módosított tartalom:** ha a videóban valósághű, gépi hang vagy kép van (pl. klónozott
  hang), a YouTube jelölést kérhet. Ezt a Studióban (vagy, ha az API-verziód támogatja, a feltöltéskor)
  kell beállítani. Beszéld meg a felhasználóval.

A feltöltő szkriptből MCP-szervert is lehet csinálni, ha az AI gyakran kérdez le adatot a csatornáról
(lista, statisztika). Egyszeri feltöltéshez egy szkript is elég.

## 4. Utána

- Írd be az `ALLAPOT.md`-be: mi ment fel, mikor, milyen ID-val, mi van hátra (végefőcím, kitűzött komment).
- A leírásban szereplő linkek (pl. letölthető anyag) már az első feltöltéskor legyenek benne.
