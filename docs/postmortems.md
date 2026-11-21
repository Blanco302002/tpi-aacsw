# Postmortems: por qué se cayó cada uno (perspectiva de Proceso)

Un **postmortem** es el informe oficial que publica una empresa después de una caída: qué pasó minuto a
minuto, por qué pasó y qué va a cambiar para que no se repita. Acá se resumen los tres de las caídas del
TPI y uno de Akamai como precedente. Las citas son textuales y cortas, en el idioma original.

---

## Cloudflare — 18/11/2025
**Fuente:** [Cloudflare outage on November 18, 2025](https://blog.cloudflare.com/18-november-2025-outage/) (blog de Cloudflare, publicado el mismo día).

**Qué pasó, en simple.**
1. A las 11:05 UTC el equipo cambió los **permisos de una base de datos**.
2. Por ese cambio, una consulta empezó a devolver datos duplicados, y un **archivo de configuración generado
   automáticamente** (el de detección de bots) **duplicó su tamaño**.
3. Ese archivo se regenera cada 5 minutos y **se copia solo a toda la red**.
4. El software que lo lee tenía un límite fijo de 200 elementos (usaba unos 60). Al pasarse, **el proxy que
   atiende el tráfico se colgó** en todo el mundo.

**Tiempos (hora argentina = UTC−3):**

| Hora (UTC) | Qué pasó |
|---|---|
| 11:20 | Empiezan los errores |
| 11:31 | Primera alerta automática |
| 14:30 | Se recupera el tráfico principal |
| 17:06 | Todo normal (casi 6 horas en total) |

**Proceso:**
- El cambio de permisos sí se desplegaba de a poco, por grupos de servidores. Pero el archivo que generaba se
  **propagó a todas las máquinas de la red** de una vez.
- El sistema trataba ese archivo como confiable porque lo genera la propia Cloudflare, y no lo validaba como
  si fuera una entrada externa.
- Cloudflare lo llama su peor caída desde 2019.

**Dato clave para el TPI:** el informe dice que **Turnstile** (su control anti-bots, el del cartel *"desbloquee
challenges.cloudflare.com"*) estuvo **caído de 11:30 a 13:10 y de 14:40 a 15:30 UTC**. Turnstile se inserta
*dentro* de sitios de otras empresas, por ejemplo en logins. Eso le da sustento a la hipótesis de las
**dependencias ocultas**: un sitio podía fallar por Cloudflare sin que su DNS dijera "Cloudflare".

**Qué van a cambiar:**
- Tratar los archivos de configuración generados por ellos mismos **como si fueran entrada de usuarios** (validarlos).
- **Más "interruptores de apagado" globales** para funciones.
- Revisar cómo falla cada módulo del proxy.

**Tono:** sin culpables individuales. Disculpa explícita del CEO.
> "The software had a limit on the size of the feature file"

---

## AWS — 20/10/2025
**Fuente:** [Summary of the Amazon DynamoDB Service Disruption in the Northern Virginia (US-EAST-1) Region](https://aws.amazon.com/message/101925/) (AWS).

**Qué pasó, en simple.**
1. DynamoDB (una base de datos de AWS que usan muchísimos servicios, incluidos los de la propia AWS) tiene un
   **sistema automático que administra sus registros DNS**: la "guía telefónica" que dice dónde está el servicio.
2. Dos partes de ese sistema automático **se pisaron entre sí** (una "condición de carrera"). Una aplicó un plan
   viejo sobre uno nuevo, y la limpieza automática **dejó la dirección de DynamoDB vacía**.
3. Sin esa dirección, nada encontraba a DynamoDB. Detrás cayeron otros servicios de AWS que dependen de él
   (servidores, balanceadores, Lambda, la consola…).

**Tiempos:**

| Hora (PDT, Argentina = PDT+4 en esa fecha) | Qué pasó |
|---|---|
| 23:48 del 19/10 | Empiezan los errores |
| 00:38 del 20/10 | Identifican el DNS como origen |
| 02:25 | Restauran el DNS |
| 14:20 | Fin del evento: unas 14 horas y media, con tres etapas de impacto, porque los otros servicios tardaron en recuperarse en cadena |

**Proceso:**
- El error estaba **latente**: el diseño lo permitía desde antes y nunca se había dado.
- Fue en **una sola región** (us-east-1, Virginia), pero es la región de la que dependen muchísimos servicios
  globales. Un punto único de falla dentro de la nube.
- Hubo que intervenir a mano porque la automatización dejó un estado inconsistente.

**Qué van a cambiar:**
- **Apagaron esa automatización en todo el mundo** hasta corregir la falla y agregar protecciones.
- Límites de velocidad para que un balanceador no pueda sacar de servicio demasiada capacidad de golpe.
- Más pruebas de los procesos de recuperación.

**Tono:** sistémico, sin culpables individuales. Disculpa explícita.
> "The race condition involves an unlikely interaction between two of the DNS Enactors."

---

## CrowdStrike — 19/07/2024
**Fuentes:**
- [Preliminary Post Incident Review](https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/) (24/07/2024).
- [Channel File 291 Incident: Root Cause Analysis is Available](https://www.crowdstrike.com/en-us/blog/channel-file-291-rca-available/) (06/08/2024).
- Cifra de equipos afectados: [Microsoft, 20/07/2024](https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/).

**Qué pasó, en simple.**
1. CrowdStrike vende un antivirus para empresas (Falcon) que corre **dentro de Windows**, con permisos muy altos.
2. El 19/07 a las 04:09 UTC (01:09 en Argentina) mandó una **actualización de contenido de rutina**, del tipo
   "respuesta rápida" que se envía seguido para detectar amenazas nuevas.
3. Esa actualización tenía un error que **no detectaron**: el programa esperaba 21 datos y recibía 20, leyó
   memoria que no debía y **Windows se colgó con la pantalla azul**.
4. La revirtieron a las 05:27 UTC, **78 minutos después**. Pero las computadoras que ya la habían recibido
   quedaron trabadas y **hubo que arreglarlas una por una, a mano**.

**Escala:** Microsoft estimó **8,5 millones de equipos con Windows**, *"less than one percent of all Windows
machines"*. Aerolíneas, bancos y hospitales en todo el mundo. En Argentina, sobre todo aerolíneas.

(Microsoft habla del 18/07 porque en hora de EE. UU. todavía era jueves: 04:09 UTC del 19/07 = 21:09 del 18/07 en California.)

**Proceso:**
- Las actualizaciones del *programa* de CrowdStrike sí se despliegan por etapas, y el cliente elige qué versión
  usar. Pero este **contenido de "respuesta rápida" llegó a todas las computadoras conectadas de una vez**.
- El validador automático tenía **un error de lógica** y dejó pasar el archivo.
- Entre las conclusiones del análisis de causa raíz figura que estos contenidos *deberían tener despliegue
  por etapas*: no lo tenían.

**Qué van a cambiar** (según su análisis de causa raíz):
- **Despliegue por etapas** (canary) también para el contenido de respuesta rápida.
- Más validaciones y pruebas.
- Controles de límites en el intérprete, para que un archivo malo no tire Windows.
- **Darle al cliente control** sobre cuándo recibe estas actualizaciones.
- Revisión externa independiente.

**Tono:** sistémico, sin culpables individuales.
> "a Rapid Response Content update with an undetected error"

---

## Precedente: Akamai — 22/07/2021 (para "¿y si se cae Akamai?")
**Fuente:** [Akamai Summarizes Service Disruption (RESOLVED)](https://www.akamai.com/blog/news/akamai-summarizes-service-disruption-resolved) (Akamai).

- A las 15:45 UTC, una **actualización de configuración** activó un bug en el DNS de su red de distribución.
- Durante **hasta una hora**, sitios de clientes no se podían encontrar.
- Lo resolvieron **revirtiendo la actualización**.
- Compromiso: revisar su proceso de actualizaciones de software. Disculpa explícita.

> "a software configuration update triggered a bug in our Secure Edge Content Delivery Network"

En los 57 servicios del TPI, Akamai es la principal en 7: Santander, BBVA, TikTok, Disney+, HBO Max, Infobae y La Nación.

---

## El patrón común (lo que va al pitch)

| | Cloudflare 2025 | AWS 2025 | CrowdStrike 2024 | Akamai 2021 |
|---|---|---|---|---|
| **Qué lo disparó** | Cambio de permisos → archivo de configuración automático | Automatización de DNS | Actualización de contenido de rutina | Actualización de configuración |
| **¿Llegó a todos de golpe?** | Sí: el archivo, a toda la red | Una región, pero de la que depende todo | Sí: todas las PCs conectadas | El informe no lo dice |
| **¿Por qué no lo frenaron antes?** | Confiaban en un archivo propio; límite fijo | Falla latente en la automatización | Validador con un error; sin despliegue por etapas | No detallado |
| **Duración** | ~6 h | ~14,5 h | 78 min el envío; días para arreglar PCs | ~1 h |
| **Qué cambian** | Validar archivos propios, interruptores de apagado | Apagar la automatización, límites | Despliegue por etapas, control del cliente | Revisar el proceso |

**Las tres ideas de Proceso (con la bibliografía de la cátedra):**
1. **Ninguna caída la causó un hackeo ni "una persona que se equivocó":** fueron **cambios de rutina** (configuración,
   automatización, actualizaciones) que el **proceso** dejó llegar a todos.
2. **Despliegue gradual (*canary*):** mandar el cambio primero a una parte chica, mirar y recién después al resto.
   Dos de los tres no lo tenían para ese tipo de cambio, y lo ponen como corrección.
   (*Site Reliability Engineering*, Google; *Software Engineering at Google*.)
3. **Postmortems sin culpables:** los cuatro informes describen **fallas del sistema**, no de personas, y tres piden
   disculpas públicas. Es la práctica que recomiendan los libros SRE: se aprende del proceso, no se busca a quién castigar.

**Cierre:** *"El producto falló, la causa estaba en el proceso, y lo pagaron las personas."*
