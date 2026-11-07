# Legacy vertical software owned by roll-up acquirers and bootstrapped-SaaS funds: "clone and improve" opportunities for a US founder (as of 7 Nov 2026)

**Method and provenance.** Fetched 2026-11-07 unless marked otherwise. I used three kinds of source:
- **Portfolio pages**, read through each acquirer's public WordPress API where available.
- **Capterra pages**: category pages and product review pages. I parsed ratings, review counts and review dates from the page text.
- **Latka profiles**. Latka figures are third-party estimates or self-reported. They are labelled "Latka (est.)" with the date Latka shows.

Further notes:
- **Review quotes** are copied from Capterra with the review date. Capterra reviews are user-submitted, and many are old. The date shows how old each one is.
- **Vendor claims** (customer counts, "leader" language) are labelled **[vendor]**.
- **Search fallback.** WebSearch was used until the session's shared search budget ran out. After that I only fetched known URLs directly. Bing was not used once the budget was gone.
- **"Via search summary"** marks a fact taken from a search-result summary whose page I did not fetch myself.
- **Unreachable sources:** Calm Company Fund (TLS error), Earnest Capital (403), Perseus (502), Lumine (connection reset), Banyan (no portfolio page; /portfolio returned 404), Harris (business-list URLs 404), Vela (portfolio renders client-side, so no entries were captured), Census CBP API (now requires a key). These are gaps, not "no data".

**Already-assessed ideas excluded per brief:** coach/practitioner booking and e-sign; realtor tools; community newsletters; church live translation; DROP processors.

---

## Q1. Which roll-up and bootstrapped-fund portfolio entries serve US niches, and which show age or neglect signals?

### Takeaway
I scanned **655 portfolio entries**: all 191 Jonas companies, all 229 Volaris companies (94 tagged North America are tabled), 44 Diversis, 16 visible Valsoft, 21 Tiny, 11 SureSwift and 143 TinySeed.

