"""Testi della pagina in inglese e in italiano.

Ogni voce è  chiave: (inglese, italiano).  I termini tecnici che in finanza si usano in inglese
(spread, breakeven, forward, probit, TIPS, Fed funds...) restano in inglese anche nella versione italiana:
tradurli renderebbe il testo meno chiaro, non più chiaro.

Nei testi, {nome} è un segnaposto riempito dal codice con un numero o una data già calcolati.
"""

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "it": ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"],
}

MONTHS_FULL = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
           "novembre", "dicembre"],
}

STR = {
    # ---------------------------------------------------------------- testata
    "topbar": ("U.S. Treasury par yield curve · 1990 to {last} · daily",
               "Curva dei rendimenti dei Treasury USA (par yield) · 1990-{last} · dati giornalieri"),
    "tk_10y": ("10Y yield", "Rendimento 10Y"),
    "tk_2y": ("2Y yield", "Rendimento 2Y"),
    "tk_spread": ("10Y - 2Y", "10Y - 2Y"),
    "tk_curve": ("Curve", "Curva"),
    "tk_last_inv": ("Last inverted", "Ultima inversione"),
    "tk_delta": ("{v} bp vs 1y ago", "{v} bp su 1 anno"),
    "tk_two_years": ("last two years", "ultimi due anni"),
    "tk_thresholds": ("below 0 inverted · 0-25 bp flat", "sotto 0 invertita · 0-25 bp piatta"),
    "tk_days_ago": ("{n} <small>days ago</small>", "{n} <small>giorni fa</small>"),
    "tk_never": ("never", "mai"),
    "tk_below_zero": ("spread below zero", "spread sotto zero"),
    "state_Normal": ("Normal", "Normale"),
    "state_Flat": ("Flat", "Piatta"),
    "state_Inverted": ("Inverted", "Invertita"),

    # ------------------------------------------------------- titolo e conclusioni
    "head_thesis": (
        "The longest yield-curve inversion in {years} years ended without a recession. What does the curve say now?",
        "La più lunga inversione della curva in {years} anni è finita senza una recessione. Cosa dice la curva adesso?"),
    "head_generic": (
        "Reading the U.S. yield curve: what the bond market says about growth, policy and risk",
        "Leggere la curva dei rendimenti USA: cosa dice il mercato obbligazionario su crescita, politica monetaria "
        "e rischio"),
    "sub_thesis": (
        "The 10Y-2Y spread stayed below zero for {days} days ({start} to {end}), and the NBER has dated no recession "
        "since {rec_end}. Today the curve is {state} at {sp} bp, and the model puts the chance of a recession in "
        "12 months at {p}%.",
        "Lo spread 10Y-2Y è rimasto sotto zero per {days} giorni ({start} - {end}) e l'NBER non ha datato nessuna "
        "recessione dopo {rec_end}. Oggi la curva è {state} a {sp} bp e il modello stima al {p}% la probabilità di "
        "una recessione tra 12 mesi."),
    "sub_generic": (
        "Data through {last}: the curve is {state} at {sp} bp, and the model puts the chance of a recession in "
        "12 months at {p}%.",
        "Dati fino al {last}: la curva è {state} a {sp} bp e il modello stima al {p}% la probabilità di una "
        "recessione tra 12 mesi."),
    "byline": ("By {name} · data through {last}", "Di {name} · dati fino al {last}"),
    "byline_plain": ("Data through {last}", "Dati fino al {last}"),
    "kp_title": ("Key points", "In sintesi"),
    "kp1_k": ("Inversion without recession.", "Inversione senza recessione."),
    "kp1_v": (
        "The 10Y-2Y spread stayed below zero for {days} days ({start} to {end}) and fell as low as {low} bp. In the "
        "{n} earlier cases a recession began {mn} to {mx} months after the first inversion; this one started {now} "
        "months ago and the NBER has dated no recession since {rec_end}.",
        "Lo spread 10Y-2Y è rimasto sotto zero per {days} giorni ({start} - {end}) ed è sceso fino a {low} bp. "
        "Nei {n} casi precedenti una recessione è iniziata da {mn} a {mx} mesi dopo la prima inversione; questa è "
        "iniziata {now} mesi fa e l'NBER non ha datato nessuna recessione dopo {rec_end}."),
    "kp1_alt": (
        "The longest inversion in the data lasted {days} days ({start} to {end}) and fell as low as {low} bp.",
        "L'inversione più lunga nei dati è durata {days} giorni ({start} - {end}) ed è scesa fino a {low} bp."),
    "kp2_k": ("What the recession model says.", "Cosa dice il modello di recessione."),
    "kp2_v": (
        "The Estrella-Mishkin probit read {peak}% in {date} and reads {p}% now. It is a probability built on one "
        "variable, not a forecast of a date.",
        "Il probit di Estrella-Mishkin segnava {peak}% ({date}) e oggi segna {p}%. È una probabilità costruita su "
        "una sola variabile, non la previsione di una data."),
    "kp3_k": ("Policy stance.", "Orientamento della politica monetaria."),
    "kp3_v": (
        "Fed funds are {ff}% against CPI inflation of {cpi}%, a real policy rate of {real} pp: policy is {stance}. "
        "The Sahm rule indicator is {sahm} pp, {sahm_status}.",
        "I Fed funds sono al {ff}% con inflazione CPI al {cpi}%, un tasso reale di {real} p.p.: la politica è "
        "{stance}. L'indicatore della regola di Sahm è {sahm} p.p., {sahm_status}."),
    "stance_restrictive": ("restrictive", "restrittiva"),
    "stance_neutral": ("roughly neutral", "più o meno neutrale"),
    "stance_accommodative": ("accommodative", "accomodante"),
    "sahm_on": ("above the 0.5 trigger", "sopra la soglia di 0,5"),
    "sahm_off": ("below the 0.5 trigger", "sotto la soglia di 0,5"),
    "kp4_k": ("Inflation expectations.", "Attese di inflazione."),
    "kp4_v": (
        "The 5y5y forward is {fwd}% and the 10-year breakeven is {be10}%, {anchor}.",
        "Il 5y5y forward è {fwd}% e il breakeven a 10 anni è {be10}%, {anchor}."),
    "anchor_ok": ("close to the 2% target", "vicino all'obiettivo del 2%"),
    "anchor_above": ("above the 2% target", "sopra l'obiettivo del 2%"),
    "anchor_below": ("below the 2% target", "sotto l'obiettivo del 2%"),
    "kp5_k": ("Italy.", "Italia."),
    "kp5_v": (
        "The BTP-Bund spread is {now} pp ({last_date}), against peaks of {pre_peak} pp ({pre_date}) and "
        "{post_peak} pp ({post_date}).",
        "Lo spread BTP-Bund è {now} p.p. ({last_date}), contro i picchi di {pre_peak} p.p. ({pre_date}) e "
        "{post_peak} p.p. ({post_date})."),
    "guide_title": ("New to yield curves? Start here", "Nuovo alle curve dei rendimenti? Parti da qui"),

    # ---------------------------------------------- titoli di sezione, figure e fonti
    "h_curve": ("What is the curve doing?", "Cosa fa la curva?"),
    "h_curve_cap": (
        "Everything starts from the shape of the curve and how it has changed since 1990. Figure 1 shows it in "
        "three dimensions. Figure 2 reduces it to a single number: the spread between the 10-year and the 2-year "
        "yield.",
        "Tutto parte dalla forma della curva e da come è cambiata dal 1990. La Figura 1 la mostra in tre "
        "dimensioni. La Figura 2 la riduce a un solo numero: lo spread tra il rendimento a 10 e a 2 anni."),
    "h_model": ("What does the recession model say?", "Cosa dice il modello di recessione?"),
    "h_fed": ("How tight is the Fed?", "Quanto è restrittiva la Fed?"),
    "h_infl": ("What does the market expect for inflation?", "Che inflazione si aspetta il mercato?"),
    "h_italy": ("How much extra risk does the market charge Italy?", "Quanto rischio in più sconta il mercato sull'Italia?"),
    "h_explore": ("Explore the data", "Esplora i dati"),
    "h_method": ("Method and limits", "Metodo e limiti"),
    "fig1": ("Figure 1. U.S. Treasury yield curve by month, 1990 to today",
             "Figura 1. Curva dei rendimenti dei Treasury USA, mese per mese, dal 1990 a oggi"),
    "fig1_read": (
        "<b>How to read Figure 1.</b> Time runs left to right, one curve per month. Depth is maturity, from "
        "3 months (front) to 30 years (back). Height and color are the yield: amber is high, dark blue is close to "
        "zero. An inversion shows where the front edge rises above the back edge.",
        "<b>Come leggere la Figura 1.</b> Il tempo scorre da sinistra a destra, una curva al mese. La profondità è "
        "la scadenza, da 3 mesi (davanti) a 30 anni (dietro). Altezza e colore sono il rendimento: ambra = alto, "
        "blu scuro = vicino a zero. Un'inversione si vede dove il bordo davanti sale sopra quello dietro."),
    "fig2": ("Figure 2. Spread between the 10-year and the 2-year yield, daily",
             "Figura 2. Spread tra il rendimento a 10 e a 2 anni, dati giornalieri"),
    "fig3": ("Figure 3. Probability of a recession 12 months ahead, Estrella-Mishkin probit",
             "Figura 3. Probabilità di recessione tra 12 mesi, probit di Estrella-Mishkin"),
    "fig4": ("Figure 4. Fed funds rate and CPI inflation; real policy rate; Sahm rule indicator",
             "Figura 4. Fed funds e inflazione CPI; tasso reale di politica monetaria; regola di Sahm"),
    "fig5": ("Figure 5. Market-implied inflation: breakeven and 5y5y forward",
             "Figura 5. Inflazione implicita nel mercato: breakeven e 5y5y forward"),
    "fig6": ("Figure 6. 10-year government bond yields", "Figura 6. Rendimenti dei titoli di Stato a 10 anni"),
    "fig7": ("Figure 7. Spread against the Bund, 10-year bonds",
             "Figura 7. Spread rispetto al Bund, titoli a 10 anni"),
    "fig8": ("Figure 8. Slope of the curve, 10-year minus 3-month: United States and euro area",
             "Figura 8. Pendenza della curva, 10 anni meno 3 mesi: Stati Uniti e area euro"),
    "src_treasury": ("Source: U.S. Department of the Treasury (par yield curve); author's calculations.",
                     "Fonte: U.S. Department of the Treasury (par yield curve); elaborazione dell'autore."),
    "src_probit": ("Source: FRED (GS10, TB3MS, USREC); NBER recession dates; author's estimates.",
                   "Fonte: FRED (GS10, TB3MS, USREC); date delle recessioni NBER; stime dell'autore."),
    "src_policy": ("Source: FRED (FEDFUNDS, CPIAUCSL, UNRATE, USREC); author's calculations.",
                   "Fonte: FRED (FEDFUNDS, CPIAUCSL, UNRATE, USREC); elaborazione dell'autore."),
    "src_infl": ("Source: U.S. Department of the Treasury (nominal and real yield curves); author's calculations.",
                 "Fonte: U.S. Department of the Treasury (curve dei rendimenti nominali e reali); "
                 "elaborazione dell'autore."),
    "src_europe": ("Source: OECD via FRED; NBER; author's calculations.",
                   "Fonte: OCSE tramite FRED; NBER; elaborazione dell'autore."),

    # ------------------------------------------------------------ introduzione
    "intro_p": (
        "The U.S. government borrows money by selling bonds called <b>Treasuries</b>. For each length of time, from "
        "3 months to 30 years, it pays a different interest rate: the <b>yield</b>. Putting those rates side by side "
        "gives the <b>yield curve</b>, and its shape says what the market expects from the economy. When short-term "
        "rates rise above long-term ones the curve is <b>inverted</b>, which has often come before a recession. "
        "This page follows the curve since 1990 and adds the macro pieces around it: the central bank (the Fed), "
        "inflation, recession risk, and the Italian spread.",
        "Il governo degli Stati Uniti si finanzia vendendo titoli di Stato, i <b>Treasury</b>. Per ogni durata, da "
        "3 mesi a 30 anni, paga un interesse diverso: il <b>rendimento</b> (yield). Mettendo questi tassi in fila si "
        "ottiene la <b>curva dei rendimenti</b>, e la sua forma dice cosa si aspetta il mercato per l'economia. "
        "Quando i tassi a breve superano quelli a lungo la curva è <b>invertita</b>, e questo spesso ha preceduto "
        "una recessione. La pagina segue la curva dal 1990 e aggiunge i pezzi macro intorno: la banca centrale "
        "(la Fed), l'inflazione, il rischio di recessione e lo spread dell'Italia."),
    "gl_yield_k": ("Yield", "Rendimento (yield)"),
    "gl_yield_v": (
        "The yearly interest for lending to the government for a given time. {y10}% on 10 years means about "
        "{y10} dollars a year for every 100 lent.",
        "L'interesse annuo che prendi prestando soldi al governo per una certa durata. {y10}% a 10 anni significa "
        "circa {y10} dollari l'anno ogni 100 prestati."),
    "gl_spread_k": ("Spread", "Spread"),
    "gl_spread_v": ("The difference between two rates. 10Y-2Y is the 10-year rate minus the 2-year rate.",
                    "La differenza tra due tassi. 10Y-2Y è il tasso a 10 anni meno quello a 2 anni."),
    "gl_bp_k": ("bp (basis points)", "bp (punti base)"),
    "gl_bp_v": ("One hundredth of a percentage point. 100 bp = 1%.",
                "Un centesimo di punto percentuale. 100 bp = 1%."),
    "gl_inv_k": ("Inverted curve", "Curva invertita"),
    "gl_inv_v": ("Short-term rates above long-term rates: a sign that a slowdown is expected.",
                 "Tassi a breve sopra quelli a lungo: segnale che il mercato si aspetta un rallentamento."),

    # ------------------------------------------------------------ riepilogo

    # ------------------------------------------------------------ 01 superficie
    "view": ("View", "Vista"),
    "view_landscape": ("Landscape", "Paesaggio"),
    "view_top": ("Top-down", "Dall'alto"),
    "view_side": ("Side profile", "Di profilo"),
    "ev_1990": ("1990: rates ~{z}%", "1990: tassi ~{z}%"),
    "ev_2000": ("2000: inversion", "2000: inversione"),
    "ev_2006": ("2006-07: inversion", "2006-07: inversione"),
    "ev_2020": ("2020: rates ~0", "2020: tassi ~0"),
    "ev_2023": ("2022-24: inversion", "2022-24: inversione"),
    "deepest": ("Deepest inversion", "Inversione più profonda"),
    "latest_curve": ("Latest curve", "Curva più recente"),
    "ax_year": ("Year", "Anno"),
    "ax_maturity": ("Maturity", "Scadenza"),
    "ax_yield": ("Yield (%)", "Rendimento (%)"),
    "cb_yield": ("Yield", "Rendimento"),

    # --------------------------------------------------------------- 02 segnale
    "s2_cap": (
        "The spread is the 10-year yield minus the 2-year yield. When it drops below zero the curve is inverted: "
        "the market is pricing lower short-term rates ahead, usually because it expects growth to slow. "
        "The longest inversion in the data ran from {start} to {end} ({days} days). Grey bands are NBER recessions.",
        "Lo spread è il rendimento a 10 anni meno quello a 2 anni. Quando scende sotto zero la curva è invertita: "
        "il mercato sconta tassi a breve più bassi in futuro, di solito perché si aspetta un rallentamento della "
        "crescita. L'inversione più lunga nei dati dura {days} giorni ({start} - {end}). Le fasce grigie sono le "
        "recessioni NBER."),
    "spread_pos": ("Spread above zero", "Spread sopra zero"),
    "inverted": ("Inverted", "Invertita"),
    "pp_title": ("percentage points", "punti percentuali"),

    # ------------------------------------------------------------ 03 probit
    "s3_cap": (
        "Estrella and Mishkin (1996) showed that the 10-year minus 3-month spread predicts U.S. recessions better "
        "than most alternatives, and the New York Fed publishes a version of this model. It is a probit regression: "
        "<b>P(recession 12 months ahead) = Φ(a + b × spread)</b>, where Φ is the normal cumulative distribution. "
        "Estimated here on {n} monthly observations from {start}, covering {nrec} recessions. "
        "Grey bands are NBER recessions.",
        "Estrella e Mishkin (1996) hanno mostrato che lo spread tra rendimento a 10 anni e a 3 mesi anticipa le "
        "recessioni USA meglio della maggior parte degli indicatori alternativi, e la Fed di New York pubblica una "
        "versione di questo modello. È una regressione probit: <b>P(recessione tra 12 mesi) = Φ(a + b × spread)</b>, "
        "dove Φ è la funzione di ripartizione della normale. Qui è stimata su {n} osservazioni mensili dal {start}, "
        "che coprono {nrec} recessioni. Le fasce grigie sono le recessioni NBER."),
    "prob_series": ("Model probability", "Probabilità del modello"),
    "prob_y": ("probability, %", "probabilità, %"),
    "st_now": ("now", "oggi"),
    "st_spread_10y3m": ("10Y-3M spread", "spread 10Y-3M"),
    "outcome_yes": (" and the economy was in an NBER-dated recession 12 months later",
                    " e 12 mesi dopo l'economia era in una recessione datata dall'NBER"),
    "outcome_no": (" and the economy was not in an NBER-dated recession 12 months later",
                   " e 12 mesi dopo l'economia non era in una recessione datata dall'NBER"),
    "prob_note": (
        "<b>How to read it.</b> The model sees only the curve. Since 2021 its highest reading was {peak}% in "
        "{date}{outcome}: a high value says the curve looks like past pre-recession curves, not that a recession "
        "has a date. Coefficients are close to the published ones (a near -0.5, b near -0.6). AUC is the chance "
        "that the model ranks a random pre-recession month above a random normal month (0.5 is a coin flip). "
        "Limits: {nrec} recessions, in-sample fit, serial correlation in the residuals (standard errors are not "
        "shown), and a single explanatory variable. No yield-curve model anticipates a shock like the 2020 pandemic.",
        "<b>Come leggerlo.</b> Il modello vede solo la curva. Dal 2021 il suo valore massimo è stato {peak}% "
        "({date}){outcome}: un valore alto dice che la curva somiglia a quelle che hanno preceduto le recessioni "
        "passate, non che una recessione abbia una data. I coefficienti sono vicini a quelli pubblicati (a intorno "
        "a -0,5, b intorno a -0,6). L'AUC è la probabilità che il modello assegni un valore più alto a un mese "
        "pre-recessione che a un mese normale scelti a caso (0,5 equivale a testa o croce). Limiti: {nrec} "
        "recessioni, stima sugli stessi dati, autocorrelazione dei residui (gli errori standard non sono mostrati) "
        "e una sola variabile esplicativa. Nessun modello basato sulla curva anticipa uno shock come la pandemia "
        "del 2020."),

    # ------------------------------------------------------ 04 politica monetaria
    "s4_cap": (
        "The <b>real policy rate</b> is the federal funds rate minus CPI inflation (year on year): the cost of "
        "money after inflation. Positive and high means restrictive policy, negative means accommodative. "
        "Inversions tend to show up when the Fed tightens faster than markets expect growth to hold. The bottom "
        "panel is the <b>Sahm rule</b>: when the 3-month average unemployment rate rises 0.5 points above its low "
        "of the previous 12 months, the labor market has historically been in recession.",
        "Il <b>tasso reale di politica monetaria</b> è il tasso sui Fed funds meno l'inflazione CPI (su base "
        "annua): il costo del denaro al netto dell'inflazione. Positivo e alto significa politica restrittiva, "
        "negativo significa accomodante. Le inversioni tendono a comparire quando la Fed stringe più in fretta di "
        "quanto il mercato si aspetti che la crescita regga. Il pannello in basso è la <b>regola di Sahm</b>: "
        "quando la media a 3 mesi del tasso di disoccupazione supera di 0,5 punti il minimo dei 12 mesi "
        "precedenti, il mercato del lavoro è storicamente già in recessione."),
    "ff_rate": ("Fed funds rate", "Tasso Fed funds"),
    "cpi_yoy": ("CPI inflation (y/y)", "Inflazione CPI (annua)"),
    "real_pos": ("Real rate > 0 (restrictive)", "Tasso reale > 0 (restrittivo)"),
    "real_neg": ("Real rate < 0 (accommodative)", "Tasso reale < 0 (accomodante)"),
    "sahm_series": ("Sahm rule indicator", "Indicatore regola di Sahm"),
    "real_y": ("real rate, pp", "tasso reale, p.p."),
    "sahm_y": ("Sahm, pp", "Sahm, p.p."),
    "st_ff": ("fed funds", "Fed funds"),
    "st_cpi": ("CPI inflation", "inflazione CPI"),
    "st_real": ("real policy rate", "tasso reale"),
    "st_unemp": ("unemployment", "disoccupazione"),
    "st_sahm": ("Sahm indicator", "indicatore di Sahm"),
    "pp_unit": ("{v} pp", "{v} p.p."),
    "sahm_triggered": ("(triggered)", "(scattato)"),
    "sahm_below": ("(below 0.5)", "(sotto 0,5)"),

    # ---------------------------------------------------- 05 inflazione attesa
    "s5_cap": (
        "<b>Nominal yield = real yield + expected inflation.</b> Subtracting the yield on inflation-protected "
        "Treasuries (TIPS) from the yield on regular Treasuries gives the market's <b>breakeven inflation</b>. "
        "The <b>5y5y forward</b> is expected inflation from year 5 to year 10, computed as 2 × BE10 − BE5. "
        "Central banks watch it to judge whether expectations are anchored near the 2% target. "
        "The 10-year breakeven bottomed at {low}% in {date}, during the financial crisis, when markets priced "
        "in deflation risk.",
        "<b>Rendimento nominale = rendimento reale + inflazione attesa.</b> Sottraendo al rendimento dei Treasury "
        "ordinari quello dei Treasury indicizzati all'inflazione (TIPS) si ottiene l'<b>inflazione breakeven</b> "
        "implicita nel mercato. Il <b>5y5y forward</b> è l'inflazione attesa dal quinto al decimo anno, calcolata "
        "come 2 × BE10 − BE5: le banche centrali lo osservano per capire se le attese restano ancorate vicino "
        "all'obiettivo del 2%. Il breakeven a 10 anni ha toccato il minimo di {low}% ({date}), durante la crisi "
        "finanziaria, quando il mercato scontava il rischio di deflazione."),
    "be5": ("5Y breakeven", "Breakeven 5Y"),
    "be10": ("10Y breakeven", "Breakeven 10Y"),
    "fwd": ("5y5y forward", "5y5y forward"),
    "target2": ("2% target", "Obiettivo 2%"),
    "per_year": ("% per year", "% annuo"),
    "real_yield": ("Real yield", "Rendimento reale"),
    "exp_infl": ("Expected inflation", "Inflazione attesa"),
    "nominal10_x": ("10Y nominal", "10Y nominale"),
    "st_nominal10": ("10Y nominal", "10Y nominale"),
    "st_real10": ("= 10Y real (TIPS)", "= 10Y reale (TIPS)"),
    "st_be10": ("+ 10Y breakeven", "+ breakeven 10Y"),
    "st_be5": ("5Y breakeven", "breakeven 5Y"),
    "st_fwd": ("5y5y forward", "5y5y forward"),
    "infl_note": (
        "<b>Caveat.</b> Breakeven is not a pure inflation forecast: it also contains an inflation risk premium and "
        "a liquidity premium, because TIPS trade less than regular Treasuries. It is best read as a market-implied "
        "measure and a trend, not an exact number. The series starts in {year}.",
        "<b>Attenzione.</b> Il breakeven non è una previsione pura dell'inflazione: contiene anche un premio per "
        "il rischio inflazione e un premio di liquidità, perché i TIPS si scambiano meno dei Treasury ordinari. "
        "Va letto come misura implicita nel mercato e come tendenza, non come numero esatto. "
        "La serie parte dal {year}."),

    # ------------------------------------------------------- 06 Europa e Italia
    "s6_cap": (
        "Government bond yields in the euro area moved together after the euro was introduced in 1999, then drifted "
        "apart in the sovereign debt crisis. The <b>BTP-Bund spread</b> is the extra yield Italy pays over Germany "
        "on 10-year bonds: it measures how much more risk the market sees in lending to Italy than to Germany. "
        "It peaked at {pre_peak} pp in {pre_date}, before the euro, and at {post_peak} pp in {post_date} since "
        "the euro. In July 2012 the ECB president said the bank would do “whatever it takes” to preserve the "
        "euro, and spreads fell. In {last_date} it stood at {now} pp.",
        "I rendimenti dei titoli di Stato dell'area euro si sono mossi insieme dopo l'introduzione dell'euro nel "
        "1999, poi si sono allontanati durante la crisi del debito sovrano. Lo <b>spread BTP-Bund</b> è il "
        "rendimento in più che l'Italia paga rispetto alla Germania sui titoli a 10 anni: misura quanto più "
        "rischio il mercato vede nel prestare all'Italia rispetto alla Germania. Ha toccato {pre_peak} punti "
        "percentuali ({pre_date}), prima dell'euro, e {post_peak} ({post_date}) dall'introduzione dell'euro. "
        "A luglio 2012 il presidente della BCE disse che la banca avrebbe fatto “whatever it takes” per "
        "preservare l'euro, e gli spread scesero. L'ultimo dato ({last_date}) è {now} punti percentuali."),
    "eu_de": ("Germany 10Y (Bund)", "Germania 10Y (Bund)"),
    "eu_it": ("Italy 10Y (BTP)", "Italia 10Y (BTP)"),
    "eu_us": ("United States 10Y", "Stati Uniti 10Y"),
    "eu_spread_it": ("Italy (BTP-Bund)", "Italia (BTP-Bund)"),
    "eu_spread_es": ("Spain", "Spagna"),
    "eu_spread_fr": ("France", "Francia"),
    "eu_spread_y": ("spread vs Bund, pp", "spread vs Bund, p.p."),
    "ev_euro": ("Euro introduced", "Introduzione dell'euro"),
    "ev_whatever": ("ECB: “whatever it takes”", "BCE: “whatever it takes”"),
    "eu_term_us": ("United States", "Stati Uniti"),
    "eu_term_de": ("Germany / euro area", "Germania / area euro"),
    "eu_slope_y": ("10Y minus 3M, pp", "10Y meno 3M, p.p."),
    "st_it_de": ("BTP-Bund", "BTP-Bund"),
    "st_es_de": ("Spain-Bund", "Spagna-Bund"),
    "st_fr_de": ("France-Bund", "Francia-Bund"),
    "st_term_us": ("U.S. slope", "pendenza USA"),
    "st_term_de": ("German slope", "pendenza Germania"),
    "eu_note": (
        "<b>Source and limits.</b> Monthly averages from the OECD, via FRED. The latest month differs by country "
        "(Italy ends in {it_end}). Short rates for Germany are 3-month interbank rates (the euro-area rate after "
        "1999), not Treasury bills, so the two slopes are comparable in direction but not exactly in level.",
        "<b>Fonte e limiti.</b> Medie mensili OCSE, tramite FRED. L'ultimo mese cambia da paese a paese (per "
        "l'Italia l'ultimo dato è {it_end}). I tassi a breve della Germania sono tassi interbancari a 3 mesi "
        "(dal 1999 il tasso dell'area euro), non rendimenti dei titoli di Stato a breve: le due pendenze sono "
        "confrontabili nella direzione, non esattamente nel livello."),

    # ------------------------------------------------------------ 07 confronto
    "s7_title": ("Compare two days", "Confronta due giorni"),
    "s7_cap": ("Pick any two dates. Default: the deepest inversion against the latest data.",
               "Scegli due date qualsiasi. Predefinito: l'inversione più profonda contro i dati più recenti."),
    "date_a": ("Date A", "Data A"),
    "date_b": ("Date B", "Data B"),

    # ------------------------------------------------------------ 08 Nelson-Siegel
    "s8_title": ("A whole curve from four numbers", "Un'intera curva con quattro numeri"),
    "s8_cap": (
        "The Nelson-Siegel model describes a yield curve with four parameters: <b>level</b> (long-run rate), "
        "<b>slope</b> (short rates against long rates), <b>curvature</b> (medium-term hump) and <b>tau</b> (where "
        "the hump sits, in years). It is fitted by least squares to the ten maturities of the chosen day.",
        "Il modello di Nelson-Siegel descrive una curva dei rendimenti con quattro parametri: <b>livello</b> "
        "(tasso di lungo periodo), <b>pendenza</b> (tassi a breve rispetto a quelli a lungo), <b>curvatura</b> "
        "(la gobba a medio termine) e <b>tau</b> (dove si trova la gobba, in anni). Si adatta ai dieci vertici "
        "della curva del giorno scelto con i minimi quadrati."),
    "day": ("Day", "Giorno"),
    "ns_model": ("Model", "Modello"),
    "ns_market": ("Market yields", "Rendimenti di mercato"),
    "st_day": ("day", "giorno"),
    "st_level": ("level", "livello"),
    "st_slope": ("slope", "pendenza"),
    "st_curvature": ("curvature", "curvatura"),
    "st_tau": ("tau", "tau"),
    "st_rmse": ("rmse", "rmse"),
    "fit_failed": ("The model could not be fitted to the yields of this day.",
                   "Il modello non è riuscito ad adattarsi ai rendimenti di questo giorno."),
    "y_unit": ("{v} y", "{v} anni"),

    # ------------------------------------------------------------ 09 metodo
    "exp_data": ("Data and SQL", "Dati e SQL"),
    "data_text": (
        "- **Yield curve**: daily par yield curve rates, U.S. Department of the Treasury (1990 to today).\n"
        "- **Real yields**: Treasury daily real yield curve (TIPS), 5 to 30 years. Breakevens are available from 2006.\n"
        "- **Macro series**: FRED, Federal Reserve Bank of St. Louis: federal funds rate (FEDFUNDS), CPI "
        "(CPIAUCSL), unemployment rate (UNRATE), the NBER recession indicator (USREC) and, for the recession "
        "model, the monthly 10-year (GS10) and 3-month (TB3MS) yields since 1960.\n"
        "- **Europe**: OECD long-term government bond yields and 3-month interbank rates, via FRED.\n"
        "- Everything is stored in SQLite and queried with SQL. The spread chart comes from this query:",
        "- **Curva dei rendimenti**: par yield curve giornaliera del Dipartimento del Tesoro USA (dal 1990 a oggi).\n"
        "- **Rendimenti reali**: curva reale giornaliera del Tesoro (TIPS), da 5 a 30 anni. I breakeven sono "
        "disponibili dal 2006.\n"
        "- **Serie macro**: FRED, Federal Reserve Bank di St. Louis: tasso sui Fed funds (FEDFUNDS), CPI "
        "(CPIAUCSL), tasso di disoccupazione (UNRATE), indicatore di recessione NBER (USREC) e, per il modello "
        "di recessione, i rendimenti mensili a 10 anni (GS10) e a 3 mesi (TB3MS) dal 1960.\n"
        "- **Europa**: rendimenti dei titoli di Stato a lungo termine e tassi interbancari a 3 mesi dell'OCSE, "
        "tramite FRED.\n"
        "- Tutto è salvato in SQLite e interrogato con SQL. Il grafico dello spread nasce da questa query:"),
    "exp_limits": ("Limitations", "Limiti"),
    "limits_text": (
        "- The 20-year yield does not exist before 1993: earlier values are interpolated between 10 and 30 years.\n"
        "- Thresholds: below 0 inverted, 0 to 0.25 pp flat, above 0.25 pp normal. The 0.25 is a choice made "
        "for this project.\n"
        "- The recession model is estimated in-sample on few recessions, with overlapping windows. It is a "
        "description of the data, not a forecast.\n"
        "- Breakeven inflation includes risk and liquidity premia.\n"
        "- European series are monthly averages and end at different dates.",
        "- Il rendimento a 20 anni non esiste prima del 1993: i valori precedenti sono interpolati tra 10 e 30 anni.\n"
        "- Soglie: sotto 0 invertita, da 0 a 0,25 p.p. piatta, sopra 0,25 p.p. normale. Lo 0,25 è una scelta fatta "
        "per questo progetto.\n"
        "- Il modello di recessione è stimato sugli stessi dati, su poche recessioni e con finestre sovrapposte. "
        "Descrive i dati, non è una previsione.\n"
        "- L'inflazione breakeven include premi per il rischio e per la liquidità.\n"
        "- Le serie europee sono medie mensili e finiscono in date diverse."),

    # --------------------------------------------------------- chi sono e piè di pagina
    "about_title": ("About", "Chi sono"),
    "about_link": ("Connect on LinkedIn", "Contattami su LinkedIn"),
    "footer": (
        "Data: U.S. Department of the Treasury; FRED, Federal Reserve Bank of St. Louis; OECD; NBER. "
        "Python, SQLite, pandas, SciPy, Plotly, Streamlit. Educational project, not investment advice.",
        "Dati: U.S. Department of the Treasury; FRED, Federal Reserve Bank di St. Louis; OCSE; NBER. "
        "Python, SQLite, pandas, SciPy, Plotly, Streamlit. Progetto didattico, non è consulenza finanziaria."),
    "loading": ("Loading Treasury and macro data...", "Carico i dati del Tesoro e i dati macro..."),
}


def language_from_header(header: str) -> str:
    """Sceglie 'it' o 'en' dall'intestazione Accept-Language del browser.

    Il browser elenca le lingue preferite con un peso (q) da 0 a 1, per esempio
    "it-IT,it;q=0.9,en;q=0.8". Si guarda la lingua col peso più alto (a parità, la prima):
    italiano se è italiano, inglese in tutti gli altri casi (compresa un'intestazione vuota).
    """
    best_lang, best_q = "en", -1.0
    for part in (header or "").split(","):
        tag, _, params = part.strip().partition(";")
        if not tag:
            continue
        q = 1.0
        if params.strip().startswith("q="):
            try:
                q = float(params.strip()[2:])
            except ValueError:
                q = 0.0
        if q > best_q:
            best_q = q
            best_lang = "it" if tag.strip().lower().split("-")[0] == "it" else "en"
    return best_lang


def translator(lang: str):
    """Restituisce la funzione t(chiave, **valori) per la lingua scelta ('en' o 'it')."""
    index = 1 if lang == "it" else 0

    def t(key: str, **values) -> str:
        text = STR[key][index]
        return text.format(**values) if values else text

    return t
