"""
De-para de AS organizations -> (grupo controlador, país do controlador)
VERSÃO FILTRADA: apenas mapeamentos de confiança ALTA.

Regras desta versão
  - Mantido só o que é (a) mesma marca/nome da controladora, ou
    (b) controle societário confirmado em fonte (link no comentário).
  - Removido: controle duvidoso, entidade vendida, nome de AS ambíguo,
    ou país do controlador ambíguo (ver lista de removidos no fim).
  - "LINK PENDENTE" = relação societária amplamente documentada, mas sem
    fonte verificada nesta rodada; incluir referência antes de publicar.
  - país_controlador = país da sede da controladora final do grupo.
  - Os totais por grupo (+empresas, +receita) do arquivo anterior mudaram
    com as remoções e precisam ser recalculados.
  - Fatos societários valem para a data do instantâneo DNS. Se o snapshot
    for anterior a uma venda listada nos removidos, reavaliar a linha.

Uso:
    dp = pd.DataFrame.from_dict(DEPARA_AS_ORG, orient='index',
                                columns=['grupo', 'pais_controlador'])
    df = df.join(dp, on='as_org')
    df['grupo'] = df['grupo'].fillna(df['as_org'])
    df['pais_controlador'] = df['pais_controlador'].fillna(df['pais'])
"""