The roll-ups hold **clusters of several competing products in the same niche**. This is the strongest structural signal of milk-for-cash ownership:
- Jonas owns **5 moving-company systems**, **4 healthcare-foodservice systems**, **5 salon systems**, **3 liquor/wine systems** and **40+ fitness, leisure and private-club systems** (by Jonas's own vertical tags).
- Volaris owns **AGRIS + ExtendAg + Greenstone + AgVision** in grain and ag retail, and **InTempo + Unique Business Systems + Wynne** in rental.
- Valsoft bought **UnionWare + MemberTrak (2025) and UnionTrack (2026)**, three of the named union-software leaders.

Tiny and SureSwift are mostly horizontal or consumer businesses and are not useful targets. TinySeed is a *source of modern challengers* (jewelers, tattoo, kennels, event rental, YMCA front desk, ABA training), not of legacy targets.

### Cited Findings

**Portfolio counts captured**
- Jonas Software lists **191 companies**, each tagged by vertical. Examples: moving-storage, club-management, fitness-leisure-sports, hair-beauty, foodservice, metal-service-centers, camps, marina-management, cinema-management-ticketing, debt-collection-recovery — [Jonas companies](https://jonassoftware.com/our-companies) (read via `/wp-json/wp/v2/companies`).
- Volaris says it "operate[s] businesses in over 40 vertical markets across more than 60 countries" and refers to "275+ companies". Its API returned **229** portfolio records, 94 of them tagged North America or untagged — [Volaris portfolio](https://www.volarisgroup.com/portfolio/).
- Diversis lists **44** current, prior and add-on companies. Examples: Marketron, Fishbowl Inventory, SalesRabbit, RoofLink, Roofle, ServicePower, LTi, AutoAlert — [Diversis portfolio](https://www.diversis.com/?post_type=diversis_portfolio).
- Valsoft's portfolio shows 16 cards before "Load More": UnionTrack, Chamber Nation, MemberLeap, KidKare, Clubspeed, Omnibus, Countfire, Medicalistics and others — [Valsoft portfolio](https://www.valsoftcorp.com/portfolio).
- Tiny says "We own 21 wonderful businesses": Metalab, Serato, Letterboxd, Dribbble, AeroPress, Shopify themes and similar. Only **MediaNet** ("Special education software for Arizona schools") is vertical B2B — [Tiny companies](https://tiny.com/companies).
- SureSwift lists 11 small horizontal products, such as a store locator, PDF data extraction and affiliate software. It also says it is "seeking to acquire profitable property service businesses, including HVAC, fire safety, and maintenance" — [SureSwift portfolio](https://www.sureswiftcapital.com/portfolio).
- TinySeed lists 143 entries from 2019 to Spring 2026. Vertical examples include Gem Logic (jewelers), Inkzup (tattoo shops), Kennel Link (pet-care facilities), RentKit (event rental), Mission Lens ("Help Desk for the YMCA Front Desk"), Sidekick Learning (ABA organizations), EMS SOAP (rescue-transport documentation), Hashio (cannabis ERP), PackemWMS (3PL warehousing) and TOOLTRIBE (contractor tool inventory) — [TinySeed portfolio](https://tinyseed.com/portfolio).

**Same-niche clusters inside one roll-up (roll-up "stacking")**
- **Jonas, moving and storage:** CompuMove, TechMate (FirstMate/LoadMate), Vans, EWS ("North American Moving & Storage market") and QuickQube (office/industrial moving sales) — [Jonas companies](https://jonassoftware.com/our-companies).
- **Jonas, healthcare foodservice:**
  - Computrition was acquired in **2007**, Jonas's first food acquisition.
  - DFM in **2008**: "a software solution for every healthcare dietary operation".
  - Common CENTS in **2009**.
  - MonarqRC is described as "an extension of Computrition".
  - [Jonas food portfolio history](https://jonassoftware.com/history-of-the-jonas-food-portfolio) (Nov 17, 2023); [SEG transaction note](https://softwareequity.com/transactions/constellation-software-tsx-csu-acquires-computrition).
- **Jonas, liquor and wine:** ICS (Wine POS "Vision", acquired 2017), WineFetch (2019) and Orion winery software (2018) — [Jonas food portfolio history](https://jonassoftware.com/history-of-the-jonas-food-portfolio).
- **Jonas, salons:** Shortcuts ("over 14,000 clients worldwide" **[vendor]**), iSalon, GuestVision, Kitomba and WhatSalon — [Jonas companies](https://jonassoftware.com/our-companies).
- **Jonas, fitness and martial arts:** EZFacility, Pike13, ASF Payment Solutions, eFit Financial, Club OS, 97Display (martial arts), Member Solutions (martial arts), MiGym, Volo, Jonas Fitness and others — [Jonas companies](https://jonassoftware.com/our-companies).
- **Volaris, grain and ag:**
  - AGRIS and ExtendAg were bought from John Deere Agri Services in **January 2011** (third-party directory) — [Grain & Feed Equipment profile](https://www.grainfeedequipment.com/profiles/cultura-technologies).
  - Volaris's agri-food page lists AgVision with Greenstone — [Volaris agri-food](https://www.volarisgroup.com/vertical/agri-food).
  - Its portfolio also includes Aeros (egg and poultry), Tibersoft and Solentra — [Volaris portfolio](https://www.volarisgroup.com/portfolio/).
- **Volaris, rental:** Unique Business Systems (AV, construction and medical equipment rental), InTempo ("independent rental operators") and Wynne Systems — [Volaris portfolio](https://www.volarisgroup.com/portfolio/).
- **Valsoft, unions:**
  - UnionWare (founded 1993) and MemberTrak (since 1996) were bought from Togetherwork on **29 Apr 2025** — [Valsoft release](https://www.valsoftcorp.com/news/valsoft-enters-the-association-management-portfolio-with-the-acquisitions-of-unionware-and-membertrak); [Gibson Dunn](https://www.gibsondunn.com/gibson-dunn-advised-togetherwork-holdings-on-its-sale-of-unionware-and-membertrak-to-valsoft-corporation/); [MergerLinks](https://app.mergerlinks.com/transactions/2025-04-29-unionware).
  - UnionTrack (founded 2014, "450+ labor affiliates") was bought via TAG Software Group in 2026 — [Newswire release](https://www.newswire.com/news/valsofts-tag-software-group-strengthens-its-association-management-portfolio). One aggregator dates it **25 Aug 2026** (unconfirmed) — [Dealroom](https://app.dealroom.co/news/note/valsoft-s-tag-software-group-buys-union-software-maker-uniontrack).

**Screened shortlist feed: entries with age or neglect signals (US-relevant SMB niches)**

| Product(s) | Owner | Niche | Age / neglect signal found | Outcome |
|---|---|---|---|---|
| UnionWare (1993), MemberTrak (1996), UnionTrack (2014) | Valsoft | Labor union locals | Three leaders consolidated within ~16 months; few public reviews | **Shortlist S1** |
| ESO Fire RMS (ex-FIREHOUSE Software), Emergency Reporting | ESO | Fire departments | FIREHOUSE rated 2.7★ (18), "runs on old software (FoxPro)"; ER being phased out after ESO's 2021 purchase | **Shortlist S2** |
| ChamberMaster (2004) / GrowthZone; Chamber Nation | GrowthZone (PE: Greenridge→Lead Edge); Valsoft | Chambers of commerce | Forced ChamberMaster→GrowthZone migration; support complaints; $2.9–3.9k/yr list prices | **Shortlist S3** |
| El Dorado, SOFTWater, QuikWater, Banyon; Harris CIS lines | Mixed independents; Harris (CSI) | Small water/sewer utility billing | Most Capterra reviews dated 2016–2022; "fees every time you turn around" | **Shortlist S4** |
| SiteLink, storEDGE, Easy Storage Solutions | Storable (EQT per Latka) | Self-storage | "Sitelink was purchased by Storable and customer ser[vice]…" (2025); forced merchant processing (2021) | **Shortlist S5 (conditional)** |
| SedonaOffice; Cornerstone Billing Solutions | Bold/EverCommerce; Jonas | Alarm/security dealers | Capterra support score 3.3/5; quote: support "still very much a work in progress" after acquisition | **Shortlist S6 (conditional)** |
| Marketron (RadioTraffic, Visual Traffic); WideOrbit | Diversis; Volaris | Radio station traffic and billing | Founded 1969; vendor says stations "traditionally" on-prem; market shrinking | **Shortlist S7 (conditional)** |
| Computrition, DFM, Common CENTS, MonarqRC | Jonas | Hospital and long-term-care dietary | 4 overlapping products held since 2007–2009; no public review data found | **Watch S8** |
| AGRIS, AgVision, Greenstone, ExtendAg | Volaris | Grain elevators and ag retail | 1–2 Capterra reviews each; AgVision 3.0★ (1) | Watch (copyability too low) |
| CompuMove, TechMate, Vans, EWS, QuickQube | Jonas | Movers | Five legacy systems stacked | Kill: SmartMoving, Chariot |
| CampSite, myCAMPapp | Jonas | Summer camps | — | Kill: CampMinder et al. |
| InTempo, UBS, Wynne; Point of Rental | Volaris; independent | Equipment rental | Point of Rental "Declining service" (Mar 2026) | Kill: Booqable, Goodshuffle |
| Artsystems, ArtBinder | Volaris | Art galleries | — | Kill: Artlogic, ArtCloud |
| ConsignPro → SimpleConsign; Ricochet | Consolidated (SimpleConsign) | Consignment/resale | Ricochet processor lock-in, "$100 a day" fine threat (Apr 2026) | Kill: cloud challengers well rated |
| KidKare (Minute Menu, 1993) | Valsoft | CACFP child-care food program | Dec 2025 service complaint | Kill: 4.7★ from 389 reviews |
| PastPerfect | Independent (not a roll-up) | Small museums | "Clunky, on an out-dated platform" (Feb 2020) | Kill: CatalogIt 4.9★ (78), 2026 migrations |
| Caterease | Independent | Caterers | "Would Not Purchase Again" (Oct 2026) | Kill: crowded, well rated |
| Printavo | Inktavo | Screen printers | 60% price-hike complaint (Jul 2022) | Kill: YoPrint, Teesom already absorbing switchers |
| Windward System Five | Volaris | Hardware/farm/rental retail | 3.8★ (189); 1★ reviews 2020/2022 | Kill: general retail POS crowding |
| ICS Wine POS, WineFetch | Jonas | Liquor stores | — | Kill: category dominated by general POS |
| Omniterm; LilYPad POS; Clubspeed | Jonas; Jonas; Valsoft | Cinemas; family entertainment centers | — | Not assessed (no data gathered) |
| Rental Car Manager | Jonas | Independent car rental | — | Not assessed |
| WebRecon, C&R Software, Lean Industries | Jonas | Debt collection | Regulated (FDCPA) | Not assessed: compliance-heavy |
| 4GL, PCI, Metalogic, Jonas Metals USA | Jonas | Metal service centers | ERP-scale | Not assessed: not 1–3-month MVP |

The kill-list rows are sourced in Q3. The full scanned-entry tables follow.

**Full tables of scanned entries (655 reviewed; 520 tabled below)**

#### Appendix A1: Jonas Software (Constellation) — all 191 companies listed on its site (fetched 2026-11-07)
Source: [Jonas Software companies](https://jonassoftware.com/our-companies), via its public WordPress API (`/wp-json/wp/v2/companies`). Descriptions are the vendor's own wording, abridged.

| # | Company | Jonas vertical tag | What it does (abridged) |
|---|---|---|---|
| 1 | Nodum Argentina | government | Nodum Software is a well-known provider of enterprise resource planning solutions in Latin… |
| 2 | Benbria | education | Benbria is a real-time experience management software company that helps organizations capture… |
| 3 | Mine Tech Services (‘MTS’) | mining-industry | MTS is a global provider of digital software solutions for the mining industry, specialising… |
| 4 | APESA Software | financial | ASPEA Software has over 25 years of experience in developing and implementing solutions for… |
| 5 | Aava Software | manufacturing | Aava Software is a leading developer of ERP and MES solutions for the manufacturing and… |
| 6 | GEOCOM | government,healthcare,retail | GEOCOM Uruguay S.A. is a technology company with over 25 years of experience, delivering… |
| 7 | myCAMPapp | camps | A leading parent engagement app in the summer camp industry . As the first application… |
| 8 | MedAdvisor Solutions (ANZ Division) | pharmacy | MedAdvisor Solutions ANZ Division is a global healthcare company dedicated to improving… |
| 9 | CAST Group of Companies | media-solutions | CAST is an Emmy award-winning developer of software and hardware solutions for the… |
| 10 | Cornerstone Billing Solutions | security | Cornerstone Billing Solutions is a trusted leader in cloud-based billing and account… |
| 11 | Wheatley Software Solutions | asset-management | Wheatley is a leading provider of specialist software for the UK utilities sector, enabling… |
| 12 | SQiBLE | crm-and-erp-solutions | SQiBLE is a market-leader with a focus in tailored ERP and CRM integration solutions to… |
| 13 | Imaginet Ltd | digital-marketing | Imaginet is a digital solutions company that helps businesses transform through services like… |
| 14 | Kobas | foodservice | Kobas is a UK-based, all-in-one hospitality management platform for restaurants, bars, and… |
| 15 | Blackbox Control | fleet-management | BlackBox Control is a leading provider of fleet management solutions, delivering real-time… |
| 16 | Intersoft Systems | payment-processing | InterSoft Systems has been driving innovation in lending & investment software for over 40… |
| 17 | TurnPoint Software | healthcare | Turnpoint Software is a trusted provider of software solutions designed for aged care and… |
| 18 | Ariane Systems | hotel-resorts | With over 20 years of expertise and over 3,000 installations across 29 countries, Ariane is… |
| 19 | Aptech | hotel-resorts | Aptech is a pioneer financial software technology specifically built for the hospitality… |
| 20 | OnTap Data | food-wine-retail | OnTap Data is a leading provider of data analytics and insights solutions tailored for the… |
| 21 | Rock Solid Knowledge | security | Rock Solid Knowledge is a market leader in the delivery of Identity and Access Management ,… |
| 22 | Tracx Systems Ltd. | transportation-logistics | Tracx is a dynamic Transportation Management System (TMS) that streamlines and optimizes… |
| 23 | Volanté | foodservice | Volanté Systems is a leading technology company specializing in comprehensive and scalable… |
| 24 | Healthpoint | healthcare | Healthpoint connects more people to better healthcare through simple, excellent digital… |
| 25 | MachineMax | construction | MachineMax is a leading provider of operational efficiency software for the mining and… |
| 26 | SpringFour | debt-collection-recovery | SpringFour is the first-of-its-kind, leading financial health fintech that empowers banks,… |
| 27 | B4Checkin | hotel-resorts | B4Checkin’s cloud-based tools for the hospitality industry create exceptional experiences for… |
| 28 | My PT Hub | fitness-leisure-sports | My PT Hub is an online web application, enabling fitness professionals to manage their clients… |
| 29 | ClubWise | fitness-leisure-sports | ClubWise integrates Club Management Software, Direct Debit Collection Services, Marketing,… |
| 30 | Carlson Marketing Solutions | loyalty | Carlson Marketing Solutions is a leading loyalty solutions platform that efficiently manages… |
| 31 | Teachworks | education | Teachworks was founded in 2014 to provide education businesses of all sizes with exceptional… |
| 32 | MWC Partners | retail | MWC Partners is a specialist in retail payments technology with expertise in the integration… |
| 33 | Dataflow Events | event-management | Dataflow Events is a leading provider of customized delegate management solutions for the… |
| 34 | Ezy Systems | wine-and-spirits | Ezy Systems builds market-leading ERP software tailored to the unique needs of wineries, wine… |
| 35 | Kahootz | government | Available since 2003, the award-winning cloud collaboration system Kahootz is now used by… |
| 36 | Club OS | fitness-leisure-sports | Club OS is a comprehensive sales engagement and marketing automation platform designed… |
| 37 | ASF Payment Solutions | fitness-leisure-sports | ASF Payment Solutions provides gym management software, payment processing solutions, and… |
| 38 | Intelligent Counting | attractions | Intelligent Counting is the leading supplier of people management solutions and services for… |
| 39 | Amisoft | legal | Amisoft is a leading provider of digital legal processing solutions for the judicial sector in… |
| 40 | Vanson Technology Services | loyalty | With over 25 years of expertise, Vanson Technology Services is at the forefront of developing… |
| 41 | Béker-Soft | radiology-laboratory-information-systems | Béker-Soft Informatika Kft. is a leading provider and developer of complete software solutions… |
| 42 | Tangerine Global | media-solutions | Tangerine Global is a Media Solutions and Network Services Provider for both commercial and… |
| 43 | Rental Car Manager | car-rental-management | Rental Car Manager offers mission critical software for car rental businesses, including… |
| 44 | Corum Health | pharmacy | Corum Health is a leading provider of innovative pharmacy management software for pharmacies… |
| 45 | Nodum Software | government | Nodum Software is a well-known provider of enterprise resource planning solutions in Latin… |
| 46 | 4GL Solutions | metal-service-centers | 4GL is a leading provider of customized ERP metal center software, specifically designed for… |
| 47 | GSoft | food-wine-retail | GSoft was founded in 1999 and is focused on electronic invoicing, payment solutions and point… |
| 48 | Theta Technologies Pty Ltd. | meat-processing | Through its innovative platform InformationLeader, Theta Technologies provides quality… |
| 49 | WebRecon | debt-collection-recovery | WebRecon is a leading provider of litigation tracking and consumer risk management solutions… |
| 50 | Uruware | government | Uruware has been dedicated to building transactional solutions for electronic data interchange… |
| 51 | Hellenic Systems Ltd. | meat-processing | Hellenic Systems Ltd. provides integrated hardware & software solutions for the food… |
| 52 | PVX Plus Technologies Ltd. | developer-tools | PVX Plus Technologies Ltd. provides a powerful collection of feature rich and intuitive… |
| 53 | Hessel Group Ltd | moving-storage | Hessel is a leading provider of global mobility management solutions and services. With a… |
| 54 | Data Basics Inc | construction | Data-Basics Inc. is a leading provider of field service and construction management software… |
| 55 | SupportAbility | government | SupportAbility provides leading client management, operations and compliance software… |
| 56 | Seiki Systems | manufacturing | Seiki is a leading supplier of production control and manufacturing execution software to… |
| 57 | Huntington Business Systems (“HBS”) | time-attendance | HBS is a leading provider of Time and Attendance Management Software for small, medium, and… |
| 58 | Qwantec Ingenieria Limitada (“Qwantec”) | time-attendance | Qwantec is a market leading Chilean and Peruvian software provider of time & attendance… |
| 59 | VetlinkPRO | veterinarian-practice-management | VetlinkPRO is the provider of a modern Practice Management Software for Veterinarian Practices… |
| 60 | Datalogic Software | government | Datalogic Software has been providing its solutions and services in software development and… |
| 61 | Vizergy | digital-marketing | For nearly 25 years, Vizergy has served the hospitality industry with leading marketing… |
| 62 | Brainbase | product-licensing | Brainbase is a modern, end-to-end licensing management platform that brings together the… |
| 63 | McCarthys | meat-processing | McCarthys’ Uniworks product provides industry specific software solutions that are fully… |
| 64 | Halo Leisure Enterprise Ltd. | asset-management | WAM software is an interactive solution for asset management, maintenance scheduling and… |
| 65 | Infoscience Limited | auctions | Infoscience works with auctioneers & livestock marketeers to provide a back-office software… |
| 66 | CompuMove Systems Corporation | moving-storage | CompuMove’s powerful move management software seamlessly brings together all of the different… |
| 67 | medQ Inc. | radiology-laboratory-information-systems | medQ provides highly configurable and customizable imaging workflow software, providing… |
| 68 | Power2SMS Limited | sms | Power2SMS Limited is a platform of communication solutions that works with businesses to… |
| 69 | LilYPad POS | fitness-leisure-sports | LilYPad provides a web-based point of sale system to family entertainment centers (FEC). It is… |
| 70 | RBRO Solutions Inc. | legal | A leading web-based document and email management provider for the legal and financial… |
| 71 | Lean Industries | debt-collection-recovery | Lean Industries is focused exclusively on delivering solutions for disputed… |
| 72 | K2B | government | K2B is a Government & Private Sector ERP solution, allowing every organization and industry to… |
| 73 | GeneXus Consulting | government | GeneXus Consulting is the company that provides services to assist organizations achieve their… |
| 74 | AMT Sybex | asset-management | AMT Sybex is the leading provider of critical utilities and infrastructure software in the UK.… |
| 75 | Seekom Limited | hotel-resorts | Seekom is a market leader for providing a full in-house and channel management platform for… |
| 76 | MySkillChart | fitness-leisure-sports | MySkillChart’s mission is to finally bring to coaches, teachers, and instructors a real… |
| 77 | Newline ASP | auctions | Newline ASP specializes in the design, supply and support of auction software to the livestock… |
| 78 | WM-data Deutschland GmbH | manufacturing | WM-data Deutschland GmbH was found from IT department of Feldmühle AG during some… |
| 79 | C&R Software | debt-collection-recovery | For organizations collecting and recovering debt, it begins with having one system managing… |
| 80 | Dynamiq | risk-management | Dynamiq is an industry leader in creating a safe and resilient world. The experience,… |
| 81 | Invotech | fitness-leisure-sports | As the leading supplier of leisure management software systems, Invotech are revolutionizing… |
| 82 | Omniterm | cinema-management-ticketing | Omniterm delivers a complete and affordable theatre management solution that includes ticket… |
| 83 | UniOne | fitness-leisure-sports | UniOne is an Australian software company that provides student activity management for… |
| 84 | Easit AB | case-management | Easit is a Swedish software company that provides case management, data management software… |
| 85 | C-SAM | asset-management | C-SAM is a leading solutions provider to the oil and gas; subsea and maritime, and related… |
| 86 | Bluestar Software | emergency-services | Bluestar is a leading solutions provider to Police Forces and related agencies, delivering… |
| 87 | RewardOps | loyalty | RewardOps is an engagement commerce platform creating positive disruption in the rewards… |
| 88 | Infomax | long-term-care | InfoMax is an industry leader focused on the Canadian long-term care industry, as well as the… |
| 89 | Ineo | corporate-mobility | Ineo offers, offering comprehensive global mobility management software, outsourced mobility… |
| 90 | PowerTrack | construction | PowerTrack is a leading provider of mobile time tracking software, offering mobile… |
| 91 | Contronics | medical-technology | Contronics is a leading provider of laboratory monitoring system products and software,… |
| 92 | MetricsFirst | club-management | MetricsFirst was born in 2015 with the goal of connecting data from a clubs myriad of… |
| 93 | Jonas Premier | construction | The number one priority for Premier is to design standard & intuitive screens that allow you… |
| 94 | Constellation Payments | payment-processing | Constellation Payments is a leading global gateway and merchant services provider with special… |
| 95 | Monarq RC | foodservice | MonarqRC is an extension of Computrition, the longtime leader in healthcare foodservice… |
| 96 | DFM | foodservice | DFM offers a software solution for every healthcare dietary operation – small or large,… |
| 97 | QuickQube | moving-storage | QuickQube is an automated sales process system designed for the office and industrial moving… |
| 98 | Club Caddie | club-management | Club Caddie’s comprehensive core system allows users to manage all aspects of their properties… |
| 99 | Smyth Systems | club-management | Smyth Systems specializes in providing superior software, services and support that empower… |
| 100 | Pulse Club Computers | fitness-leisure-sports | Pulse Club has grown to become the leading provider to the Australian golf and club industry.… |
| 101 | Achiga | hotel-resorts | Achiga’s Live Enterprise digital experience management solution provides an enterprise level… |
| 102 | SpaSoft | hotel-resorts | Spa Soft is an industry leading, all-in-one spa management solution, trusted by over 65% of… |
| 103 | Volo Innovations | fitness-leisure-sports | A provider of online scheduling and business management applications to the health and fitness… |
| 104 | Jonas Leisure | fitness-leisure-sports | At Jonas Leisure we aim to deliver software that provides real and lasting value for fitness,… |
| 105 | ClubHouse Online | club-management | ClubHouse Online website is custom designed and can be fully responsive, allowing your members… |
| 106 | Orion | food-wine-retail,wine-and-spirits | Orion offers solutions to help wineries manage their operational information, enabling them to… |
| 107 | Wine POS by ICS | food-wine-retail,wine-and-spirits | ICS is a leading provider of software solutions to the US beer, liquor and wine retail market.… |
| 108 | WineFetch | food-wine-retail,wine-and-spirits | WineFetch provides cutting-edge e-commerce websites and apps for wine and spirit stores that… |
| 109 | Happen | managed-print-services | Happen was established to fill a growing need in the market for a comprehensive accounting and… |
| 110 | Greycon | manufacturing | Greycon is the world’s leading provider of production planning, scheduling, forecasting and… |
| 111 | Pacsoft | marina-management | Pacsoft is a New Zealand-based company with 20 years’ experience providing software for… |
| 112 | HavenStar | marina-management | HavenStar is an enterprise Marina Management System for managing multiple sites, and also… |
| 113 | BEC Legal Systems | legal | BEC develops enterprise solutions to help law firms organize and streamline their day-to-day… |
| 114 | Chameleon Software | case-management | Chameleon’s flagship product, Case Manager , is the leading case management system for the… |
| 115 | Resolve Software | case-management | Resolve is a leading provider of Enterprise Case Management Software and solutions for… |
| 116 | PayGate | payment-processing | PayGate is a payment processing software business which provides data validation and services… |
| 117 | MyMediaBox | product-licensing | MyMediaBox is a leading provider of affordable, intuitive and flexible hosted, online business… |
| 118 | TechMate International | moving-storage | TechMate provides comprehensive moving storage solutions with leading products such as… |
| 119 | Vans | moving-storage | The Vans solution provides fully integrated applications designed to assist your Moving and… |
| 120 | EWS | moving-storage | EWS is a leading provider of software solutions and services to the North American Moving &… |
| 121 | PCI Systems | metal-service-centers | PCI provide integrated IT solutions that have been specifically designed and developed by us… |
| 122 | Metalogic | metal-service-centers | Metalogic is a leading provider of management software solutions for the Metal Stockholding… |
| 123 | Jonas Metals USA | metal-service-centers | Supplying ERP systems to North American Metal Service Centers through its Metal Focused ERP… |
| 124 | LRS Health | radiology-laboratory-information-systems | LRS Health is a leading developer of management, billing and communication software for the… |
| 125 | Kestral | radiology-laboratory-information-systems | For more than twenty years, Kestral has specialised in providing intuitive, best of breed,… |
| 126 | Critical Impact | digital-marketing | Critical Impact is a Virginia-based company with over 10 years’ experience providing email… |
| 127 | SignMeUp | event-management | SignMeUp is a leading provider of web-based software and services for event registration,… |
| 128 | Jonas Event Technology | event-management | Jonas Event Technology is a leading registration services and events software company that… |
| 129 | 123Signup | event-management | 123Signup’s solutions are transforming the way events and member organizations are managed.… |
| 130 | CampSite | camps | CampSite is an industry leader providing an all-in-one camp management software to summer… |
| 131 | Retail & Sports Systems | food-wine-retail | R&SS offers a true Omni-channel solution from a single supplier you can trust — allowing… |
| 132 | Uniware | food-wine-retail | Uniware is the leading, proven provider of EPoS systems for the hospitality and retail… |
| 133 | ePOS Group Ltd | food-wine-retail | ePOS Group Ltd. (“ePOS”) is a leading provider of Software solutions in the UK retail market,… |
| 134 | Fashion Master | food-wine-retail | Fashion Master is a leading provider of Enterprise Software solutions in the UK retail market,… |
| 135 | Cunninghams EPOS Group | food-wine-retail | For the past 40 years, Cunninghams EPOS Group have been a leading provider of point of sale… |
| 136 | MCR | food-wine-retail | MCR provides hospitality, catering and leisure organizations with enterprise management… |
| 137 | ProviderSoft | childhood-development | ProviderSoft’s comprehensive core system allows users to monitor all aspects of their business… |
| 138 | MINTclass | education | MINTclass transforms educational institutions and educators by utilizing student information… |
| 139 | XLerant | budgeting | XLerant provides cloud-based budgeting, forecasting and reporting solutions designed with easy… |
| 140 | InReach LLC | continuing-education | InReach LLC “InReach” is a leading player in the Continuing Education vertical in the US, with… |
| 141 | EasyTrace | education | EasyTrace is the recognised market leader in the provision of “Smart” card and biometric… |
| 142 | Gladstone Education | education | Gladstone Education specializes in providing “Smart School Solutions” which include Identity… |
| 143 | Tucasi | education | Tucasi creates software systems that help schools manage income more effectively. Their… |
| 144 | CRB Cunninghams | education | CRB Cunninghams is a leading provider of cashless catering solutions to the UK education… |
| 145 | Outbound Software | attractions | Outbound Software LLC is an up and coming provider of business and process management… |
| 146 | Centaman | attractions | CENTAMAN is a market leader in computer systems for the Tourism, Leisure and Attractions… |
| 147 | GuestVision | hair-beauty | GuestVision is one of a few salon software packages flexible enough to span the breadth of the… |
| 148 | WhatSalon | hair-beauty | WhatSalon is a mobile market place that shows you the hottest salons that are closest to you.… |
| 149 | Kitomba | hair-beauty | Kitomba is a leading provider of Software and Service solutions to the Salon and Spa industry.… |
| 150 | iSalon | hair-beauty | iSalon is a leading provider of Salon Software and Services to businesses throughout the… |
| 151 | Shortcuts | hair-beauty | Shortcuts is the leading global standard in smart salon technology, working with over 14,000… |
| 152 | Leonardo | hotel-resorts | Leonardo provides hotels, management companies and travel websites with robust solutions to… |
| 153 | BookAssist | hotel-resorts | BookAssist partners with hotels to build their brand online, drive direct business to their… |
| 154 | Jonas Chorum | hotel-resorts | Jonas Chorum is a leading cloud services technology company delivering hotel property… |
| 155 | Springer Miller Systems | hotel-resorts | Founded in 1984, Springer Miller Systems is a globally recognized leader in the field of fully… |
| 156 | Impos | food-wine-retail | Impos Solutions is designed to suit a range of hospitality business types, from cafes and… |
| 157 | ITWERCS | food-wine-retail | ITWERCS was founded in 2016 in Marietta, Georgia, USA. Their cloud platform was originally… |
| 158 | Common CENTS Solutions | foodservice | Common CENTS Solutions has been providing innovative hospitality solutions to the healthcare… |
| 159 | Computrition | foodservice | Computrition, Inc. provides innovative foodservice and healthcare software solutions. Since… |
| 160 | Green 4 | attractions,fitness-leisure-sports | Green 4 specialises in providing sports and leisure businesses with a CRM driven approach to… |
| 161 | Ez-Runner | fitness-leisure-sports | Ez-Runner’s leading software solution can be tailored to match the exact needs of the business… |
| 162 | Pike13 | fitness-leisure-sports | Pike13 is a new point of service mobile app that not only takes payments but also helps… |
| 163 | InnoSoft | fitness-leisure-sports | InnoSoft is the leading provider of campus recreation management software to the University… |
| 164 | MiGym | fitness-leisure-sports | MiGym is a leading provider of custom-branded mobile apps for the fitness industry. Features… |
| 165 | Nutrition Complete | fitness-leisure-sports | Nutrition Complete is a leading provider of nutrition management software. Their applications… |
| 166 | CAP2 | fitness-leisure-sports | Cap2 Solutions are the happy people behind the helpful software; CoursePro. CoursePro is the… |
| 167 | The Retention People | fitness-leisure-sports | The Retention People are the leading researchers in leisure customer retention. We use this… |
| 168 | SDA | fitness-leisure-sports | SDA Software specializes in providing web-based membership, management, CRM, booking and… |
| 169 | Xn Leisure | fitness-leisure-sports | Xn Leisure is a leading provider of Leisure Management Solutions (LMS) in the UK with over… |
| 170 | Gladstone Health & Leisure | fitness-leisure-sports | Gladstone aims to become recognised as the leading international provider of innovative… |
| 171 | Retention Management | fitness-leisure-sports | Retention Management specializes in technology solutions that help fitness operators track,… |
| 172 | Frontline Solutions | fitness-leisure-sports | Frontline Solutions grew out of the need to bring together multiple areas of business… |
| 173 | eFit Financial | fitness-leisure-sports | eFit Financial offers club management software and full-service billing for health clubs,… |
| 174 | EZFacility | fitness-leisure-sports | EZFacility specializes in software solutions that streamline the daily operations and… |
| 175 | 97Display | fitness-leisure-sports | 97Display is a leading provider of software and services to the Martial Arts industry. Their… |
| 176 | Member Solutions | fitness-leisure-sports | Member Solutions is a SaaS provider specializing in martial arts and fitness businesses.… |
| 177 | Jonas Fitness | fitness-leisure-sports | At Jonas Fitness, our vision is to be the branded global leader in fitness software and… |
| 178 | Automated Integration | construction | Automated Integration is a fully-integrated, enterprise resource planning software solution… |
| 179 | Motion Software | asset-management | Motion is a provider of industry leading software for workforce mobilisation in the areas of… |
| 180 | mJobTime | construction | mJobTime provides customizable, scalable time-tracking software to help businesses improve on… |
| 181 | VMS | construction | VMS has been a leading provider of business management software for contractors since 1984.… |
| 182 | Ascente | construction | Ascente service contractor software is an integrated solution that serves the plumbing, HVAC,… |
| 183 | Jonas Construction | construction | The Jonas Construction package is a comprehensive and fully integrated construction accounting… |
| 184 | Club Systems Africa | club-management | Club Systems Africa provides a full suite of Club Management applications, all of which are… |
| 185 | WebCreative UK | club-management | WebCreative UK is a leading provider of website solutions to clubs throughout the United… |
| 186 | ClubMinder | club-management | ClubMinder has provided solutions to Golf Clubs in the UK for over 10 years helping improve a… |
| 187 | Private Club Network | club-management | The Private Club Network is the leading provider of reciprocal play management for private… |
| 188 | ClubPay | club-management | ClubPay offers best of class solutions for payroll outsourcing, integrated HR management, time… |
| 189 | Clubsystems Group | club-management | clubsystems group is a leading provider of innovative club management software, offering… |
| 190 | MembersFirst | club-management | MembersFirst is an award winning digital agency & software provider for member-based… |
| 191 | Jonas Club Software | club-management | Whether your club is small, large, public or fully private, Jonas Club Software has the right… |

#### Appendix A2: Volaris Group (Constellation) — the 94 North-America-tagged companies out of 229 listed (fetched 2026-11-07)
Source: [Volaris portfolio](https://www.volarisgroup.com/portfolio/), via its public WordPress API (`/wp-json/wp/v2/portfolios`). The other 135 entries are tagged to other regions only and were skipped.

| # | Company | Volaris vertical tag | What it does (abridged) |
|---|---|---|---|
| 1 | LoginRadius Global | security | LoginRadius Global provides cloud-based customer identity and access management (CIAM)… |
| 2 | Accent Technologies | compliance | A provider of enterprise sales enablement software designed for regulated and… |
| 3 | Sureview Systems | security | SureView is a leading PSIM provider in North America, delivering scalable, hardware-agnostic… |
| 4 | Symplicity | education | Symplicity sells SaaS-based solutions that help manage all aspects of a student’s life on… |
| 5 | BIG Consulting | agri-food | BIG Consulting is a team of business intelligence, data analytics, finance, and agriculture… |
| 6 | Alpine Testing Solutions | workforce-management | Alpine Testing Solutions Inc. provides expertise and solutions to help organizations create… |
| 7 | AskCody | asset-management-logistics | AskCody develops software that simplifies meeting booking, resource scheduling, visitor… |
| 8 | Trellint | people-transportation | Trellint provides comprehensive parking and curbside management solutions that make the curb… |
| 9 | Squirrel Systems | foodservice-hospitality | Squirrel provides point-of-sale solutions to the hospitality industry. Squirrel revolutionized… |
| 10 | Parlance | healthcare | Parlance is a leading provider of voice-first communication solutions, known for its… |
| 11 | Elovate | people-transportation | Elovate fosters safer communities through the implementation of innovative, data-driven… |
| 12 | Dassian | compliance | Dassian is a premium provider of SAP Certified Add-ons for complex contract and project… |
| 13 | Husk | healthcare | Husk offers a wellness management platform designed for healthcare providers. Their software… |
| 14 | WideOrbit | (untagged) | WideOrbit is a platform that ties everything together – from programmatic and digital ad sales… |
| 15 | WennSoft | field-service-management | With over 25 years of industry expertise, WennSoft (formerly “Key2Act”), is an innovator in… |
| 16 | Titanium | (untagged) | Titan.ium provides flexible and powerful platforms for telecommunication and government… |
| 17 | Squirrels | education | Squirrels is a world leader in wireless screen mirroring and digital signage software for… |
| 18 | RAF | post-parcel | RAF specializes in AI-driven pattern recognition, intelligent data extraction, and signature… |
| 19 | Multiforce Systems Corporation | fuel | Multiforce Systems is the innovator behind the FuelForce line fuel management hardware and… |
| 20 | FunctionFox | martech | FunctionFox provides timesheet and project management software for marketing, creative, design… |
| 21 | ClickDimensions | martech | ClickDimensions is the technology solution for small to medium businesses (SMBs) that unifies… |
| 22 | TSi Auto Solutions | automotive | Canadian automotive software company specialising in enterprise reporting, performance… |
| 23 | TransLoc | people-transportation | Transloc provides microtransit, on-demand services, and fixed route transportation solutions… |
| 24 | Tomia | (untagged) | TOMIA is an innovator and leader in global monetization solutions. Their software optimizes… |
| 25 | Crosscap | martech | Crosscap provides a retail marketing execution platform for retailers, printers, and… |
| 26 | Bravura Security | security | Bravura Security is the only identity management, privileged access and password management… |
| 27 | Artsystems | arts-culture | Artsystems delivers art management solutions to commercial art galleries, private and… |
| 28 | ArtBinder | arts-culture | ArtBinder is a worldwide leader in collection management solutions for commercial art… |
| 29 | Agronomix Software | agri-food | Agronomix Software provides market-leading, specialist software for the plant breeding,… |
| 30 | Intellicene | security | Intellicene’s mission is to help organizations worldwide harmonize security, business… |
| 31 | Aislelabs | martech,retail,security | Aislelabs provides advanced WiFi location analytics and marketing solutions to large shopping… |
| 32 | Vontas | people-transportation | Vontas helps agencies make public transit the desired mode of transportation in their… |
| 33 | Ubersmith | (untagged) | Ubersmith is a leader in subscription management software for the cloud. Ubersmith provides… |
| 34 | Softchalk | education | SoftChalk’s cloud-based content authoring solution gives educators the ability to create high… |
| 35 | Sansio | healthcare | Sansio provides a point-of-care data management solution that allows you to seamlessly… |
| 36 | ResultsPlus | non-profit | ResultsPlus, a division of Metafile Information Systems, is a nonprofit CRM software for donor… |
| 37 | Oasys | education | Oasys offers an integrated suite of software products that give administrators, educators, and… |
| 38 | MetaViewer | financial-services | MetaViewer, a division of Metafile Information Systems, is a financial software solution that… |
| 39 | Kansys | (untagged) | Kansys Inc. is a provider of modular billing subscription management, event intelligence, and… |
| 40 | ISB | education | ISB is a provider of consulting, administrative services and web-based software solutions to… |
| 41 | Four Js | software-development | Four Js is a global provider of mission-critical low-code / no-code software development… |
| 42 | EnvisionWare | library-management | EnvisionWare is a provider of technology solutions for public libraries. EnvisionWare is a… |
| 43 | Datapro | financial-services | Datapro offers solutions designed to take on the challenges of digital transformation in the… |
| 44 | Curbstone | financial-services | Curbstone is a provider of credit card processing specific to companies on IBM Power Systems. |
| 45 | ASSET Intertech | engineering | ASSET InterTech provides solutions to validate, characterize, test and debug chips and circuit… |
| 46 | AgVision | agri-food | AgVision is a proven leader in developing grain, ag retail, feed, fertilizer and seed… |
| 47 | Unique Business Systems | rental-management | UBS provides rental operations management software for AV, construction, and medical equipment… |
| 48 | Tribute | asset-management-logistics | Tribute provides integrated ERP software solutions to industrial distributors across North… |
| 49 | medaptus | healthcare | Medaptus is a leading provider of revenue cycle improvement, coding automation, and patient… |
| 50 | Go Solutions | education | Go Solutions is a Medicaid claims reimbursement software provider for special education. |
| 51 | Clarity Group | healthcare | Clarity Group provides risk management software and managed services to Healthcare… |
| 52 | Charity Dynamics | non-profit | Charity Dynamics is a leading provider of peer-to-peer (P2P) fundraising technology and… |
| 53 | BiblioCommons | library-management | BiblioCommons builds software that transforms public libraries’ essential online services –… |
| 54 | Windward | retail | Windward Software provides a complete ERP solution for the retail and customer service… |
| 55 | RedHawk | financial-services | Red Hawk provides technology-enabled services delivered by a team of insurance and IT… |
| 56 | Portfolio+ | financial-services | Portfolio+ is an open banking platform that includes software applications for loans,… |
| 57 | Insuresoft | financial-services | Insuresoft’s flagship product, Diamond, is a digital insurance platform comprised of policy,… |
| 58 | FIVE x 5 | supply-chain-inventory-management | FIVE x 5 provides the craft beverage industry with a comprehensive SaaS-based solution that… |
| 59 | Criterions | healthcare | Criterions provides Electronic Health Records and Practice Management software to a wide range… |
| 60 | Covenir | financial-services | Covenir is the leading Property and Casualty business process outsourcing provider with a… |
| 61 | Advantage360 | (untagged) | Advantage 360 is a converged platform providing Tier 3 and 4 emerging markets operators with… |
| 62 | Momentm | people-transportation | Momentm is a dedicated Health & Human Services Transportation software company specializing in… |
| 63 | ASC Automotive | automotive | Leading Dealer Management Software (DMS) provider specialising in multi-OEM dealerships,… |
| 64 | Helm | marine | Helm delivers solutions to address all departments of tug and barge marine operations for… |
| 65 | Function Point | martech | Function Point is a provider of online project management software for agencies and creative… |
| 66 | Aleyant | print-publishing | Aleyant’s automated print software solutions create a solid foundation for growing print media… |
| 67 | WebCheckout | education | WebCheckout provides equipment scheduling and resource management software to the higher… |
| 68 | TransTrack | people-transportation | TransTrack Systems, Inc. provides a web-based business analytics and data management system to… |
| 69 | Tibersoft | agri-food | Tibersoft is a leading provider of SaaS analytics solutions for CPG foodservice providers |
| 70 | CaterTrax | foodservice-hospitality | CaterTrax is a catering management software company primarily serving the non-commercial… |
| 71 | TOPAZ Technologies | healthcare | Topaz provides software solutions for organizations operating in highly regulated research and… |
| 72 | Greenstone | agri-food | Greenstone’s mission is to enable the diversified grain industry and cooperatives to maximize… |
| 73 | Andar Software | non-profit | Andar Software is a nonprofit CRM software provider with a focus on workplace fundraising and… |
| 74 | Kinetic North America | education | Kinetic North America provides student housing, resident life, and camps, conference, and… |
| 75 | Solentra | agri-food | Solentra collaborates with enterprise agribusinesses by providing comprehensive software and… |
| 76 | Red River Software | fuel | Red River Software provides point-of-sale, back-office & accounting software solutions for… |
| 77 | InTempo | rental-management | InTempo delivers mission-critical software solutions to local and regional independent rental… |
| 78 | TripSpark | people-transportation | TripSpark’s people transportation technology provides the software, in-vehicle hardware and… |
| 79 | Telepin | (untagged) | Telepin is a global leader of mobile transaction platforms, serving tier-one operators in the… |
| 80 | Incognito | (untagged) | Incognito Software Systems provides software and services solutions that help service… |
| 81 | Silvervine | financial-services | Silvervine provides property and casualty insurance administration software to regional… |
| 82 | ExtendAg | agri-food | ExtendAg is a highly acclaimed enterprise crop, raw product and grower management system… |
| 83 | Aeros | agri-food | Aeros provides integrated software solutions for the egg and poultry industry to address their… |
| 84 | SpecTec Cruise | marine | SpecTec Cruise is the industry leader in fleet asset management solutions for the cruise… |
| 85 | Wynne Systems | rental-management | Wynne Systems is a global software company providing comprehensive end-to-end software… |
| 86 | Travisoft | financial-services | Travisoft provides employee health and benefits administration software to more than 500… |
| 87 | Gallery Systems | arts-culture | Gallery Systems provides cultural collections management, digital asset management,… |
| 88 | equivant | justice | equivant provides case management software for courts, attorneys, supervision, and inmate… |
| 89 | FacilityForce | asset-management-logistics | FacilityForce addresses the ongoing challenges faced by government entities with a significant… |
| 90 | Centurisk | risk-management | Centurisk provides innovative solutions to help states, risk pools, and other organizations… |
| 91 | AssetWorks Appraisal – Risk Management | risk-management | AssetWorks builds integrated software solutions to help organizations make data-backed… |
| 92 | AssetWorks – Fleet | asset-management-logistics | AssetWorks provides organizations with appraisal software and services, facilities management… |
| 93 | AssetWorks | education | AssetWorks addresses the ongoing challenges faced by educational institutions with a… |
| 94 | Trapeze Group | people-transportation | Trapeze Group works with public transport organizations and their communities to streamline… |

#### Appendix A3: Diversis Capital — all 44 portfolio entries (current, prior and add-on)
Source: [Diversis portfolio](https://www.diversis.com/?post_type=diversis_portfolio), via `/wp-json/wp/v2/diversis_portfolio`.

| # | Company | Status tags | What it does (abridged) |
|---|---|---|---|
| 1 | Viki Solutions | add-on,prior,software | Viki Solutions is a leading provider of enterprise-grade collaboration and automation tools… |
| 2 | Design2Launch | add-on,prior,software | Design2Launch is a leading provider of artwork and label management software to… |
| 3 | American Restaurant Association | add-on,current,prior,software | Since 1996, American Restaurant Association (ARA) has been the premier food energy commodity… |
| 4 | Prime Timesheet | add-on,current,portfolio-categories,software | Prime Timesheet extends its Atlassian Jira built-in, flexible, time tracking and reporting… |
| 5 | Blue Software | prior,software | Carved out from Matthews International (NASDAQ: MATW), Blue Software, with its flagship… |
| 6 | ArrowStream | prior,software | Headquartered in Chicago, IL, ArrowStream is the first company to develop innovative supply… |
| 7 | ServicePower | current,software | Founded in 1996, ServicePower, Inc. is a leading provider of complex mobile workforce… |
| 8 | Marketron | current,software | Marketron is the media industry’s leading provider of business software solutions and services… |
| 9 | Tempo | current,software | Carved out from Origo hf. (NASDAQ: ORIGO), Tempo is a leading productivity-enhancing project… |
| 10 | PureCars | current,software | Carved out from Raycom Media, PureCars is an automotive business intelligence and marketing… |
| 11 | FORM | portfolio-categories,prior,software | Form is a SaaS mobile data collection platform for complex, business-critical use cases across… |
| 12 | RFi Group | current,portfolio-categories,software | RFI Global is the only global data and insights company dedicated exclusively to financial… |
| 13 | GoSpotCheck | add-on,portfolio-categories,prior,software | GoSpotCheck is a leading mobile task management and field execution software platform with a… |
| 14 | Black Box Intelligence | current,portfolio-categories,software | Black Box Intelligence™ (formerly TDn2K) is the leading data and insights provider of… |
| 15 | Performance Design Products | portfolio-categories,prior | Performance Designed Products (PDP) designs and distributes licensed aftermarket videogame… |
| 16 | MillerPulse | add-on,current,portfolio-categories,software | MillerPulse delivers market level insights to restaurant companies and industry observers via… |
| 17 | Rodio | add-on,current,portfolio-categories,software | Rodio is a mobile communications platform for organizations with dispersed teams working… |
| 18 | Shelfwise | add-on,portfolio-categories,prior,software | ShelfWise brings Artificial Intelligence to the shelf using state-of-the-art image recognition… |
| 19 | truPayments | add-on,current,portfolio-categories,software | truPayments is a financial technology company with deep roots in eCommerce and the Automotive… |
| 20 | Adlib Software | current,portfolio-categories,software | Adlib Software is an enterprise content intelligence and process automation software provider.… |
| 21 | Fishbowl Inventory | current,portfolio-categories,software | Fishbowl Inventory is based near Salt Lake City and is a leading provider of inventory… |
| 22 | Roadmunk | add-on,current,portfolio-categories,software | Roadmunk is an enterprise SaaS platform that enables product teams to collect feedback,… |
| 23 | SalesRabbit | current,software | SalesRabbit has been enabling field sales organizations with end-to-end native mobile and… |
| 24 | ALM Works | add-on,current,software | ALM Works provides specialized project management solutions that empower users with greater… |
| 25 | InductiveHealth | buyout,current,software | Solutions for data integration, implementation, hosting and support of disease surveillance… |
| 26 | AreTheyHappy | add-on,current,software | AreTheyHappy is a leading provider of cloud-based reputation monitoring software used daily by… |
| 27 | AutoSigma | add-on,current,portfolio-categories,software | AutoSigma is a leading provider of digital asset management software for automotive… |
| 28 | MacroMonitor | add-on,current,portfolio-categories,software | The MacroMonitor is the most comprehensive, independent macroeconomic measurement of US… |
| 29 | Autominer | add-on,current,portfolio-categories,software | Autominer is a customer data platform and data ingestion, cleansing and mining engine for the… |
| 30 | Sellware | buyout,current,portfolio-categories,software | Sellware is a multi-channel e-commerce marketplace software provider for small and mid-sized… |
| 31 | LiquidPlanner | add-on,current,portfolio-categories,software | LiquidPlanner is a industry-leading predictive scheduling and capacity planning solution. It’s… |
| 32 | Old Street Solutions | add-on,current,portfolio-categories,software | Old Street Solutions provides custom reporting capabilities for Jira dashboards. It’s flagship… |
| 33 | DBM Atlas | add-on,current,software | DBM develops research products for financial institutions in Australia to better understand… |
| 34 | AlphaServe | add-on,current,portfolio-categories,software | Alpha Serve is a pioneer in enterprise-grade data connectivity, offering a suite of powerful… |
| 35 | Decision Lens | current,software | Decision Lens develops integrated planning software which modernizes how government… |
| 36 | Infotech | buyout,current,software | Info Tech Operating LLC, DBA Infotech (Infotech) is a leading SaaS solutions provider for the… |
| 37 | Genesis | buyout,portfolio-categories | (no description) |
| 38 | Meperia | add-on,portfolio-categories | (no description) |
| 39 | Kermit | add-on,portfolio-categories | (no description) |
| 40 | RoofLink | add-on,current,software | RoofLink provides a comprehensive CRM designed to simplify and streamline the operations of… |
| 41 | LTi Technology Solutions | current,software | LTi Technology Solutions is a global provider of lease and loan finance software for the… |
| 42 | Roofle Technologies | add-on,current,software | Roofle Technologies is a provider of instant roof quoting and lead management for the roofing… |
| 43 | iSky Research | add-on,current,software | iSky Research is a provider of fact-based research for digital services industries globally,… |
| 44 | AutoAlert | add-on,current,software | AutoAlert is a provider of equity mining software for automotive dealerships. Its platform… |

#### Appendix A4: Valsoft, Tiny and SureSwift — portfolio entries visible on their sites (fetched 2026-11-07)
Valsoft's portfolio page loads with "Load More", so only the first 16 cards were captured: [Valsoft portfolio](https://www.valsoftcorp.com/portfolio). Tiny lists 21 companies: [Tiny companies](https://tiny.com/companies). SureSwift shows only product descriptions, not names: [SureSwift portfolio](https://www.sureswiftcapital.com/portfolio).

| Owner | Entry (as listed) | Niche |
|---|---|---|
| Valsoft | Chalco | Product content platform for luxury and retail brands |
| Valsoft | Firebrand (Edelweiss) | Software and services for book publishers |
| Valsoft | MIrus | Restaurant analytics and data management |
| Valsoft | Medicalistics | Correctional and public health care software |
| Valsoft | Square 9 | Document processing and content management |
| Valsoft | UnionTrack | Member management and engagement for unions |
| Valsoft | Countfire | Cloud takeoff and estimation (fire alarm) |
| Valsoft | Clubspeed | Venue management for entertainment operators |
| Valsoft | eziway | Salary packaging / FBT compliance (Australia) |
| Valsoft | MemberLeap | Cloud AMS for membership organizations |
| Valsoft | Chamber Nation | Membership and community commerce for chambers |
| Valsoft | NedFox (RetailVista) | Retail ERP for garden centres |
| Valsoft | Omnibus (Edelweiss) | Bookstore operating system |
| Valsoft | KidKare | CACFP child-care claims and meal tracking |
| Valsoft | digitaled | STEM interactive learning and assessment |
| Valsoft | Hazel | AI assistants for child care and schools |
| Tiny | Metalab, Serato, Creative Market, AeroPress, Stamped, Letterboxd, Dribbble, MediaNet, HappyFunCorp, Wholesale Pet, BeFunky, Archetype, Clean Canvas, Mateina, Meteor, Pixel Union, Foursixty, Orbit, Norbauer & Co., KNO Commerce, Out of the Sandbox | Mostly horizontal/consumer/Shopify; only MediaNet ("Special education software for Arizona schools") is vertical B2B software |
| SureSwift | 11 unnamed products | Reference checks, website testing, social scheduling, affiliate software, trade journaling, document data extraction, store locator, trader analytics, Stripe card reader, email parsing, craft-spirits subscription |

#### Appendix A5: TinySeed portfolio — 143 entries (batches Spring 2019 to Spring 2026)
Source: [TinySeed portfolio](https://tinyseed.com/portfolio). Older batches show only a tag, not a company name. These are mostly young companies, so they are evidence of the vertical-clone pattern and possible future challengers, not proven-revenue targets.

| # | Entry (URL or tag) | Description (abridged) |
|---|---|---|
| 1 | handelbay.com | HandelBay is an all-in-one, AI-powered procurement platform that automates the entire… |
| 2 | missionlens.org | Mission Lens is the Help Desk for the YMCA Front Desk. We reduce call volume, improve… |
| 3 | usesettle.com | Settle automatically discovers and wins new business for companies through RFPs. Teams… |
| 4 | sidekicklearning.net | Sidekick Learning is a training and performance tracking platform for ABA organizations.… |
| 5 | sitehunt.io | Sitehunt automates industrial real estate research so economic developers can respond to… |
| 6 | turbosource.ai | TurboSource is outbound recruiting infrastructure that turns job descriptions into AI… |
| 7 | wasapi.io | Wasapi is the all-in-one WhatsApp platform for teams flooded with more messages than they… |
| 8 | ipos.shop | Pos SaaS solution for retail stores. Combines Online, Marketpaces and in store sales into… |
| 9 | shopra.ai | Shopra is the Palantir of the beverage industry, giving suppliers real-time visibility… |
| 10 | porteria.com | Porteria is an AI-powered access control platform and app that streamlines security,… |
| 11 | gohashio.com | Hashio is the Cannabis ERP for scaling operators. They're the easy-to-use, data-rich, and… |
| 12 | giantrocketship.com | Giant Rocketship automates how IT service teams work. AI takes care of ticket flow,… |
| 13 | gem-logic.com | Gem Logic is the all-in-one operating system for jewelers — repairs, sales, stock, CRM,… |
| 14 | askedgar.io | AskEdgar transforms messy SEC filings into structured, searchable intelligence using… |
| 15 | bluelightmaps.com | Blue Light Maps equips first responders with purpose-built navigation and mapping… |
| 16 | elementix.ai | Elementix is a borrower intelligence platform that gives real estate lenders a clear view… |
| 17 | EMSSOAP.com | Fire departments and ambulance companies lose millions every year in unpaid rescue… |
| 18 | assemblia.ai | Assemblia builds highly customized AI automations to help government relations teams… |
| 19 | 4admin.co.uk | 4admin helps financial advisers scale using AI purpose-built for their complex… |
| 20 | cargofax.co | CargoFax offers a web-based platform that democratizes trade data, providing actionable… |
| 21 | datapeers.co | Datapeers is an AI revenue workforce for real estate companies. |
| 22 | hothawk.ai | HotHawk is an email client designed for how lead generation agencies run cold email for… |
| 23 | getinboxzero.com | Inbox Zero is your intelligent email assistant. It automatically sorts your messages and… |
| 24 | leadtruffle.com | LeadTruffle helps local businesses turn website visitors and missed calls into paying… |
| 25 | outboundlegal.com | OutboundLegal delivers consistent client acquisition for personal injury attorneys… |
| 26 | ppcassist.com | PPC Assist helps Amazon sellers increase profits and save time with automation and an AI… |
| 27 | rootabl.com | Rootabl is an all-in-one affiliate platform designed for online course creators and… |
| 28 | getsombra.com | Sombra provides financial firms with a secure system that captures client conversations,… |
| 29 | getspindle.com | Spindle helps companies optimize complex operations with real-time, intelligent tracking… |
| 30 | checkoutpage.co | Checkout Page is transforming how businesses accept payments online with the most… |
| 31 | easy-review.de | easyreview is a powerful talent management platform that helps busy HR teams foster a… |
| 32 | marllm.io | Marllm helps businesses scale customised sales funnels using human-centric content AI… |
| 33 | oneaccord.ai | OneAccord is a live AI translation platform for churches, bridging language gaps to make… |
| 34 | remea.io | Remea provides a smart EV charging management platform tailored for businesses in the… |
| 35 | flo-sp.com | Vocala Smart Properties provides fleet-managed, Technology Enabled Care solutions that… |
| 36 | wanotifier.com | WANotifier is an all-in-one WhatsApp marketing SaaS tool for businesses that lets them… |
| 37 | vendorsage.com | VendorSage's software and community helps organisations get more value out of every… |
| 38 | myteamfluence.com | We are a cloud platform that helps B2B companies to fill their sales pipeline from… |
| 39 | sitio.ai | Sitio is a comprehensive digital governance platform that helps organizations optimize… |
| 40 | seestuff.net | In the commercial property space, buildings often rely on 20 or more disconnected… |
| 41 | scalelist.com | Scalelist allows salespeople to close more deals by creating the perfect prospect list.… |
| 42 | packemwms.com | I'm Sam, founder of PackemWMS. We're on a mission to make warehousing software accessible… |
| 43 | leadcapture.io | LeadCapture.io <http://LeadCapture.io> is an advanced lead capture platform built to help… |
| 44 | kennellink.com | Kennel Link is an all-in-one platform for pet care facilities that streamlines daily… |
| 45 | inkzup.com | Inkzup is an all-in-one business management platform designed for tattoo shops and… |
| 46 | getdrum.com | Drum is all-in-one software for Australian professional service businesses. |
| 47 | blinkmetrics.com | Know every inch of your business in seconds with automated KPI tracking - automatically… |
| 48 | rentkit.com | RentKit offers powerful, user-friendly event rental software and equipment rental… |
| 49 | avohq.io | Avo helps developers build apps 10x faster, using configuration instead of traditional… |
| 50 | growform.co | Growform helps lead generation agencies and marketers build forms that look great on any… |
| 51 | jasaratech.com | Jasara Technology is building PrepBusiness, an inventory management software for 3PLs… |
| 52 | linklo.io | Linklo.io helps Linkedin advertisers easily optimise ad campaigns and maximise ROI - with… |
| 53 | marcode.ai | Marcode monitors the ads that are running in search engines for a company's brand… |
| 54 | qommet.com | Qommet helps companies to make comprehensive decisions on pay raises with internal equity… |
| 55 | recview.co | RecView is the modern video tool for recruiters, allowing teams to insert video into all… |
| 56 | reviewflowz.com | Reviewflowz helps SaaS companies optimize their visibility on software review platforms… |
| 57 | sanoflow.io | Sanoflow is an omnichannel conversational commerce platform that helps businesses to sell… |
| 58 | zitles.com | Zitles modernizes archaic real estate title search and review processes. Zitles… |
| 59 | userdoc.fyi | Userdoc's AI supercharges your software requirements, allowing you to scope your systems… |
| 60 | trot.to | Trotto is an enterprise go links provider, an internal URL shortener that enables your… |
| 61 | tooltribe.com | TOOLTRIBE is the tool inventory app built for the job site. We make it easy for… |
| 62 | tempestamedia.com | We can predictively drive leads, revenue and ROI from content marketing for our business… |
| 63 | outboundsync.com | OutboundSync integrates outbound sales and marketing tools with your CRM. Get leads,… |
| 64 | nekst.com | Nekst simplifies real estate processes, allowing agents and teams to create personalized… |
| 65 | joinmoov.com | As schools struggle to engage their students (and quantify their engagement) in a world… |
| 66 | gentext.ai | Gentext develops AI-powered Microsoft Office add-ins for industry-specific uses. Their… |
| 67 | HR | Say hello to Wrenly. Nestled in Slack/Teams and powered by AI, she’s your ally in… |
| 68 | Bookkeeping | UpSheets is a web-based app that enables businesses to upload data into Xero Payroll and… |
| 69 | Fitness | TrainerMetrics enables personal training at scale. By automating service delivery,… |
| 70 | PropTech | The 3D Tiny House Designer is the first design software made for the small home industry. |
| 71 | Marketing | Shrpa bridges the gap between destinations and creators with our industry-leading content… |
| 72 | SaaS | RewardUp enables brands to easily implement customizable loyalty and gift card programs,… |
| 73 | Analytics | Basket Point of Sale is a fully managed analytics platform for independent retailers.… |
| 74 | Security | Relay Hawk secures answering services and call centers through a suite of cybersecurity… |
| 75 | Sales | Dealintent is an AI-powered software platform that streamlines the B2B buying and selling… |
| 76 | eCommerce | Flexibl is a payment intelligence platform that allows ecommerce SaaS providers to… |
| 77 | Construction | Mawi revolutionizes project management for construction firms across Latin America,… |
| 78 | Freight | Oway is a rideshare freight platform that sells unused space in trucks to SMBs at a 50%… |
| 79 | Government | RefactorOS is a fully customisable data management platform built specifically for public… |
| 80 | SEO | Adaptify uses AI to automate SEO services for agencies and their customers. It… |
| 81 | Construction | Introducing AutoPSI, the breakthrough software transforming the construction industry's… |
| 82 | SaaS | Classcard is the fastest way to manage and sell classes. Classcard does all the boring… |
| 83 | CX | Cliezen is a dedicated CX platform uniquely tailored for non-SaaS industries, going… |
| 84 | Weddings | Mybridal is an all-in-one platform that simplifies and automates many of the day to day… |
| 85 | SaaS | Carrick brings patient texts, calls, voicemails, AI assistance, and more together in one… |
| 86 | HR | Omega provides affordable, full-featured employee benefit websites to help HR teams… |
| 87 | Legal | Legal27 provides lawyers and law firms with a remote legal assistant and legal software,… |
| 88 | Events | Gandaya offers a no-code platform-builder so that large festivals and events can empower… |
| 89 | Analytics | Datacoves is a turnkey analytics workbench that reduces the complexity of the modern data… |
| 90 | eSports | Castmetrics is the easiest way to get insights into the esports industry. Castmetrics… |
| 91 | Infrastructure | Approximated is the fastest, easiest, and most scalable way to offer a custom domains… |
| 92 | SaaS | Super is The Family Office OS. All-in-one software to streamline asset aggregation,… |
| 93 | AI | Siterecon is an AI-powered job site mapping tool for outdoor services professionals. It… |
| 94 | Education | SessionLab helps facilitators, consultants and team leaders to design and deliver… |
| 95 | eCommerce | Panoramata helps you track your ecommerce competitors strategy and find unlimited… |
| 96 | Events | HeySummit is the easy to use virtual event platform that helps you grow your audience and… |
| 97 | SaaS | VerificationManager provides secure, automated processing of verification of income and… |
| 98 | E-Commerce Tools | Your brand is discoverable, now make it shoppable. Nextchannel helps consumers locate and… |
| 99 | Marketing | Any brand can generate new revenue by giving customers a friction-free way to buy… |
| 100 | Investor Tools | The cleanest source of financial data on the internet. Investors can research public… |
| 101 | Developer Tools | StatusGator monitors all your cloud vendors, gives your team a unified status page, and… |
| 102 | Security Testing | GlitchSecure helps companies secure their products and infrastructure through real-time… |
| 103 | Events | Event Cost Sheet makes it easier for teams to plan, manage, and run events. The software… |
| 104 | Software Testing | Software teams use Currents to improve the performance, stability and efficiency of their… |
| 105 | Engineering | Beyondware is focused on making better 3D visualization tools for transportation and… |
| 106 | SaaS | Fleetworks helps car and van fleet operators, such as leasing or rental companies,… |
| 107 | Education | Frontend Mentor helps people improve their coding skills by building projects. We also… |
| 108 | SaaS | AudienceTap is a text-to-buy platform that turns SMS into an instant checkout for DTC… |
| 109 | AI | Automata helps marketing teams produce more content in less time with AI-powered… |
| 110 | SaaS | Whale Blue helps investment funds manage their portfolio dashboards, credit reviews and… |
| 111 | SaaS | WayLit is an immigration management platform for U.S. and Canadian employers. |
| 112 | Internal Tools | Suggestion Ox is the online feedback and reporting platform that makes it easy for HR… |
| 113 | Security | Skysnag protects organizations against email impersonation. |
| 114 | Productivity | Keeping is a help desk and shared inbox that works on top of Gmail. We help small and… |
| 115 | Accounting | Client Hub is designed specifically for cloud-based accounting and bookkeeping practices… |
| 116 | Marketing | Personalized offboarding experiences for subscription businesses. |
| 117 | Hardware SaaS | KioskBuddy is an app that transforms a tablet into a self-service ordering kiosk, helping… |
| 118 | Healthcare | Zentake is a patient intake management tool that improves Medical practices patient… |
| 119 | SaaS | Testable helps behavioral researchers create experiments and surveys in minutes instead… |
| 120 | Security | Risk management software to secure information for your organization, employees, vendors… |
| 121 | Developer Tools | Judoscale is a Heroku add-on for avoiding app slowdowns and lowering your Heroku bill. |
| 122 | Marketing | Postaga is an all-in-one link building and outreach platform that helps marketers more… |
| 123 | Legal SaaS | Lexgo is the first automated legal service for startups in Latam, enabling founders to… |
| 124 | getlasso.co | Lasso is the all-in-one affiliate marketing plugin for WordPress, helping you create… |
| 125 | Productivity | Dashfox is an out-of-the-box sales tool that enables non-tech savvy users to follow-up… |
| 126 | Marketing | SaaS email automation that understands your customer data model. Track clean… |
| 127 | Podcasting | The remote recording studio that your audience will love. Create high-quality audio and… |
| 128 | Acquired | Database insights via Python and SQL. |
| 129 | Developer Tools | Tired of getting blocked while scraping the web? ScrapingBee’s API handles headless… |
| 130 | Productivity | Customizable retrospectives for Agile development teams. |
| 131 | Asset Management SaaS | Organizations of all sizes use Reftab to track and manage equipment. Whether assigning… |
| 132 | Biotech SaaS | DealForma provides the biotech data and does your research for you — so you can focus on… |
| 133 | Hiring | Make better hiring decisions with take-home coding challenges. |
| 134 | SaaS | All-in-One CRM, estimating, and production management software just for contractors. |
| 135 | Productivity | Finally, a scheduling tool both the sender and the recipient will love ♥️ |
| 136 | Financial | Build trust in your plans. Express your financial operations on a flexible canvas. |
| 137 | Education | Automate Class, Camp, and Aftercare registration. Paperless enrollment, payments, and… |
| 138 | Hiring | The best way to reimburse job candidates. Perfectly balancing easy expense reporting,… |
| 139 | Developer Tools | Don't crash under peak traffic! Load test your web application with thousands of bots to… |
| 140 | Acquired | Accounting and bookkeeping software for small businesses. |
| 141 | Interior Design | Gather is interior design project management software that helps busy teams share… |
| 142 | SaaS | Automated client intake for attorneys. |
| 143 | Podcasting | Castos is the only podcast hosting platform that automates every aspect of building a… |

### Inferences
- **Stacking signals milking.** When one owner holds 3–5 competing products in a niche (Jonas movers, Jonas dietary, Volaris grain, Valsoft unions), customers have fewer independent alternatives, and the owner has little reason to modernise every product. This is the cleanest "proven revenue plus neglect" pattern. It is not always true: Jonas's CampSite and Valsoft's KidKare both rate 4.7★.
- **The Constellation ecosystem skews to enterprise and international.** Of 229 Volaris entries only 94 touch North America, and many of those are public-sector or enterprise: transit, insurance carriers, courts. SMB-reachable US targets are concentrated in Jonas (clubs, fitness, moving, salon, foodservice) and in the newer Valsoft association-management stack.
- **TinySeed's portfolio is evidence the playbook works**: small funds back modern vertical clones for jewelers, tattoo shops and kennels. It also warns that the best SMB niches attract funded challengers quickly.

### Gaps
- Harris (Constellation's public-sector and utilities group), Perseus, Lumine, Banyan, Vela, Calm Company Fund, Earnest and Upland lists could not be captured; see the method note. Upland's products page was fetched but not analysed.
- Valsoft's full list sits behind a "Load More" control; only 16 entries were captured.
- Acquisition dates and prices are mostly undisclosed. Volaris pages show "Founded" and "Acquired" years in HTML, but the API records did not include them.

---

## Q2. Shortlist: which clone opportunities survive the method? (evidence per candidate)

### Takeaway
Seven candidates survive, three of them only conditionally, plus one on the watch list. All seven are **membership, records or billing back-offices for small, under-staffed organisations** that a roll-up or PE owner now controls. Ranked by score /25:
1. **Chambers of commerce (S3): 19.** Proven price points of $2.9–3.9k/yr, >7,500 US chambers, a clear association channel.
2. **Labor-union locals with OLMS LM-3/LM-4 filing (S1): 17.** ~16.4k small-union filers; Valsoft now owns three leaders.
3. **Volunteer/rural fire department records, NERIS-native (S2): 16.** 27,126 registered departments; ESO is phasing out Emergency Reporting.
4. **Small water/sewer utility billing (S4): 16.** ~47,000 small community water systems.
5. **Independent self-storage (S5): 16.** Conditional, crowded.
6. **Alarm dealer back-office (S6): 15.** Conditional, thin data.
7. **Small-market radio traffic and billing (S7): 14.** Conditional, shrinking market.

Healthcare dietary (S8) is on watch for lack of evidence. None of the shortlisted niches has a single dominant modern, fairly priced challenger, but several have credible small ones (Muni-Link, First Due, 6Storage). Every candidate is a *positioning* opportunity, not an empty field.

### Cited Findings

#### S1. Labor-union local back-office plus OLMS annual-report filing (incumbents: UnionWare, MemberTrak, UnionTrack; owner: Valsoft)
- **Revenue proof (acquisitions):**
  - Valsoft acquired UnionWare and MemberTrak, "two North American leaders in the union software industry". UnionWare was founded in 1993 and covers "member and dues management to grievances and organizing" — [Valsoft release](https://www.valsoftcorp.com/news/valsoft-enters-the-association-management-portfolio-with-the-acquisitions-of-unionware-and-membertrak) (29 Apr 2025).
  - The seller was Togetherwork, which is backed by GI Partners — [Gibson Dunn](https://www.gibsondunn.com/gibson-dunn-advised-togetherwork-holdings-on-its-sale-of-unionware-and-membertrak-to-valsoft-corporation/); [via search summary: MergerLinks](https://app.mergerlinks.com/transactions/2025-04-29-unionware).
  - Valsoft's TAG Software Group then acquired UnionTrack. UnionTrack was founded in 2014 in Rockville, MD and "supports more than 450 labor affiliates across North America" **[vendor]**. Its ENGAGE product combines "dues and per capita payments, bidirectional member communications, organizing, training, and grievance tracking" — [Newswire](https://www.newswire.com/news/valsofts-tag-software-group-strengthens-its-association-management-portfolio).
  - UnionWare marketing says UFCW runs >1.3M members on it **[vendor; via search summary]** — [UnionWare](https://unionware.com/labor-union-app).
- **TAM and regulation:**
  - Unions with ≥$250k annual receipts file LM-2, those under $250k may file LM-3, and those under $10k may file LM-4. The 2022 LM-4 instructions cite <$25k, so sources conflict.
  - OLMS proposed raising the thresholds to $450k (LM-2) and $25k (LM-4). I found no final rule.
  - Reports are due within 90 days of fiscal year-end.
  - Sources: [OLMS forms](https://www.dol.gov/agencies/olms/reports/forms/lm-1-lm-2-lm-3-lm-4); [OLMS threshold notice](https://www.dol.gov/agencies/olms/notice-revision-filing-thresholds-lm2-lm3-lm4) (via search summary).
  - OLMS rulemaking requires LM-3 and LM-4 filers to submit electronically — [OLMS e-filing rule](https://www.dol.gov/agencies/olms/laws/regulations/nprm-required-electronic-filing-lm-3-ml-4).
  - **2020 filings: 9,953 LM-3 and 6,429 LM-4** (older data; counts declining since 2009) — [OLMS data, archived 2020](https://webarchive.library.unt.edu/web/20201220033537/https://www.dol.gov/agencies/olms/data) (via search summary; direct fetch failed TLS).
- **Neglect evidence:**
  - Public reviews are thin. SourceForge and Slashdot show no user reviews for UnionTrack (via search summary) — [SourceForge UnionTrack alternatives](https://www.sourceforge.net/software/product/UnionTrack/alternatives).
  - The consolidation itself is the main signal: the owner of three leaders now faces less competition at renewal.
  - **I found no dated price-hike quotes for these products.**
- **Modern challengers (fragmented, none dominant found):**
  - Union Impact sells against UnionTrack directly ("UnionTrack Dues and PAC Payments Alternative") with demos and a "1 Month Risk-Free Trial". Its testimonials come from UA Local 32, IATSE Local 665 and Teamster Local 456 — [Union Impact](https://unionimpact.com/uniontrack-dues-pac-payments-alternative/).
  - Other named alternatives: eMembership, VUE Labor Management, Un1on, Union365 and WeRise — [SourceForge](https://www.sourceforge.net/software/product/UnionTrack/alternatives).

#### S2. Volunteer and rural fire department records, NERIS-native (incumbents: FIREHOUSE Software / ESO Fire RMS, Emergency Reporting; owner: ESO)
- **Neglect evidence (dated quotes, Capterra):**
  - ESO Fire RMS (formerly FIREHOUSE Software) has **2.7★ from 18 reviews**. Its newest review on the page is from 2022 — [Capterra FIREHOUSE](https://www.capterra.com/p/121521/FIREHOUSE-Software/reviews/).
    - "Not intuitive. Runs on old software (FoxPro). Mobile products are horrible. Customer service is practically non-responsive" (Jan 4, 2018).
    - "attempted to contact the company several times… told my situation would be escalated… then never hear back" (Jun 30, 2022).
    - "FH has not continued to keep up with the times" (Apr 17, 2018).
  - Emergency Reporting has 4.4★ (43) — [Capterra Emergency Reporting](https://www.capterra.com/p/121517/Fire-Package/reviews/).
    - "they were acquired by ESO in 2021, and are planning a phase-out of the platform… existing customers are leaving in droves for other vendors" (Battalion Chief, Jan 13, 2025).
    - "They were bought out and will be no longer availble after Nov 2025" (Mar 17, 2025).
    - "now we have to switch to ESO" (Dec 5, 2022).
  - A North Dakota state notice (Mar 2025) told departments on ER to move to the new ESO tool. It said ESO "will migrate most of the data" — [ND notice, via search summary](https://www.firemarshal.nd.gov/news/data-reporting-option-north-dakota-fire-districts).
- **Regulatory trigger:**
  - NFIRS sunsets in Feb 2026 per USFA (Mass.gov and VFIRE say Jan 2026) — [USFA NFIRS sunset](https://www.usfa.fema.gov/nfirs/sunset/).
  - NERIS access is **free** to verified departments — [USFA NERIS FAQ](https://www.usfa.fema.gov/nfirs/neris/faq/ux/).
  - Departments without a CAD or RMS can use a NERIS-provided data-capture app — [Virginia Fire NERIS](https://vafire.com/risk-reduction/neris/) (via search summary).
  - ESO announced its NERIS solution on Nov 20, 2025 at "no additional cost" to ESO Fire Incidents customers — [ESO NERIS](https://www.eso.com/neris/); [ESO NERIS FAQ](https://www.eso.com/blog/neris-faqs/).
- **TAM:** 27,126 departments are on the USFA National Fire Department Registry, 91% of US departments — [USFA registry summary, via search summary](https://apps.usfa.fema.gov/registry/summary). An OMB statement from Sep 2026 cites 27,182 — [OMB supporting statement](https://omb.report/icr/202605-1660-001/doc/168514300.pdf).
- **Modern challengers:**
  - First Due has 4.6★ (58). Recent reviews are positive ("Best Firefighting software", Nov 25, 2025) — [Capterra First Due](https://www.capterra.com/p/179338/First-Due/reviews/).
  - Latka (est.) puts First Due at $11.8M revenue (Oct 2024) and 294 employees (Dec 2024) — [Latka First Due](https://getlatka.com/companies/first-due).
  - The category page also lists PSTrax 5.0 (20), Emergency Logs 4.9 (58), Rescue Hub 4.6 (52), Responder360 4.6 (20) and Aladtec — [Capterra fire department software](https://www.capterra.com/fire-department-software/).

#### S3. Chambers of commerce and small business associations (incumbents: GrowthZone / ChamberMaster; Chamber Nation; owners: Lead Edge Capital (PE); Valsoft)
- **Revenue proof:**
  - GrowthZone was acquired by PE firm Greenridge in Nov 2019 — [Newswire](https://www.newswire.com/news/growthzone-announces-acquisition-by-greenridge-investment-partners-21030235). It was then acquired by Lead Edge Capital in May 2023 — [William Blair](https://www.williamblair.com/News/GrowthZone-and-Lead-Edge-Capital-Transaction).
  - GrowthZone itself is a roll-up: BuilderFusion (home-builder associations, 2017) — [GrowthZone](https://www.growthzone.com/news-press/growthzone-acquires-builderfusion); MemberSuite (2023) — [MergerLinks](https://app.mergerlinks.com/transactions/2023-09-21-membersuite); JUNO (2024) — [GrowthZone](https://www.growthzone.com/news-press/growthzone-aquires-juno-to-enhance-member-engagement-capabilities).
  - Latka: GrowthZone revenue $4.6M (Aug 2020, older), 84 employees (Dec 2020) — [Latka GrowthZone](https://getlatka.com/companies/growthzone).
  - Chamber Nation (Valsoft) list pricing is **$2,878.75** on a 1-, 3- or 5-year term, with a "combined setup" of **$3,386.75** (term only) — [Chamber Nation pricing](https://www.chambernation.com/pricing).
  - ChamberMaster listings say subscriptions start at **$3,900/yr** (via search summary) — [Capterra ChamberMaster](https://www.capterra.com/p/144469/ChamberMaster/).
- **Neglect evidence:** ChamberMaster has 4.3★ (20); its newest review on the page is from 2022 — [Capterra ChamberMaster reviews](https://www.capterra.com/p/144469/ChamberMaster/reviews/).
  - "Poor customer support… They should do away with the ChamberMaster platform altogether and switch everyone to Growth Zone… impossible to make changes to the front end without the help of a level 2 tech person" (Jun 15, 2022).
  - "Our organization felt it was timely to switch to GrowthZone… It hasn't been a smooth transition" (Mar 19, 2021).
  - A SourceForge reviewer reports "a price increase and a gateway fee added to their bill in the first few months" (via search summary) — [SourceForge GrowthZone](https://www.sourceforge.net/software/product/GrowthZone).
  - Counterpoint: GrowthZone's own Capterra listing shows 4.4★ from 276 reviews (via search summary). The incumbent is not universally disliked.
- **TAM:** ACCE says "more than 7,500 chambers of commerce in the United States", using a broad definition — [ACCE](https://www.acce.org/pages/chambers/). ACCE itself serves "9,000 leaders from 1,300 chambers" — [ACCE about](https://secure.acce.org/pages/about-us/). The US Chamber cites ~7,000 (via search summary) — [US Chamber accreditation](https://www.uschamber.com/chamber-accreditation-program?state=id).

#### S4. Small community water and sewer utility billing (incumbents: El Dorado, SOFTWater, QuikWater, Banyon and Harris lines; owners: mixed, with Harris/Constellation consolidating at the top)
- **Roll-up activity:**
  - Harris bought PowerManager (utility billing, AR/AP and payroll for "over 170 municipalities and utilities", May 2023) — [NMPP](https://www.nmppenergy.org/news/harris-acquires-powermanager-business-salt-creek-software-nmpp).
  - Harris also bought Cognera (2012) — [Harris](https://harriscomputer.com/news/en/ma-resourcescognera) — and SilverBlaze portals — [Harris](https://harriscomputer.com/news/en/ma-resourcessilverblaze).
- **Neglect evidence (Capterra; most reviews are old):**
  - El Dorado has 4.3★ (78); the newest review on the page is from 2023 — [Capterra El Dorado](https://www.capterra.com/p/21260/Utility-Billing-Software/reviews/).
    - "as soon as we can we are leaving the software… their programming team is lacking. There also fees every time you turn around for things that should be pretty standard" (Apr 9, 2021).
  - SOFTWater has 4.4★ (29); all parsed reviews are from 2018 — [Capterra SOFTWater](https://www.capterra.com/p/17163/SOFTWater/reviews/).
    - "regular glitches that require a call in to have fixed" (Sep 21, 2018).
    - "COMPARED TO ALOT OF NEWER SOFTWARE, THE PRINTED BILLS SHOULD BE MORE INFORMATIVE" (Oct 23, 2018).
  - QuikWater has 4.5★ (31); its newest review is from 2021 — [Capterra QuikWater](https://www.capterra.com/p/16629/QuikWater/reviews/).
- **Modern challengers (credible, not dominant):** Muni-Link 4.8 (59; review Oct 2025), MuniBilling 4.7 (54), Rural Billing 4.9 (60) and Banyon 4.6 (14) — [Capterra utility billing](https://www.capterra.com/utility-billing-software/); [Capterra Muni-Link](https://www.capterra.com/p/128792/Muni-Link/reviews/).
- **TAM:** Small systems (≤10,000 served) are "more than 92% of the nation's 51,000 community water systems" — [EPA](https://www.epa.gov/dwregdev/small-drinking-water-system-variances). There are "over 148,000 public water systems" in total — [EPA](https://www.epa.gov/dwreginfo/information-about-public-water-systems).

#### S5. Independent self-storage operators (incumbents: SiteLink, storEDGE, Easy Storage Solutions; owner: Storable, which Latka lists as EQT-owned) — conditional
- **Revenue proof:**
  - SiteLink Web Edition has 4.7★ from 452 reviews — [Capterra SiteLink](https://www.capterra.com/p/92752/SiteLink-Web-Edition/reviews/).
  - Easy Storage Solutions has 4.8★ from 703 reviews — [Capterra ESS](https://www.capterra.com/p/112769/Self-Storage-Software/reviews/).
  - "Storable Edge" (storEDGE) has 4.4★ from 234 reviews — [Capterra Storable Edge](https://www.capterra.com/p/218435/storEDGE/reviews/).
  - Latka lists Storable's owner as EQT; revenue is not disclosed — [Latka Storable](https://getlatka.com/companies/storable).
- **Neglect evidence (dated quotes):**
  - "Once was a great company - nothing like they originally were… Actively looking for a replacement to SiteLink… Sitelink was purchased by Storable and customer ser[vice]…" (Apr 29, 2025).
  - "we were forced to move to their merchant services platform and we have had issue after issue" (Nov 11, 2021).
  - "They switched over all of their credit card processing to themselves, and it was not planned out well" (Jun 8, 2022) — all [Capterra SiteLink](https://www.capterra.com/p/92752/SiteLink-Web-Edition/reviews/).
  - ESS: "As of the last few months I feel like something has changed or they have been bought out and the customer service has went down" (Sep 30, 2024) — [Capterra ESS](https://www.capterra.com/p/112769/Self-Storage-Software/reviews/).
  - storEDGE: "I do not recommend this company… keep being told things are done" (Feb 11, 2026) — [Capterra Storable Edge](https://www.capterra.com/p/218435/storEDGE/reviews/).
  - WebSelfStorage has 3.3★ (93): "Hate This Software" (May 4, 2021) — [Capterra WebSelfStorage](https://www.capterra.com/p/99711/WebSelfStorage/reviews/).
- **Modern challengers (many, none dominant):** 6Storage 4.7 (90), Stora 4.8 (21), Storeganise 4.7 (18), KINNOVIS 4.7 (21), StoragePug 5.0 (20), Unit Trac 4.7 (69), CCStorage 4.5 (54) — [Capterra self-storage](https://www.capterra.com/self-storage-software/).

#### S6. Alarm and security dealer back-office: recurring-revenue billing, service, inspections (incumbents: SedonaOffice; Cornerstone Billing Solutions; owners: Bold Group/EverCommerce; Jonas) — conditional
- **Ownership:**
  - EverCommerce acquired Perennial (SedonaOffice) and Bold in 2018, then merged them — [Security Sales](https://www.securitysales.com/news/bold-technologies-perennial-merge/78669/); [SDM](https://www.sdmmag.com/articles/95013-perennial-software-acquired-by-service-commerce-platform-evercommerce) (older, 2018).
  - Jonas lists Cornerstone Billing Solutions ("cloud-based billing and account management solutions" in its security vertical) — [Jonas companies](https://jonassoftware.com/our-companies).
- **Neglect evidence:**
  - SedonaOffice has 4.3★ from 8 reviews, with sub-scores Ease of Use 3.9/5 and **Customer Support 3.3/5** (Capterra Canada, via search summary) — [Capterra.ca SedonaOffice](https://www.capterra.ca/software/168581/sedonaoffice).
  - One dealer wrote that support "has gotten a bit better since Bold acquired Sedona, but is still very much a work in progress" (via search summary) — [Capterra.ca reviews](https://www.capterra.ca/reviews/168581/sedonaoffice).
  - Pricing is "Contact vendor" — [Capterra SedonaOffice](https://www.capterra.com/p/234356/SedonaOffice/).

#### S7. Small-market radio station traffic and billing (incumbents: Marketron; WideOrbit; owners: Diversis; Volaris) — conditional
- **Revenue proof:**
  - Latka: Marketron (founded 1969; owner Diversis) revenue $11.5M (Apr 2021, older), 170 employees, "Customers 7K" — [Latka Marketron](https://getlatka.com/companies/marketron).
  - Volaris lists WideOrbit (ad sales to traffic and billing) — [Volaris portfolio](https://www.volarisgroup.com/portfolio/).
  - Diversis lists Marketron as "the media industry's leading provider of business software" **[vendor]** — [Diversis portfolio](https://www.diversis.com/?post_type=diversis_portfolio).
- **Neglect and age:**
  - Marketron's own pages say cloud SaaS "is somewhat rare in the radio traffic environment" because stations "traditionally had most of their software on premises". It pitches its lower tier, RadioTraffic, at "small-market broadcasters" and "single-person traffic teams" (via search summary) — [Marketron radio traffic](https://www.marketron.com/?p=73).
  - The only 2025 "Radio Traffic Software Survey" was run with Marketron. Its results are gated — [Future B2B webinar](https://events.futureb2b.com/on-demand/2467/the-radio-traffic-system-landscape-industry-perceptions-and-needs).
  - **No independent neglect quotes were found.**
- **TAM:** As of Jun 30, 2026 the FCC counted 4,300 AM, 6,560 commercial FM and 4,806 educational FM stations (15,666 total) plus 2,013 LPFM. The count is declining quarter over quarter — [FCC DA-26-652A1](https://docs.fcc.gov/public/attachments/DA-26-652A1.pdf) (via search summary).

#### S8 (watch). Hospital and long-term-care dietary/diet-office software (Computrition, DFM, Common CENTS, MonarqRC; owner: Jonas)
- **Holding period:** Jonas has held these since 2007, 2008 and 2009, and describes DFM as covering "production, point of sale, diet office management and nutritional care" — [Jonas food portfolio history](https://jonassoftware.com/history-of-the-jonas-food-portfolio).
- **Evidence gap:** Capterra search returned no matching listings, and no review, customer-count or challenger data was found.

### Inferences

**Score table (1–5 each: revenue proof / beatability / copyability / expansion / channel replicability)**

| # | Opportunity | Rev | Beat | Copy | Expand | Channel | **Total /25** | Confidence |
|---|---|---|---|---|---|---|---|---|
| S3 | Chamber and association back-office ("chamber-in-a-box") | 4 | 3 | 4 | 4 | 4 | **19** | Medium |
| S1 | Union local back-office plus LM-3/LM-4 autopilot | 4 | 3 | 4 | 3 | 3 | **17** | Medium-low (thin reviews) |
| S2 | NERIS-native volunteer fire department ops | 4 | 3 | 3 | 3 | 3 | **16** | Medium |
| S4 | Small water/sewer district billing | 4 | 2 | 3 | 4 | 3 | **16** | Medium |
| S5 | Independent self-storage with no forced processor | 5 | 2 | 3 | 3 | 3 | **16** | Medium (crowded) |
| S6 | Alarm dealer RMR billing and service | 3 | 3 | 3 | 3 | 3 | **15** | Low (n=8 reviews) |
| S7 | Small-market radio traffic and billing | 4 | 2 | 3 | 2 | 3 | **14** | Low |
| S8 | Senior-living and LTC diet office (watch) | 3 | 2 | 2 | 3 | 2 | **12** | Very low |

**S3: Chambers.** Spin: a flat **$99–199/mo** chamber platform, against $2.9–3.9k/yr plus setup and multi-year terms, covering:
- member directory with SEO profile pages
- dues autopay and invoicing
- events and ticketing
- renewals with dunning
- a member self-service portal
- AI drafting for renewal letters and event copy
- **No multi-year term, no setup fee.**

MVP (6–10 weeks): CRM, dues billing on Stripe, events, a public directory and an importer from ChamberMaster/GrowthZone/Chamber Nation CSV exports. The importer is the wedge, because chambers fear losing member history. No regulation.

Expansion path:
- home-builder associations (GrowthZone's own BuilderFusion move shows the adjacency)
- Main Street, downtown and tourism organisations
- small trade associations
- add-ons: payments take-rate, gift-card or "shop local" programs, sponsorship marketplaces

Channel: ACCE (1,300 member chambers), state chamber-executive associations and their conferences, and SEO on "ChamberMaster alternative". Incumbents sell by phone (Chamber Nation's number is "855-ADD-Members") and custom quotes. A newcomer can replicate this through association sponsorships and webinars. Risk: low per-customer budgets and slow board-approved switching.

**S1: Union locals.** Spin: "the treasurer's tool" for locals filing LM-3 or LM-4 (~16.4k filers in 2020), at roughly **$49–149/mo**. It covers:
- member roster
- dues schedules
- employer check-off file reconciliation
- per-capita remittance to the international
- an online dues and PAC portal
- an **LM-3/LM-4 worksheet generated from categorised transactions**, ready for OLMS electronic filing

MVP (8–12 weeks): roster/dues/ledger, CSV import from UnionWare, MemberTrak and Excel, a Stripe/ACH dues portal and the LM-3 export. The regulatory surface is the LMRDA reporting format only. A wrong filing has legal consequences, so the output should be a "prepared for officer review" worksheet.

Expansion:
- grievance tracking
- hiring-hall dispatch (Union Impact's IATSE testimonial shows the demand)
- member app
- PAC compliance
- then other dues-funded organisations: fraternal lodges, professional societies

Channel: word-of-mouth between local officers, international union conventions, central labor councils. **Trust and "union-friendly vendor" status matter.** This is a channel risk I could not quantify.

**S2: Fire departments.** Spin: a **$39–99/mo** ops tool for volunteer and combination departments:
- submit incidents to NERIS via API, so data is not entered twice into the free federal app
- apparatus and SCBA checks
- training hours and ISO documentation
- member roster and certifications
- an importer for NFIRS 5.0 / Firehouse / Emergency Reporting exports

MVP: 10–14 weeks, because NERIS integration and vendor compatibility testing add time. The kill risk is real. First Due is well-funded and well-rated, ESO bundles NERIS at no added cost, and the federal portal is free. The angle is "cheaper and simpler than First Due for 10–40-member volunteer departments", not "NERIS compliance". Expansion: rescue squads, EMS agencies, county fire marshals (inspections and permits). Channel: state firefighter associations and fire-marshal offices, which actively publish vendor guidance (the ND notice). Sales are slow: chief and board approval cycles.

**S4: Water districts.** Spin:
- cloud billing for systems serving ≤3,300 people
- rate tables with tiers, minimums and sewer add-ons
- meter-read import from handheld/AMR CSV files
- PDF and email bills
- online pay with a convenience fee passed to the customer (El Dorado reviewers cite this as a key saving)
- shut-off and late-fee lists
- importer from legacy exports

MVP: 10–12 weeks. Beatability is the weak point. Muni-Link and Rural Billing are already well-rated cloud options, and switching triggers are rare (staff retirement, vendor sunset). Expansion: sewer districts, gas co-ops, small electric munis, HOA water systems. Channel: rural-water associations and state clerk associations (inference; not verified).

**S5: Self-storage.** Spin: "your merchant account, your rules". Flat pricing for 1–3 facility owners, no forced in-house processing (the most repeated complaint), a tenant portal, auto-pay migration and an importer from SiteLink/ESS exports. Copy risk: gate-access integrations (PTI, OpenTech, Noke) are required for many facilities. Crowding is high: at least six well-rated challengers. This is only worth doing with a sharper sub-niche, such as rural U-Haul dealers moving off WebSelfStorage.

**S6: Alarm dealers.** Spin: recurring-revenue billing plus service tickets plus an inspection-report app for dealers with under 2,000 accounts, with a QuickBooks Online sync. Data is thin (8 reviews), and central-station integrations add scope. Validate with customer interviews before building.

**S7: Radio.** Spin: a browser-based traffic log and billing tool for single-station and small-cluster owners, with automation-system log export and FCC political-file helpers. The market is shrinking (15,666 full-power stations, falling each quarter), and log-format integration is fiddly. Lowest priority.

**Cross-cutting:**
- Every shortlisted niche needs an **importer** as the main wedge.
- Every niche has **payments as the monetisation add-on**: dues, utility bills, rent, RMR.
- Every niche sells through **associations**, so channel replicability rests on conference and sponsorship presence plus "X alternative" SEO pages.

### Gaps
- **Census CBP establishment counts** for NAICS 813930 (labor unions), 813910 (business associations), 515112 (radio), 561621 (security systems), 531130 (storage) and 221310 (water) could not be fetched: the API now requires a key. The TAM figures above come from OLMS, ACCE, USFA, EPA and FCC instead.
- **Price-hike quotes are missing** for the union products, Marketron and the Jonas dietary products. Their beatability scores rest on ownership structure, not on documented customer pain.
- **Alarm-dealer counts:** I found no sourced US count.
- **Customer counts and revenue:** Latka had no profiles for UnionTrack, UnionWare, KidKare, Computrition, Muni-Link, SimpleConsign or CatalogIt (404).
- **Recent LM filing counts:** the 2021–2026 counts are not captured; the 2020 figures are the latest found.

---

## Q3. Kill list: which candidates die, and why?

### Takeaway
Most legacy roll-up niches already have a well-rated modern challenger with traction, so the "clone the neglected incumbent" thesis fails on beatability. That covers moving, camps, rental, art galleries, consignment, museums, catering and screen printing. CACFP fails because the roll-up-owned incumbent is still well-rated.

### Cited Findings
- **Movers (Jonas: CompuMove, TechMate, Vans, EWS, QuickQube):**
  - Capterra moving category: SmartMoving 4.9★ (143), Chariot 5.0 (64), Movegistics 4.9 (43), MoveitPro 4.4 (97), Supermove 4.6 (18), Elromco 4.7 (22) — [Capterra moving](https://www.capterra.com/moving-software/).
  - Latka: SmartMoving $3.8M (est., Nov 2024), 46 employees — [Latka SmartMoving](https://getlatka.com/companies/smartmoving).
  - **Kill:** modern challengers dominate the review counts.
- **Summer camps (Jonas CampSite, myCAMPapp):** CampMinder 4.7 (256), CampSite 4.7 (148), UltraCamp 4.7 (23), CampDoc 4.8 (191), Sawyer 4.5 (319), Regpack 4.4 (372) — [Capterra camps](https://www.capterra.com/camp-management-software/). **Kill:** crowded and well rated, including the roll-up's own product.
- **Equipment and party rental (Volaris InTempo/UBS/Wynne; Point of Rental):**
  - Booqable 4.8 (1,195), Goodshuffle Pro 4.8 (157), TapGoods 4.9 (60), InflatableOffice 4.9 (76), Point of Rental 4.3 (149) — [Capterra equipment rental](https://www.capterra.com/equipment-rental-software/).
  - Point of Rental neglect does exist: "Declining service keeps me looking for new solutions" (Mar 24, 2026); "Speed, crashes, printing problems that happen daily" (May 31, 2023) — [Capterra Point of Rental](https://www.capterra.com/p/29074/Point-of-Rental-Software/reviews/).
  - **Kill:** challengers already capture switchers.
- **Art galleries (Volaris Artsystems, ArtBinder):** ArtCloud 4.8 (72), Artwork Archive 4.9 (110), Artlogic 4.7 (45), Artsystems 5.0 (26), ArtBinder 4.8 (4) — [Capterra art gallery](https://www.capterra.com/art-gallery-software/). **Kill:** modern options are well established, and the incumbent is well rated.
- **Consignment and resale:**
  - ConsignPro is now owned by SimpleConsign (competitor blog) — [ConsignCloud blog](https://consigncloud.com/blog/6-top-consignment-softwares-for-2026).
  - A SimpleConsign reviewer: "not as user friendly as ConsignPro… reporting… was much better when it was Consign[Pro]" (Oct 29, 2025) — [Capterra SimpleConsign](https://www.capterra.com/p/121828/SimpleConsign/reviews/).
  - A Ricochet owner: "They forced us to use Fortis… we have less than a month to force us to a new processor… we will be fined $100 a day" (Apr 24, 2026) — [Capterra Ricochet](https://www.capterra.com/p/136226/Ricochet-Consignment-Software/reviews/).
  - The category is well served: SimpleConsign 4.7 (356), ConsignPro 4.6 (434), Ricochet 4.7 (119), Circle-Hand 4.9 (84), ConsignCloud 4.6 (52), Aravenda 4.9 (19) — [Capterra consignment](https://www.capterra.com/consignment-software/).
  - **Kill:** well-rated cloud alternatives exist. Note that processor lock-in is a recurring roll-up tactic, shared with Storable.
- **Small museums (PastPerfect, independent):**
  - PastPerfect claims use "by over 12,000" institutions **[vendor; a cached snippet also shows 11,000]** — [PastPerfect](https://museumsoftware.com/).
  - "Clunky, on an out-dated platform… Most of my volunteers refuse to use it" (Feb 6, 2020); 4.2★ (17) — [Capterra PastPerfect](https://www.capterra.com/p/121813/PastPerfect/reviews/).
  - CatalogIt has 4.9★ (78), with 2026 reviews describing switching and migration ("They migrated our entire collection of 1500…", May 7, 2026) — [Capterra CatalogIt](https://www.capterra.com/p/183811/CatalogIt/reviews/).
  - **Kill:** a modern challenger is gaining traction, and the incumbent is not a roll-up.
- **CACFP child-care food program (Valsoft KidKare):** KidKare Food Program has 4.7★ (389). The negative quote "Improve your customer service. I feel taken advantage of" (Dec 8, 2025) is an outlier — [Capterra KidKare](https://www.capterra.com/p/166858/Kid-Kare/reviews/). **Kill:** a well-rated incumbent embedded in sponsor and state workflows.
- **Caterers (Caterease):**
  - "Would Not Purchase Again… plenty of options that are much easier to use" (Oct 21, 2026); "Outdated and not worth the money… $1800 a year" (Mar 12, 2020) — [Capterra Caterease](https://www.capterra.com/p/2280/Caterease/reviews/).
  - Alternatives are already strong: Total Party Planner 4.8 (153), Tripleseat 4.7 (576), Better Cater 4.8 (36), Flex Catering 4.9 (12), Perfect Venue 4.8 (82) — [Capterra catering](https://www.capterra.com/catering-software/).
  - **Kill.**
- **Screen printers (Printavo, Inktavo):**
  - "there's a 60% price increase coming… puts the annual cost $3500-$4000k". The poster was trialling YoPrint, "All of this for $2k less per year", and another member uses Teesom (Jul 14, 2022, older) — [The Shirt Board](https://www.theshirtboard.com/index.php/topic,26353.0.html).
  - Printavo has only 15 Capterra reviews, with the newest from 2022 — [Capterra Printavo](https://www.capterra.com/p/154421/Printavo/reviews/).
  - **Kill:** challengers already absorbed the price-hike switchers.
- **Funeral homes:** Osiris 4.7 (65), Parting Pro 4.6 (57), Halcyon 4.8 (38), Gather 4.9 (39), Passare 4.6 (13); cemeteries: PlotBox 4.7 (95), Chronicle 4.7 (60) — [Capterra funeral](https://www.capterra.com/funeral-home-software/). **Kill:** crowded with modern entrants.
- **Liquor stores (Jonas ICS / WineFetch):** the category is dominated by general POS: Square 4.6 (3,045), Lightspeed 4.0 (976), KORONA 4.7 (80) — [Capterra liquor POS](https://www.capterra.com/liquor-store-pos-software/). **Kill.**
- **Hardware, farm and rental retail (Volaris Windward System Five):**
  - 3.8★ (189): "This system is not worth the money, time, effort with no support" (Apr 4, 2022); "I wish I never heard of Windward Software" (Nov 17, 2020) — [Capterra Windward](https://www.capterra.com/p/43189/Windward-System-Five/reviews/).
  - **Kill:** a general SMB retail POS replacement market (Paladin 4.6, RetailEdge 4.8 in the same category list) — [Capterra liquor POS](https://www.capterra.com/liquor-store-pos-software/).
- **Grain elevators and ag retail (Volaris AGRIS/AgVision/Greenstone):** AGRIS 5.0 (2), AgVision 3.0 (1) on Capterra — [Capterra AGRIS](https://www.capterra.com/p/187241/Greenstone); [Capterra AgVision](https://www.capterra.com/p/2847/AgVision-Grain-Software/). **Downgraded to watch:** proven roll-up stacking, but there is too little review evidence and the build is too heavy (grain contracts, settlements, warehouse receipts).
- **Driving schools (not a roll-up niche):** fragmented small vendors, e.g. DrivingSchoolSoftware.com 5.0 (43), Total Drive 5.0 (30) — [Capterra driving school](https://www.capterra.com/driving-school-software/). **Not pursued:** no roll-up incumbent.

### Inferences
- The kill pattern is consistent. Wherever a niche has **thousands of owner-operated businesses that buy online** (movers, caterers, rental shops, screen printers), venture- or bootstrap-funded challengers arrived 5–10 years ago, and review counts now favour them.
- What remains are niches where buyers are **boards, volunteers or under-staffed public bodies** (chambers, union locals, fire departments, water districts). Their software is bought slowly, often through associations, and modern SaaS founders mostly avoid them. That is the opportunity, and also the main channel cost.

### Gaps
- Family entertainment centres (Clubspeed, LilYPad), cinemas (Omniterm), salons, martial arts, independent car rental and debt collection were screened from the portfolios but not checked against challengers. The search budget ran out. Treat them as **unassessed**, not killed.

---

## Q4. Channels: how do incumbents sell, and can a newcomer reach the buyers?

### Takeaway
Incumbents sell through quotes, contracts and associations:
- Chamber Nation uses multi-year terms and setup fees.
- ChamberMaster and SedonaOffice are "contact vendor".
- ESO works through account managers and state fire-data coordinators.
- Marketron runs webinars co-produced with a trade publication.

A newcomer can reach these buyers through the same associations and through comparison/alternative SEO. Union Impact's "UnionTrack … Alternative" page and 1-month free trial show the playbook already in use.

### Cited Findings
- Chamber Nation pricing is published with "1, 3 or 5-year term" and a phone line "855-ADD-Members" — [Chamber Nation pricing](https://www.chambernation.com/pricing).
- ChamberMaster pricing is custom-quoted, "starting at $3,900 annually" (via search summary) — [Capterra ChamberMaster](https://www.capterra.com/p/144469/ChamberMaster/). SedonaOffice is "Contact vendor" — [Capterra SedonaOffice](https://www.capterra.com/p/234356/SedonaOffice/).
- ESO tells Firehouse and Emergency Reporting users who are "ready to switch" to email their account manager — [ESO NERIS](https://www.eso.com/neris/). State fire marshals publish vendor and transition guidance, e.g. North Dakota's ER-to-ESO notice (via search summary) — [ND notice](https://www.firemarshal.nd.gov/news/data-reporting-option-north-dakota-fire-districts).
- Marketron co-hosted "The Radio Traffic System Landscape" webinar with Radio World — [Future B2B](https://events.futureb2b.com/on-demand/2467/the-radio-traffic-system-landscape-industry-perceptions-and-needs).
- Union Impact runs competitor-alternative SEO pages and a "1 Month Risk-Free Trial" — [Union Impact](https://unionimpact.com/uniontrack-dues-pac-payments-alternative/).
- ACCE represents 1,300 chambers and 9,000 chamber professionals, a concentrated channel — [ACCE about](https://secure.acce.org/pages/about-us/).

### Inferences
- **Most replicable channel:** chambers (S3). One association reaches 1,300 decision-makers; buyers search for alternatives online; switching is triggered by renewal dates on multi-year terms.
- **Hardest channel:** fire departments and water districts. Board and council approvals, procurement thresholds and state-level vendor relationships slow sales. Budget 6–12-month cycles.
- **Union locals** sit in between. Officer networks are tight and word-of-mouth is strong, but the "union-friendly vendor" trust requirement means founder credibility in labor circles is part of the channel.

### Gaps
- No association membership or sponsorship prices were gathered for ACCE, state fire associations or rural-water associations.
- No Facebook-group or forum sizes were measured. Reddit and Facebook were not reachable or searched in this session.