DEPARA_AS_ORG = {
    # ===== DigiCert | US =====
    "Vercara, LLC": ("DigiCert", "US"),  # aquisição concluída em set/2024 | https://www.digicert.com/news/digicert-completes-acquisition-of-vercara-strengthening-position-as-a-leader-in-digital-trust
    "Tiggee LLC": ("DigiCert", "US"),  # Tiggee = DNS Made Easy; aquisição em jun/2022 (não 2019) | https://www.digicert.com/news/digicert-acquires-dns-made-easy-extending-leadership-in-digital-trust-with-enterprise-grade-managed-dns-services

    # ===== GoDaddy | US =====
    # Host Europe Group (HEG) adquirido pela GoDaddy em 03/04/2017 (subsidiária integral)
    #   https://www.sec.gov/Archives/edgar/data/0001609711/000160971117000070/a991hegclosingpressrelease.htm
    # O AS44273 tem as-name GODADDY-DNS, org "Host Europe GmbH", registro DE:
    #   https://ipgeolocation.io/browse/asn/44273
    # e anuncia o IPv6 dos servidores nsXX.domaincontrol.com (IPv4 sai pelo AS26496 GoDaddy.com, LLC):
    #   https://bgp.he.net/dns/NS42.DOMAINCONTROL.com
    "Host Europe GmbH": ("GoDaddy", "US"),  # [Alta] ver evidências acima
    "GoDaddy.com, LLC": ("GoDaddy", "US"),  # [Alta] mesma marca
    "Go Daddy Netherlands B.V.": ("GoDaddy", "US"),  # [Alta] mesma marca (prefixos dentro de ASes da Host Europe)
    "123 REG LIMITED": ("GoDaddy", "US"),  # [Alta] 123 Reg é marca do HEG | https://onlinedomain.com/2017/04/04/domain-name-news/godaddy-completes-acquisition-host-europe-group/

    # ===== Akamai | US =====
    "Akamai International B.V.": ("Akamai", "US"),  # mesma marca
    "Akamai Connected Cloud": ("Akamai", "US"),  # mesma marca (ex-Linode)
    "Akamai Technologies, Inc.": ("Akamai", "US"),  # mesma marca

    # ===== Alibaba | CN =====
    "Alibaba (US) Technology Co., Ltd.": ("Alibaba", "CN"),  # mesma marca
    "Alibaba Cloud (Singapore) Private Limited": ("Alibaba", "CN"),  # mesma marca; registro SG, controlador CN
    "Hangzhou Alibaba Advertising Co.,Ltd.": ("Alibaba", "CN"),  # mesma marca

    # ===== China Telecom | CN =====
    "No.31,Jin-rong Street": ("China Telecom", "CN"),  # WHOIS do AS4134 (CHINANET-BACKBONE) | https://stat.ripe.net/AS4134
    "China Telecom (Group)": ("China Telecom", "CN"),  # mesma marca
    "IDC, China Telecommunications Corporation": ("China Telecom", "CN"),  # mesma marca
    "CHINANET Nanjing Jishan IDC network": ("China Telecom", "CN"),  # CHINANET = backbone China Telecom
    "CHINANET SiChuan Telecom Internet Data Center": ("China Telecom", "CN"),  # idem
    "CHINANET Guangdong province network": ("China Telecom", "CN"),  # idem
    "CHINANET Guangdong province Dongguan MAN network": ("China Telecom", "CN"),  # idem
    "China Telecom Next Generation Carrier Network": ("China Telecom", "CN"),  # mesma marca
    "China Telecom Beijing Tianjin Hebei Big Data Industry Park Branch": ("China Telecom", "CN"),  # mesma marca
    "CHINANET Guangdong province Shenzhen MAN network": ("China Telecom", "CN"),  # idem
    "CHINATELECOM Jiangsu province Changzhou 5G network": ("China Telecom", "CN"),  # mesma marca
    "CHINATELECOM Hubei province Wuhan 5G network": ("China Telecom", "CN"),  # mesma marca
    "CHINATELECOM Fujian province Fuzhou 5G network": ("China Telecom", "CN"),  # mesma marca
    "CHINANET SHAANXI province Cloud Base network": ("China Telecom", "CN"),  # idem
    "CHINANET Liaoning province Dalian MAN network": ("China Telecom", "CN"),  # idem
    "CHINANET Jiangx province IDC network": ("China Telecom", "CN"),  # idem
    "Shijiazhuang IDC network, CHINANET Hebei province": ("China Telecom", "CN"),  # idem

    # ===== China Unicom | CN =====
    "China Unicom Beijing Province Network": ("China Unicom", "CN"),  # mesma marca
    "China Unicom Guangdong IP network": ("China Unicom", "CN"),
    "CHINA UNICOM China169 Backbone": ("China Unicom", "CN"),
    "China Unicom Shanghai FuTe IDC network": ("China Unicom", "CN"),
    "China Unicom Shanghai network": ("China Unicom", "CN"),
    "China Unicom Shenzen network": ("China Unicom", "CN"),
    "China Unicom IP network China169 Guangdong province": ("China Unicom", "CN"),
    "China Unicom IP network": ("China Unicom", "CN"),
    "CHINA UNICOM Industrial Internet Backbone": ("China Unicom", "CN"),
    "China Unicom Guangzhou network": ("China Unicom", "CN"),
    "China Unicom Global": ("China Unicom", "CN"),

    # ===== IONOS / United Internet | DE =====
    "IONOS SE": ("IONOS / United Internet", "DE"),  # mesma marca
    "Fasthosts Internet Limited": ("IONOS / United Internet", "DE"),  # subsidiária IONOS | LINK PENDENTE
    "Strato GmbH": ("IONOS / United Internet", "DE"),  # subsidiária IONOS | LINK PENDENTE
    "1&1 Versatel GmbH": ("IONOS / United Internet", "DE"),  # grupo 1&1 / United Internet | LINK PENDENTE

    # ===== China Mobile | CN =====
    "China Mobile communications corporation": ("China Mobile", "CN"),  # mesma marca
    "China Mobile Communications Group Co., Ltd.": ("China Mobile", "CN"),
    "China Mobile Communicaitons Corporation": ("China Mobile", "CN"),
    "Shanghai Mobile Communications Co.,Ltd.": ("China Mobile", "CN"),  # filial provincial
    "Hebei Mobile Communication Company Limited": ("China Mobile", "CN"),  # filial provincial
    "Shandong Mobile Communication Company Limited": ("China Mobile", "CN"),  # filial provincial
    "China TieTong Telecommunications Corporation": ("China Mobile", "CN"),  # incorporada à China Mobile em 2008 | LINK PENDENTE

    # ===== Tencent | CN =====
    "Tencent Building, Kejizhongyi Avenue": ("Tencent", "CN"),  # endereço da sede no WHOIS
    "Shenzhen Tencent Computer Systems Company Limited": ("Tencent", "CN"),  # mesma marca

    # ===== team.blue | BE =====
    "REGISTER S.P.A.": ("Hosting (team.blue)", "BE"),  # controladora final declarada: team.blue | https://register.it/company/?lang=en
    "TEAM BLUE INTERNET SERVICES UK LIMITED": ("Hosting (team.blue)", "BE"),  # mesma marca
    "Combell NV": ("Hosting (team.blue)", "BE"),  # team.blue formada pela fusão Combell+TransIP (2019) | https://tech.eu/2019/06/12/combell-transip-merger-team-blue/
    "team.blue Denmark A/S": ("Hosting (team.blue)", "BE"),  # mesma marca
    "Team Blue Carrier Limited": ("Hosting (team.blue)", "BE"),  # mesma marca

    # ===== NTT | JP =====
    "NTT DOCOMO BUSINESS,Inc.": ("NTT", "JP"),  # mesma marca
    "NTT PC Communications, Inc.": ("NTT", "JP"),
    "NTT SmartConnect Corporation": ("NTT", "JP"),
    "Arcnet NTT MSC ISP": ("NTT", "JP"),
    "NTT DATA Services Holdings Corporation": ("NTT", "JP"),
    "NTT DATA CORPORATION": ("NTT", "JP"),
    "NTT COMMUNICATIONS INDIA NETWORK SERVICES PRIVATE LIMITED": ("NTT", "JP"),
    "NTT-ME Corporation": ("NTT", "JP"),
    "ASN - NTT SINGAPORE PTE LTD": ("NTT", "JP"),
    "Dimension Data": ("NTT", "JP"),  # adquirida pela NTT em 2010 | LINK PENDENTE

    # ===== KDDI | JP =====
    "KDDI CORPORATION": ("KDDI", "JP"),
    "KDDI Web Communications Inc.": ("KDDI", "JP"),

    # ===== F5 | US =====
    "F5, Inc.": ("F5", "US"),
    "F5 Networks SARL": ("F5", "US"),

    # ===== Chunghwa Telecom | TW =====
    "Data Communication Business Group": ("Chunghwa Telecom", "TW"),  # AS3462 HINET, org Chunghwa Telecom | https://ipgeolocation.io/browse/asn/3462
    "Chunghwa Telecom Global, INC": ("Chunghwa Telecom", "TW"),  # mesma marca

    # ===== Telia | SE =====
    "Telia Company AB": ("Telia", "SE"),
    "Telia Finland Oyj": ("Telia", "SE"),
    "Telia Norge AS": ("Telia", "SE"),  # não há evidência de venda; Telia Norway segue operando | https://telecoms.com/operator-ecosystem/telia-to-buy-6-000-globalconnect-customers
    "Telia Eesti AS": ("Telia", "SE"),
    "Telia Lietuva, AB": ("Telia", "SE"),
    "Telia Cygate Oy": ("Telia", "SE"),

    # ===== LG Group | KR =====
    "LG DACOM Corporation": ("LG Group", "KR"),  # LG DACOM = LG Uplus
    "LG CNS": ("LG Group", "KR"),
    "LG HelloVision Corp.": ("LG Group", "KR"),

    # ===== Tata Group | IN =====
    "TATA COMMUNICATIONS (AMERICA) INC": ("Tata Group", "IN"),
    "TATA Communications formerly VSNL is Leading ISP": ("Tata Group", "IN"),
    "TCS eServe Limited": ("Tata Group", "IN"),
    "Tata Teleservices Maharashtra Ltd": ("Tata Group", "IN"),

    # ===== Deutsche Telekom | DE =====
    "Deutsche Telekom AG": ("Deutsche Telekom", "DE"),
    "T-Mobile Austria GmbH": ("Deutsche Telekom", "DE"),
    "Deutsche Telekom Global Business Solutions GmbH": ("Deutsche Telekom", "DE"),
    "T-Mobile Polska S.A.": ("Deutsche Telekom", "DE"),
    "Ote SA (Hellenic Telecommunications Organisation)": ("Deutsche Telekom", "DE"),  # DT majoritária | LINK PENDENTE
    "Magyar Telekom Plc.": ("Deutsche Telekom", "DE"),  # DT majoritária | LINK PENDENTE

    # ===== Rackspace | US =====
    "Rackspace Ltd.": ("Rackspace", "US"),
    "Rackspace Hosting": ("Rackspace", "US"),

    # ===== GMO Internet Group | JP =====
    "GMO Internet, Inc.": ("GMO Internet Group", "JP"),
    "GMO-Z.com Runsystem Joint Stock Company": ("GMO Internet Group", "JP"),
    "GMO GlobalSign Holdings K.K.": ("GMO Internet Group", "JP"),
    "GMO NetIRD, Inc.": ("GMO Internet Group", "JP"),

    # ===== UpCloud | FI =====
    "UpCloud Ltd": ("UpCloud", "FI"),
    "UpCloud USA Inc": ("UpCloud", "FI"),

    # ===== Thales | FR =====
    "Incapsula Inc": ("Thales", "FR"),  # Incapsula = Imperva; Imperva adquirida pela Thales (dez/2023) | https://www.thalesgroup.com/en/news-centre/press-releases/thales-completes-acquisition-imperva-creating-global-leader
    "Thales Services Numeriques SAS": ("Thales", "FR"),

    # ===== Orange | FR =====
    "Orange Business Services SA": ("Orange", "FR"),
    "ORANGE BUSINESS SERVICES U.S. Inc.": ("Orange", "FR"),
    "Orange S.A.": ("Orange", "FR"),
    "Orange Polska Spolka Akcyjna": ("Orange", "FR"),
    "Orange Business Communications Technology Limited": ("Orange", "FR"),
    "Orange Romania S.A.": ("Orange", "FR"),

    # ===== Lumen | US =====
    "Level 3 Parent, LLC": ("Lumen", "US"),  # Level 3 + CenturyLink = Lumen | LINK PENDENTE
    "CenturyLink Communications, LLC": ("Lumen", "US"),  # idem | LINK PENDENTE

    # ===== Leaseweb | NL =====
    "LeaseWeb Netherlands B.V.": ("Leaseweb", "NL"),
    "Leaseweb Deutschland GmbH": ("Leaseweb", "NL"),
    "Leaseweb USA, Inc.": ("Leaseweb", "NL"),
    "LEASEWEB SINGAPORE PTE. LTD.": ("Leaseweb", "NL"),
    "LEASEWEB HONG KONG LIMITED": ("Leaseweb", "NL"),
    "Leaseweb Canada Inc.": ("Leaseweb", "NL"),

    # ===== SK Group | KR =====
    "SK Broadband Co Ltd": ("SK Group", "KR"),
    "SK Telecom": ("SK Group", "KR"),

    # ===== Telefónica | ES =====
    "TELEFONICA DE ESPANA S.A.U.": ("Telefónica", "ES"),
    "TELEFONICA BRASIL S.A": ("Telefónica", "ES"),
    "acens Technologies, S.L.": ("Telefónica", "ES"),  # acens adquirida pela Telefónica | LINK PENDENTE

    # ===== VNPT | VN =====
    "Vietnam Posts and Telecommunications (VNPT)": ("VNPT", "VN"),
    "VNPT Corp": ("VNPT", "VN"),
    "VIETNAM POSTS AND TELECOMMUNICATIONS GROUP": ("VNPT", "VN"),

    # ===== Far EasTone | TW =====
    "Far EastTone Telecommunication Co., Ltd.": ("Far EasTone", "TW"),
    "Asia Pacific Telecom": ("Far EasTone", "TW"),  # fusão concluída dez/2023, FET sucessora | https://www.analysysmason.com/about-us/news/newsletter/asia-pacific-mergers/
    "Asia Pacific Broadband Fixed Lines Co., Ltd.": ("Far EasTone", "TW"),  # grupo APT, idem | https://www.taipeitimes.com/News/biz/archives/2022/02/26/2003773774

    # ===== Iliad | FR =====
    "Free SAS": ("Iliad", "FR"),
    "Free Pro SAS": ("Iliad", "FR"),
    "P4 Sp. z o.o.": ("Iliad", "FR"),  # P4 = Play, controlada pela Iliad desde 2020 | https://en.wikipedia.org/wiki/Play_(telecommunications)
    "Scaleway SAS": ("Iliad", "FR"),  # braço de cloud da Iliad | LINK PENDENTE

    # ===== PCCW / HKT | HK =====
    "PCCW IMS Ltd (PCCW Business Internet Access)": ("PCCW / HKT", "HK"),
    "HKT Limited": ("PCCW / HKT", "HK"),
    "PCCW Global (HK) Ltd.": ("PCCW / HKT", "HK"),

    # ===== América Movil | MX =====
    "UNINET": ("América Movil", "MX"),  # rede da Telmex | LINK PENDENTE
    "Triara.com S.A. de C.V.": ("América Movil", "MX"),  # data center da Telmex | LINK PENDENTE
    "CLARO S.A.": ("América Movil", "MX"),  # marca Claro | LINK PENDENTE
    "Telmex Colombia S.A.": ("América Movil", "MX"),  # Claro Colombia | LINK PENDENTE

    # ===== Exabytes | MY =====
    "Exa Bytes Network Sdn.Bhd.": ("Exabytes", "MY"),
    "Exabytes Network (Singapore) Pte. Ltd.": ("Exabytes", "MY"),
    "PT. EXABYTES NETWORK INDONESIA": ("Exabytes", "MY"),

    # ===== Vodafone Group | GB =====
    "Vodafone Net Iletisim Hizmetler AS": ("Vodafone Group", "GB"),  # Vodafone Turquia
    "Vodafone Group Services GmbH": ("Vodafone Group", "GB"),
    "Vodacom": ("Vodafone Group", "GB"),  # Vodafone majoritária na Vodacom | LINK PENDENTE

    # ===== Huawei | CN =====
    "Huawei Cloud Service data center": ("Huawei", "CN"),
    "HUAWEI CLOUDS": ("Huawei", "CN"),

    # ===== Ooredoo | QA =====
    "Ooredoo Q.S.C.": ("Ooredoo", "QA"),
    "NATIONAL MOBILE TELECOMMUNICATIONS COMPANY K.S.C.P.": ("Ooredoo", "QA"),  # NMTC = Ooredoo Kuwait, membro do grupo | https://www.gsma.com/get-involved/gsma-membership/gsma_orgs/national-mobile-telecommunications-company-k-s-c/

    # ===== Zayo | US =====
    "Zayo Infrastructure France SA": ("Zayo", "US"),
    "Zayo Bandwidth": ("Zayo", "US"),
    "Latisys-Chicago, LLC": ("Zayo", "US"),  # aquisição concluída fev/2015 (não 2017) | https://www.sec.gov/Archives/edgar/data/0001608249/000119312515058388/d879167dex991.htm

    # ===== CERNET | CN =====
    "China Education and Research Network Center": ("CERNET", "CN"),
    "China Next Generation Internet CERNET2": ("CERNET", "CN"),

    # ===== Newfold Digital | US =====
    "Newfold Digital, Inc.": ("Newfold Digital", "US"),
    "Network Solutions, LLC": ("Newfold Digital", "US"),  # marca Newfold desde 2021 | https://newfold.com/newsroom/clearlake-completes-acquisition-of-endurance-international-group
    "Unified Layer": ("Newfold Digital", "US"),  # rede da Bluehost (ex-Endurance) | LINK PENDENTE

    # ===== Telenor | NO =====
    "Telenor Sverige AB": ("Telenor", "NO"),
    "Telenor Norge AS": ("Telenor", "NO"),
    "DNA Oyj": ("Telenor", "NO"),  # controle desde ago/2019 | https://www.telenor.com/media/newsroom/archive/telenor-completes-dna-transaction-announces-mandatory-tender-offer-for-remaining-shares-in-dna/

    # ===== Telstra | AU =====
    "Telstra Limited": ("Telstra", "AU"),
    "Telstra Global": ("Telstra", "AU"),

    # ===== Polsat (Cyfrowy Polsat) | PL =====
    "Cyfrowy Polsat S.A.": ("Polsat (Cyfrowy Polsat)", "PL"),
    "Netia SA": ("Polsat (Cyfrowy Polsat)", "PL"),  # controle adquirido em mai/2018 | https://grupapolsatplus.pl/en/taxonomy/term/38?page=6
    "Polkomtel Sp. z o.o.": ("Polsat (Cyfrowy Polsat)", "PL"),  # operadora Plus, grupo Polsat | LINK PENDENTE

    # ===== DTS Systeme | DE =====
    "DTS Systeme GmbH": ("DTS Systeme", "DE"),
    "DTS Systeme Muenster GmbH": ("DTS Systeme", "DE"),

    # ===== Hanwha | KR =====
    "HANWHA Corp. Information Service div.": ("Hanwha", "KR"),
    "Hanwha Ocean Co., Ltd.": ("Hanwha", "KR"),

    # ===== PTT | TH =====
    "PTT Digital Solutions Company Limited": ("PTT", "TH"),
    "PTT Global Chemical Public Company Limited": ("PTT", "TH"),

    # ===== WIIT | IT =====
    "WIIT AG": ("WIIT", "IT"),
    "WIIT S.p.A.": ("WIIT", "IT"),

    # ===== Altice USA | US =====
    "Cablevision Systems Corp.": ("Altice USA", "US"),  # Cablevision = Altice USA | LINK PENDENTE
    "Cablevision Lightpath LLC": ("Altice USA", "US"),  # Altice USA mantém 50,01% e o controle | https://investors.alticeusa.com/news-events/press-releases/detail/35/altice-usa-announces-closing-of-sale-of-49-99-of-lightpath

    # ===== UBS | CH =====
    "UBS Group AG": ("UBS", "CH"),
    "UBS AG": ("UBS", "CH"),

    # ===== Marsh McLennan | US =====
    "Marsh Limited": ("Marsh McLennan", "US"),
    "Marsh Inc.": ("Marsh McLennan", "US"),
    "Marsh & McLennan Companies, Inc.": ("Marsh McLennan", "US"),

    # ===== Mercedes-Benz | DE =====
    "MERCEDES-BENZ USA, LLC": ("Mercedes-Benz", "DE"),
    "Mercedes-Benz Singapore Pte. Ltd.": ("Mercedes-Benz", "DE"),
    "Mercedes-Benz Group AG": ("Mercedes-Benz", "DE"),

    # ===== Pearson | GB =====
    "NCS Pearson Inc.": ("Pearson", "GB"),
    "Pearson Shared Services Ltd": ("Pearson", "GB"),
    "Pearson Group": ("Pearson", "GB"),

    # ===== Publicis (Re:Sources) | FR =====
    "LION RESOURCES, INC.": ("Publicis (Re:Sources)", "FR"),  # Re:Sources = serviços compartilhados da Publicis | LINK PENDENTE
    "PG Lion ReSources Aust Pty Ltd": ("Publicis (Re:Sources)", "FR"),  # idem | LINK PENDENTE
    "Re:Sources France SAS": ("Publicis (Re:Sources)", "FR"),  # idem | LINK PENDENTE

    # ===== RELX | GB =====
    "RELX inc.": ("RELX", "GB"),
    "Elsevier Ltd": ("RELX", "GB"),
    "Elsevier Limited": ("RELX", "GB"),

    # ===== Turkcell | TR =====
    "TURKCELL ILETISIM HIZMETLERI A.S.": ("Turkcell", "TR"),
    "Superonline Iletisim Hizmetleri A.S.": ("Turkcell", "TR"),  # subsidiária 100% Turkcell | https://www.prnewswire.co.uk/news-releases/turkcell-superonline-bridges-europe-asia-and-middle-east-to-turn-istanbul-into-an-internet-hub-171481141.html

    # ===== Volvo | SE =====
    "Volvo Information Technology AB": ("Volvo", "SE"),
    "Volvo Group North America, Inc.": ("Volvo", "SE"),

    # ===== XL Axiata | ID =====
    "PT XL Axiata Tbk": ("XL Axiata", "ID"),
    "PT XL Axiata": ("XL Axiata", "ID"),
    "Linknet ASN": ("XL Axiata", "ID"),  # Axiata/XL adquiriram 66,03% da Link Net (jun/2022) | https://www.axiata.com/media/news/2022/axiata-and-xl-axiata-successfully-complete-acquisition-6603-link-nets-shares

    # ===== Telkom SA | ZA =====
    "Telkom SA Ltd.": ("Telkom SA", "ZA"),
    "Business Connexion Communications": ("Telkom SA", "ZA"),  # BCX 100% Telkom desde 2015 | https://telkom.co.za/ir/financial/annual-results-2016/notes/note16.shtml

    # ===== Grupos de mesmo nome (evidência = o próprio nome) =====
    "Accenture UK Limited": ("Accenture", "IE"),
    "Accenture LLP": ("Accenture", "IE"),
    "ARAMARK": ("Aramark", "US"),
    "Aramark Services, Inc.": ("Aramark", "US"),
    "Eviden Netherlands B.V.": ("Atos", "FR"),  # Eviden é marca da Atos | LINK PENDENTE
    "Atos France SAS": ("Atos", "FR"),
    "Robert Bosch GmbH": ("Bosch", "DE"),
    "Robert Bosch Gesellschaft mit Beschraenkter Haftung": ("Bosch", "DE"),
    "CS LOXINFO PUBLIC COMPANY LIMITED": ("CS Loxinfo", "TH"),
    "POPIDC powered by CSLoxinfo": ("CS Loxinfo", "TH"),
    "Charter Communications LLC": ("Charter Communications", "US"),
    "Charter Communications Inc": ("Charter Communications", "US"),
    "Cogeco Connexion inc": ("Cogeco", "CA"),
    "Cogeco Connexion Inc.": ("Cogeco", "CA"),
    "Deutsche Bank APAC RHO in Singapore Internet AS": ("Deutsche Bank", "DE"),
    "Deutsche Bank AG": ("Deutsche Bank", "DE"),
    "Deutsche Boerse AG": ("Deutsche Börse", "DE"),
    "Clearstream Services S.A.": ("Deutsche Börse", "DE"),  # Clearstream é da Deutsche Börse | LINK PENDENTE
    "Dustin Sverige AB": ("Dustin", "SE"),
    "Dustin NL B.V.": ("Dustin", "SE"),
    "Experian": ("Experian", "IE"),  # sede em Dublin (incorporada em Jersey)
    "Experian International Unlimited": ("Experian", "IE"),
    "First Advantage Corporation": ("First Advantage", "US"),
    "FIRST ADVANTAGE GLOBAL OPERATING CENTER PRIVATE LIMITED": ("First Advantage", "US"),
    "Ford Motor Company Limited": ("Ford", "US"),
    "Ford Motor Company": ("Ford", "US"),
    "GIGAS HOSTING USA, LLC": ("Gigas", "ES"),
    "GIGAS HOSTING S.A.": ("Gigas", "ES"),
    "Grifols S.A.": ("Grifols", "ES"),
    "Grifols Inc.": ("Grifols", "ES"),
    "IQVIA SOLUTIONS HQ LTD": ("IQVIA", "US"),
    "IQVIA Holdings Inc": ("IQVIA", "US"),
    "Interactive Brokers LLC": ("Interactive Brokers", "US"),
    "Interactive Brokers Corp": ("Interactive Brokers", "US"),
    "LFDJ-AS": ("La Française des Jeux", "FR"),
    "La Francaise des Jeux": ("La Française des Jeux", "FR"),
    "M247 Ltd": ("M247", "GB"),
    "M247 Europe SRL": ("M247", "GB"),
    "METTLER-TOLEDO INTERNATIONAL INC., Wilmington, Delaware, Greifensee Branch": ("Mettler-Toledo", "US"),
    "Mettler-Toledo LLC": ("Mettler-Toledo", "US"),
    "NETEASE HONG KONG LIMITED": ("NetEase", "CN"),
    "NetEase Building No.16 Ke Yun Road,": ("NetEase", "CN"),  # endereço da sede no WHOIS
    "Novartis Pharmaceuticals": ("Novartis", "CH"),
    "Novartis AG": ("Novartis", "CH"),
    "OWENS CORNING FRANCE SAS": ("Owens Corning", "US"),
    "Owens-Corning": ("Owens Corning", "US"),
    "Shell Information Technology International, Inc.": ("Shell", "GB"),
    "Shell Information Technology International B.V.": ("Shell", "GB"),
    "SITEONE LANDSCAPE SUPPLY, LLC": ("SiteOne", "US"),
    "SiteOne Landscape Supply": ("SiteOne", "US"),
    "TAURON WYTWARZANIE SPOLKA AKCYJNA": ("TAURON", "PL"),
    "TAURON Dystrybucja S.A.": ("TAURON", "PL"),
    "Vaisala Oyj": ("Vaisala", "FI"),
    "Vaisala Inc": ("Vaisala", "FI"),
    "VeriSign Infrastructure & Operations": ("VeriSign", "US"),
    "VeriSign Global Registry Services": ("VeriSign", "US"),
    "VISTEON CORPORATION": ("Visteon", "US"),
    "Visteon Corporation": ("Visteon", "US"),
    "Vodafone Mobile Services Ltd": ("Vodafone Idea", "IN"),  # Vodafone Group minoritário; controle indiano
    "Vodafone Idea Ltd": ("Vodafone Idea", "IN"),
    "Zoho Corporation PTY LTD": ("Zoho", "IN"),
    "ZOHO": ("Zoho", "IN"),
}

# ---------------------------------------------------------------------------
