"""
De-para de AS organizations -> (grupo controlador, país do controlador).

Critério de inclusão (por grupo, comparado ao maior AS individual do grupo):
  - ganho de empresas (soma - maior AS) >= 50, OU
  - receita somada >= 110% da receita do maior AS.

Comentário de cada linha: [confiança] evidência | nota
Confiança 'Média' = depende de aquisição/controle societário; verificar em fonte primária.

Uso:
    # from_dict(orient='index'): cada chave vira uma linha e a tupla vira as colunas
    dp = pd.DataFrame.from_dict(DEPARA_AS_ORG, orient='index',
                                columns=['grupo', 'pais_controlador'])
    # join(on=...) casa a coluna as_org do df com o índice do dp (left join)
    df = df.join(dp, on='as_org')
    # quem não está no de-para fica NaN: mantém o próprio nome e o país de registro
    df['grupo'] = df['grupo'].fillna(df['as_org'])
    df['pais_controlador'] = df['pais_controlador'].fillna(df['pais'])
"""

DEPARA_AS_ORG = {
    # ===== DigiCert | país controlador: US | 2 AS orgs | +238 empresas, +23% receita =====
    "Vercara, LLC": ("DigiCert", "US"),  # [Média] controle societário (conhecimento — verificar) | Vercara (ex-Neustar UltraDNS) adquirida pela DigiCert em 2024
    "Tiggee LLC": ("DigiCert", "US"),  # [Média] controle societário (conhecimento — verificar) | Tiggee = DNS Made Easy, adquirida pela DigiCert em 2019

    # ===== Akamai | país controlador: US | 3 AS orgs | +58 empresas, +1% receita =====
    "Akamai International B.V.": ("Akamai", "US"),  # [Alta] mesma marca / subsidiária | Akamai Connected Cloud = antiga Linode (adquirida 2022)
    "Akamai Connected Cloud": ("Akamai", "US"),  # [Alta] mesma marca / subsidiária | Akamai Connected Cloud = antiga Linode (adquirida 2022)
    "Akamai Technologies, Inc.": ("Akamai", "US"),  # [Alta] mesma marca / subsidiária | Akamai Connected Cloud = antiga Linode (adquirida 2022)

    # ===== Alibaba | país controlador: CN | 3 AS orgs | +269 empresas, +126% receita =====
    "Alibaba (US) Technology Co., Ltd.": ("Alibaba", "CN"),  # [Alta] mesma marca / subsidiária | Alibaba Cloud (Singapore) registrado em SG, controlador chinês
    "Alibaba Cloud (Singapore) Private Limited": ("Alibaba", "CN"),  # [Alta] mesma marca / subsidiária | Alibaba Cloud (Singapore) registrado em SG, controlador chinês
    "Hangzhou Alibaba Advertising Co.,Ltd.": ("Alibaba", "CN"),  # [Alta] mesma marca / subsidiária | Alibaba Cloud (Singapore) registrado em SG, controlador chinês

    # ===== China Telecom | país controlador: CN | 18 AS orgs | +269 empresas, +141% receita =====
    "No.31,Jin-rong Street": ("China Telecom", "CN"),  # [Média] controle societário (conhecimento — verificar) | endereço da sede da China Telecom no WHOIS (AS4134) — verificar
    "China Telecom (Group)": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "IDC, China Telecommunications Corporation": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINANET Nanjing Jishan IDC network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "CHINANET SiChuan Telecom Internet Data Center": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "CHINANET Guangdong province network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "Chongqing Telecom": ("China Telecom", "CN"),  # [Média] controle societário (conhecimento — verificar) | provável filial provincial da China Telecom
    "CHINANET Guangdong province Dongguan MAN network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "China Telecom Next Generation Carrier Network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Telecom Beijing Tianjin Hebei Big Data Industry Park Branch": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINANET Guangdong province Shenzhen MAN network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "CHINATELECOM Jiangsu province Changzhou 5G network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINATELECOM Hubei province Wuhan 5G network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINATELECOM Fujian province Fuzhou 5G network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINANET SHAANXI province Cloud Base network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "CHINANET Liaoning province Dalian MAN network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "CHINANET Jiangx province IDC network": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom
    "Shijiazhuang IDC network, CHINANET Hebei province": ("China Telecom", "CN"),  # [Alta] mesma marca / subsidiária | CHINANET é o backbone da China Telecom

    # ===== China Unicom | país controlador: CN | 11 AS orgs | +249 empresas, +154% receita =====
    "China Unicom Beijing Province Network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Guangdong IP network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINA UNICOM China169 Backbone": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Shanghai FuTe IDC network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Shanghai network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Shenzen network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom IP network China169 Guangdong province": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom IP network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "CHINA UNICOM Industrial Internet Backbone": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Guangzhou network": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária
    "China Unicom Global": ("China Unicom", "CN"),  # [Alta] mesma marca / subsidiária

    # ===== IONOS / United Internet | país controlador: DE | 4 AS orgs | +105 empresas, +345% receita =====
    "Fasthosts Internet Limited": ("IONOS / United Internet", "DE"),  # [Média] controle societário (conhecimento — verificar) | Fasthosts é subsidiária da IONOS
    "IONOS SE": ("IONOS / United Internet", "DE"),  # [Alta] mesma marca / subsidiária
    "Strato GmbH": ("IONOS / United Internet", "DE"),  # [Média] controle societário (conhecimento — verificar) | Strato é subsidiária da IONOS
    "1&1 Versatel GmbH": ("IONOS / United Internet", "DE"),  # [Média] controle societário (conhecimento — verificar) | 1&1 é do grupo United Internet

    # ===== China Mobile | país controlador: CN | 7 AS orgs | +109 empresas, +324% receita =====
    "China Mobile communications corporation": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária
    "China Mobile Communications Group Co., Ltd.": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária
    "China Mobile Communicaitons Corporation": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária
    "Shanghai Mobile Communications Co.,Ltd.": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária | filial provincial
    "Hebei Mobile Communication Company Limited": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária | filial provincial
    "China TieTong Telecommunications Corporation": ("China Mobile", "CN"),  # [Média] controle societário (conhecimento — verificar) | China Tietong incorporada à China Mobile
    "Shandong Mobile Communication Company Limited": ("China Mobile", "CN"),  # [Alta] mesma marca / subsidiária | filial provincial

    # ===== Tencent | país controlador: CN | 2 AS orgs | +83 empresas, +58% receita =====
    "Tencent Building, Kejizhongyi Avenue": ("Tencent", "CN"),  # [Alta] mesma marca / subsidiária | 'Tencent Building...' é endereço no WHOIS
    "Shenzhen Tencent Computer Systems Company Limited": ("Tencent", "CN"),  # [Alta] mesma marca / subsidiária | 'Tencent Building...' é endereço no WHOIS

    # ===== Hosting (team.blue) | país controlador: BE | 7 AS orgs | +80 empresas, +581% receita =====
    "REGISTER S.P.A.": ("Hosting (team.blue)", "BE"),  # [Média] controle societário (conhecimento — verificar) | Register.it integrado ao team.blue — verificar
    "TEAM BLUE INTERNET SERVICES UK LIMITED": ("Hosting (team.blue)", "BE"),  # [Alta] mesma marca / subsidiária
    "Combell NV": ("Hosting (team.blue)", "BE"),  # [Média] controle societário (conhecimento — verificar) | Combell é team.blue; mesma assinatura de receita que Easyhost
    "Easyhost BVBA": ("Hosting (team.blue)", "BE"),  # [Média] controle societário (conhecimento — verificar) | Easyhost faz parte do Combell Group (team.blue)
    "team.blue Denmark A/S": ("Hosting (team.blue)", "BE"),  # [Alta] mesma marca / subsidiária
    "Hostpoint AG": ("Hosting (team.blue)", "BE"),  # [Média] controle societário (conhecimento — verificar) | Hostpoint integrado ao team.blue — verificar
    "Team Blue Carrier Limited": ("Hosting (team.blue)", "BE"),  # [Alta] mesma marca / subsidiária

    # ===== NTT | país controlador: JP | 10 AS orgs | +32 empresas, +65% receita =====
    "NTT DOCOMO BUSINESS,Inc.": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "NTT PC Communications, Inc.": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "Dimension Data": ("NTT", "JP"),  # [Média] controle societário (conhecimento — verificar) | Dimension Data integrada à NTT
    "NTT SmartConnect Corporation": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "Arcnet NTT MSC ISP": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "NTT DATA Services Holdings Corporation": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "NTT DATA CORPORATION": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "NTT COMMUNICATIONS INDIA NETWORK SERVICES PRIVATE LIMITED": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "NTT-ME Corporation": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária
    "ASN - NTT SINGAPORE PTE LTD": ("NTT", "JP"),  # [Alta] mesma marca / subsidiária

    # ===== KDDI | país controlador: JP | 2 AS orgs | +26 empresas, +35% receita =====
    "KDDI CORPORATION": ("KDDI", "JP"),  # [Alta] mesma marca / subsidiária
    "KDDI Web Communications Inc.": ("KDDI", "JP"),  # [Alta] mesma marca / subsidiária

    # ===== F5 | país controlador: US | 2 AS orgs | +3 empresas, +11% receita =====
    "F5, Inc.": ("F5", "US"),  # [Alta] mesma marca / subsidiária
    "F5 Networks SARL": ("F5", "US"),  # [Alta] mesma marca / subsidiária

    # ===== Chunghwa Telecom | país controlador: TW | 2 AS orgs | +1 empresas, +10% receita =====
    "Data Communication Business Group": ("Chunghwa Telecom", "TW"),  # [Média] controle societário (conhecimento — verificar) | HiNet (AS3462) da Chunghwa Telecom
    "Chunghwa Telecom Global, INC": ("Chunghwa Telecom", "TW"),  # [Alta] mesma marca / subsidiária

    # ===== Telia | país controlador: SE | 6 AS orgs | +24 empresas, +135% receita =====
    "Telia Company AB": ("Telia", "SE"),  # [Alta] mesma marca / subsidiária
    "Telia Finland Oyj": ("Telia", "SE"),  # [Alta] mesma marca / subsidiária
    "Telia Norge AS": ("Telia", "SE"),  # [Média] controle societário (conhecimento — verificar) | Telia Norway vendida pela Telia em 2024 — verificar se ainda conta como Telia
    "Telia Eesti AS": ("Telia", "SE"),  # [Alta] mesma marca / subsidiária
    "Telia Lietuva, AB": ("Telia", "SE"),  # [Alta] mesma marca / subsidiária
    "Telia Cygate Oy": ("Telia", "SE"),  # [Alta] mesma marca / subsidiária

    # ===== LG Group | país controlador: KR | 3 AS orgs | +13 empresas, +94% receita =====
    "LG DACOM Corporation": ("LG Group", "KR"),  # [Alta] mesma marca / subsidiária | LG DACOM = LG Uplus
    "LG CNS": ("LG Group", "KR"),  # [Alta] mesma marca / subsidiária | LG DACOM = LG Uplus
    "LG HelloVision Corp.": ("LG Group", "KR"),  # [Alta] mesma marca / subsidiária | LG DACOM = LG Uplus

    # ===== Tata Group | país controlador: IN | 4 AS orgs | +15 empresas, +471% receita =====
    "TATA COMMUNICATIONS (AMERICA) INC": ("Tata Group", "IN"),  # [Alta] mesma marca / subsidiária
    "TATA Communications formerly VSNL is Leading ISP": ("Tata Group", "IN"),  # [Alta] mesma marca / subsidiária
    "TCS eServe Limited": ("Tata Group", "IN"),  # [Alta] mesma marca / subsidiária | TCS = Tata Consultancy Services
    "Tata Teleservices Maharashtra Ltd": ("Tata Group", "IN"),  # [Alta] mesma marca / subsidiária

    # ===== Deutsche Telekom | país controlador: DE | 6 AS orgs | +10 empresas, +23% receita =====
    "Deutsche Telekom AG": ("Deutsche Telekom", "DE"),  # [Alta] mesma marca / subsidiária
    "T-Mobile Austria GmbH": ("Deutsche Telekom", "DE"),  # [Alta] mesma marca / subsidiária
    "Deutsche Telekom Global Business Solutions GmbH": ("Deutsche Telekom", "DE"),  # [Alta] mesma marca / subsidiária
    "Ote SA (Hellenic Telecommunications Organisation)": ("Deutsche Telekom", "DE"),  # [Média] controle societário (conhecimento — verificar) | OTE controlada pela DT
    "Magyar Telekom Plc.": ("Deutsche Telekom", "DE"),  # [Média] controle societário (conhecimento — verificar) | Magyar Telekom é controlada pela DT
    "T-Mobile Polska S.A.": ("Deutsche Telekom", "DE"),  # [Alta] mesma marca / subsidiária

    # ===== Rackspace | país controlador: US | 2 AS orgs | +12 empresas, +93% receita =====
    "Rackspace Ltd.": ("Rackspace", "US"),  # [Alta] nome quase idêntico
    "Rackspace Hosting": ("Rackspace", "US"),  # [Alta] nome quase idêntico

    # ===== GMO Internet Group | país controlador: JP | 4 AS orgs | +5 empresas, +27% receita =====
    "GMO Internet, Inc.": ("GMO Internet Group", "JP"),  # [Alta] mesma marca / subsidiária
    "GMO-Z.com Runsystem Joint Stock Company": ("GMO Internet Group", "JP"),  # [Alta] mesma marca / subsidiária
    "GMO GlobalSign Holdings K.K.": ("GMO Internet Group", "JP"),  # [Alta] mesma marca / subsidiária
    "GMO NetIRD, Inc.": ("GMO Internet Group", "JP"),  # [Alta] mesma marca / subsidiária

    # ===== UpCloud | país controlador: FI | 2 AS orgs | +2 empresas, +15% receita =====
    "UpCloud Ltd": ("UpCloud", "FI"),  # [Alta] nome quase idêntico
    "UpCloud USA Inc": ("UpCloud", "FI"),  # [Alta] nome quase idêntico

    # ===== Thales | país controlador: FR | 2 AS orgs | +2 empresas, +11% receita =====
    "Incapsula Inc": ("Thales", "FR"),  # [Média] controle societário (conhecimento — verificar) | Incapsula/Imperva adquirida pela Thales em 2023
    "Thales Services Numeriques SAS": ("Thales", "FR"),  # [Alta] mesma marca / subsidiária

    # ===== Orange | país controlador: FR | 6 AS orgs | +16 empresas, +852% receita =====
    "Orange Business Services SA": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária
    "ORANGE BUSINESS SERVICES U.S. Inc.": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária
    "Orange S.A.": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária
    "Orange Polska Spolka Akcyjna": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária
    "Orange Business Communications Technology Limited": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária
    "Orange Romania S.A.": ("Orange", "FR"),  # [Alta] mesma marca / subsidiária

    # ===== Lumen | país controlador: US | 2 AS orgs | +10 empresas, +13% receita =====
    "Level 3 Parent, LLC": ("Lumen", "US"),  # [Média] controle societário (conhecimento — verificar) | Level 3 e CenturyLink formam a Lumen
    "CenturyLink Communications, LLC": ("Lumen", "US"),  # [Média] controle societário (conhecimento — verificar) | Level 3 e CenturyLink formam a Lumen

    # ===== Leaseweb | país controlador: NL | 6 AS orgs | +11 empresas, +2099% receita =====
    "LeaseWeb Netherlands B.V.": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária
    "Leaseweb Deutschland GmbH": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária
    "Leaseweb USA, Inc.": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária
    "LEASEWEB SINGAPORE PTE. LTD.": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária
    "LEASEWEB HONG KONG LIMITED": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária
    "Leaseweb Canada Inc.": ("Leaseweb", "NL"),  # [Alta] mesma marca / subsidiária

    # ===== SK Group | país controlador: KR | 3 AS orgs | +6 empresas, +809% receita =====
    "SK Broadband Co Ltd": ("SK Group", "KR"),  # [Alta] mesma marca / subsidiária
    "SK Co.,": ("SK Group", "KR"),  # [Alta] mesma marca / subsidiária
    "SK Telecom": ("SK Group", "KR"),  # [Alta] mesma marca / subsidiária

    # ===== Telefónica | país controlador: ES | 5 AS orgs | +13 empresas, +150% receita =====
    "TELEFONICA DE ESPANA S.A.U.": ("Telefónica", "ES"),  # [Alta] mesma marca / subsidiária
    "acens Technologies, S.L.": ("Telefónica", "ES"),  # [Média] controle societário (conhecimento — verificar) | acens é do grupo Telefónica
    "CTC. CORP S.A. (TELEFONICA EMPRESAS)": ("Telefónica", "ES"),  # [Alta] mesma marca / subsidiária
    "TELEFONICA BRASIL S.A": ("Telefónica", "ES"),  # [Alta] mesma marca / subsidiária
    "TELEFONICA CHILE S.A.": ("Telefónica", "ES"),  # [Alta] mesma marca / subsidiária

    # ===== VNPT | país controlador: VN | 3 AS orgs | +6 empresas, +123% receita =====
    "Vietnam Posts and Telecommunications (VNPT)": ("VNPT", "VN"),  # [Alta] mesma marca / subsidiária
    "VNPT Corp": ("VNPT", "VN"),  # [Alta] mesma marca / subsidiária
    "VIETNAM POSTS AND TELECOMMUNICATIONS GROUP": ("VNPT", "VN"),  # [Alta] mesma marca / subsidiária

    # ===== Far EasTone | país controlador: TW | 4 AS orgs | +5 empresas, +25% receita =====
    "New Century InfoComm Tech Co., Ltd.": ("Far EasTone", "TW"),  # [Média] controle societário (conhecimento — verificar) | NCIC (Sparq) é da Far EasTone
    "Asia Pacific Broadband Fixed Lines Co., Ltd.": ("Far EasTone", "TW"),  # [Média] controle societário (conhecimento — verificar) | Asia Pacific Telecom incorporada pela Far EasTone em 2023
    "Far EastTone Telecommunication Co., Ltd.": ("Far EasTone", "TW"),  # [Alta] mesma marca / subsidiária
    "Asia Pacific Telecom": ("Far EasTone", "TW"),  # [Média] controle societário (conhecimento — verificar) | Asia Pacific Telecom incorporada pela Far EasTone em 2023

    # ===== Gulfnet | país controlador: KW | 2 AS orgs | +4 empresas, +423% receita =====
    "Gulfnet International KEMS LLC": ("Gulfnet", "KW"),  # [Alta] nome quase idêntico
    "GULFNET COMMUNICATIONS CO. WLL": ("Gulfnet", "KW"),  # [Alta] nome quase idêntico

    # ===== Iliad | país controlador: FR | 4 AS orgs | +3 empresas, +106% receita =====
    "Scaleway SAS": ("Iliad", "FR"),  # [Média] controle societário (conhecimento — verificar) | Scaleway é do grupo Iliad
    "Free SAS": ("Iliad", "FR"),  # [Alta] mesma marca / subsidiária
    "Free Pro SAS": ("Iliad", "FR"),  # [Alta] mesma marca / subsidiária
    "P4 Sp. z o.o.": ("Iliad", "FR"),  # [Média] controle societário (conhecimento — verificar) | P4 = Play (Polônia), do grupo Iliad

    # ===== PCCW / HKT | país controlador: HK | 3 AS orgs | +4 empresas, +66% receita =====
    "PCCW IMS Ltd (PCCW Business Internet Access)": ("PCCW / HKT", "HK"),  # [Alta] mesma marca / subsidiária
    "HKT Limited": ("PCCW / HKT", "HK"),  # [Alta] mesma marca / subsidiária
    "PCCW Global (HK) Ltd.": ("PCCW / HKT", "HK"),  # [Alta] mesma marca / subsidiária

    # ===== SABIC | país controlador: SA | 3 AS orgs | +8 empresas, +200% receita =====
    "SABIC INNOVATIVE PLASTICS US, LLC": ("SABIC", "SA"),  # [Alta] mesma marca / subsidiária | SIPPE = SABIC Innovative Plastics
    "SIPPE-SG": ("SABIC", "SA"),  # [Alta] mesma marca / subsidiária | SIPPE = SABIC Innovative Plastics
    "Saudi Basic Industries Co": ("SABIC", "SA"),  # [Alta] mesma marca / subsidiária | SIPPE = SABIC Innovative Plastics

    # ===== América Movil | país controlador: MX | 4 AS orgs | +5 empresas, +62% receita =====
    "UNINET": ("América Movil", "MX"),  # [Média] controle societário (conhecimento — verificar) | Uninet/Triara são da Telmex
    "CLARO S.A.": ("América Movil", "MX"),  # [Média] controle societário (conhecimento — verificar) | Claro = América Movil
    "Triara.com S.A. de C.V.": ("América Movil", "MX"),  # [Média] controle societário (conhecimento — verificar) | Uninet/Triara são da Telmex
    "Telmex Colombia S.A.": ("América Movil", "MX"),  # [Média] controle societário (conhecimento — verificar) | Claro = América Movil

    # ===== Exabytes | país controlador: MY | 3 AS orgs | +6 empresas, +109% receita =====
    "Exa Bytes Network Sdn.Bhd.": ("Exabytes", "MY"),  # [Alta] mesma marca / subsidiária
    "Exabytes Network (Singapore) Pte. Ltd.": ("Exabytes", "MY"),  # [Alta] mesma marca / subsidiária
    "PT. EXABYTES NETWORK INDONESIA": ("Exabytes", "MY"),  # [Alta] mesma marca / subsidiária

    # ===== GlobalConnect | país controlador: SE | 2 AS orgs | +5 empresas, +100% receita =====
    "GlobalConnect AB": ("GlobalConnect", "SE"),  # [Alta] nome quase idêntico
    "GLOBALCONNECT AS": ("GlobalConnect", "SE"),  # [Alta] nome quase idêntico

    # ===== Vodafone Group | país controlador: GB | 4 AS orgs | +6 empresas, +96% receita =====
    "Vodafone Net Iletisim Hizmetler AS": ("Vodafone Group", "GB"),  # [Alta] mesma marca / subsidiária | Vodafone Turquia
    "Vodacom": ("Vodafone Group", "GB"),  # [Média] controle societário (conhecimento — verificar) | Vodacom é controlada pela Vodafone
    "Vodafone Group Services GmbH": ("Vodafone Group", "GB"),  # [Alta] mesma marca / subsidiária
    "Vodafone Data": ("Vodafone Group", "GB"),  # [Média] controle societário (conhecimento — verificar) | Vodafone Egito é controlada pela Vodacom

    # ===== Huawei | país controlador: CN | 2 AS orgs | +5 empresas, +34% receita =====
    "Huawei Cloud Service data center": ("Huawei", "CN"),  # [Alta] mesma marca / subsidiária
    "HUAWEI CLOUDS": ("Huawei", "CN"),  # [Alta] mesma marca / subsidiária

    # ===== Ooredoo | país controlador: QA | 2 AS orgs | +1 empresas, +19% receita =====
    "Ooredoo Q.S.C.": ("Ooredoo", "QA"),  # [Alta] mesma marca / subsidiária
    "NATIONAL MOBILE TELECOMMUNICATIONS COMPANY K.S.C.P.": ("Ooredoo", "QA"),  # [Média] controle societário (conhecimento — verificar) | NMTC = Ooredoo Kuwait

    # ===== Zayo | país controlador: US | 3 AS orgs | +5 empresas, +50% receita =====
    "Zayo Infrastructure France SA": ("Zayo", "US"),  # [Alta] mesma marca / subsidiária
    "Zayo Bandwidth": ("Zayo", "US"),  # [Alta] mesma marca / subsidiária
    "Latisys-Chicago, LLC": ("Zayo", "US"),  # [Média] controle societário (conhecimento — verificar) | Latisys adquirida pela Zayo em 2017

    # ===== Advania | país controlador: IS | 3 AS orgs | +6 empresas, +150% receita =====
    "ADVANIA NORGE AS": ("Advania", "IS"),  # [Alta] mesma marca / subsidiária
    "Advania Finland Oy": ("Advania", "IS"),  # [Alta] mesma marca / subsidiária
    "Advania Island ehf": ("Advania", "IS"),  # [Alta] mesma marca / subsidiária

    # ===== Liberty Global | país controlador: GB | 2 AS orgs | +1 empresas, +49% receita =====
    "Telenet BV": ("Liberty Global", "GB"),  # [Média] controle societário (conhecimento — verificar) | Telenet controlada pela Liberty Global
    "Liberty Global Europe Holding B.V.": ("Liberty Global", "GB"),  # [Alta] mesma marca / subsidiária

    # ===== Taiwan Mobile | país controlador: TW | 2 AS orgs | +1 empresas, +13% receita =====
    "Taiwan Fixed Network, Telco and Network Service Provider.": ("Taiwan Mobile", "TW"),  # [Média] controle societário (conhecimento — verificar) | TFN é subsidiária da Taiwan Mobile
    "Taiwan Mobile Co., Ltd.": ("Taiwan Mobile", "TW"),  # [Alta] mesma marca / subsidiária

    # ===== CERNET | país controlador: CN | 2 AS orgs | +4 empresas, +100% receita =====
    "China Education and Research Network Center": ("CERNET", "CN"),  # [Alta] mesma marca / subsidiária
    "China Next Generation Internet CERNET2": ("CERNET", "CN"),  # [Alta] mesma marca / subsidiária

    # ===== Newfold Digital | país controlador: US | 3 AS orgs | +4 empresas, +197% receita =====
    "Unified Layer": ("Newfold Digital", "US"),  # [Média] controle societário (conhecimento — verificar) | Unified Layer (Bluehost) é Newfold
    "Newfold Digital, Inc.": ("Newfold Digital", "US"),  # [Alta] mesma marca / subsidiária
    "Network Solutions, LLC": ("Newfold Digital", "US"),  # [Média] controle societário (conhecimento — verificar) | Network Solutions é Newfold

    # ===== Telenor | país controlador: NO | 3 AS orgs | +4 empresas, +144% receita =====
    "DNA Oyj": ("Telenor", "NO"),  # [Média] controle societário (conhecimento — verificar) | DNA (Finlândia) controlada pela Telenor
    "Telenor Sverige AB": ("Telenor", "NO"),  # [Alta] mesma marca / subsidiária
    "Telenor Norge AS": ("Telenor", "NO"),  # [Alta] mesma marca / subsidiária

    # ===== Telstra | país controlador: AU | 2 AS orgs | +2 empresas, +34% receita =====
    "Telstra Limited": ("Telstra", "AU"),  # [Alta] mesma marca / subsidiária
    "Telstra Global": ("Telstra", "AU"),  # [Alta] mesma marca / subsidiária

    # ===== Polsat (Cyfrowy Polsat) | país controlador: PL | 3 AS orgs | +3 empresas, +697% receita =====
    "Netia SA": ("Polsat (Cyfrowy Polsat)", "PL"),  # [Média] controle societário (conhecimento — verificar) | Netia controlada pela Cyfrowy Polsat
    "Polkomtel Sp. z o.o.": ("Polsat (Cyfrowy Polsat)", "PL"),  # [Média] controle societário (conhecimento — verificar) | Polkomtel (Plus) do grupo Polsat
    "Cyfrowy Polsat S.A.": ("Polsat (Cyfrowy Polsat)", "PL"),  # [Alta] mesma marca / subsidiária

    # ===== Techint (Ternium/Tenaris) | país controlador: AR | 4 AS orgs | +4 empresas, +234% receita =====
    "SIDERAR S.A.I.C.": ("Techint (Ternium/Tenaris)", "AR"),  # [Média] controle societário (conhecimento — verificar) | Siderar = Ternium Argentina
    "Ternium Mexico, S.A. de C.V.": ("Techint (Ternium/Tenaris)", "AR"),  # [Média] controle societário (conhecimento — verificar) | Siderar = Ternium Argentina
    "SIDERCA S.A.I.C.": ("Techint (Ternium/Tenaris)", "AR"),  # [Média] controle societário (conhecimento — verificar) | Siderca = Tenaris
    "Tenaris Global Services (USA) Corp.": ("Techint (Ternium/Tenaris)", "AR"),  # [Média] controle societário (conhecimento — verificar) | Siderca = Tenaris

    # ===== DTS Systeme | país controlador: DE | 2 AS orgs | +2 empresas, +41% receita =====
    "DTS Systeme GmbH": ("DTS Systeme", "DE"),  # [Alta] nome quase idêntico
    "DTS Systeme Muenster GmbH": ("DTS Systeme", "DE"),  # [Alta] nome quase idêntico

    # ===== Hanwha | país controlador: KR | 2 AS orgs | +1 empresas, +11% receita =====
    "HANWHA Corp. Information Service div.": ("Hanwha", "KR"),  # [Alta] mesma marca / subsidiária
    "Hanwha Ocean Co., Ltd.": ("Hanwha", "KR"),  # [Alta] mesma marca / subsidiária

    # ===== PTT | país controlador: TH | 2 AS orgs | +1 empresas, +14% receita =====
    "PTT Digital Solutions Company Limited": ("PTT", "TH"),  # [Alta] mesma marca / subsidiária
    "PTT Global Chemical Public Company Limited": ("PTT", "TH"),  # [Alta] mesma marca / subsidiária

    # ===== WIIT | país controlador: IT | 2 AS orgs | +2 empresas, +119% receita =====
    "WIIT AG": ("WIIT", "IT"),  # [Alta] nome quase idêntico
    "WIIT S.p.A.": ("WIIT", "IT"),  # [Alta] nome quase idêntico

    # ===== Web Werks | país controlador: IN | 2 AS orgs | +1 empresas, +87% receita =====
    "Web Werks India Pvt. Ltd.": ("Web Werks", "IN"),  # [Alta] nome quase idêntico
    "Web Werks": ("Web Werks", "IN"),  # [Alta] nome quase idêntico

    # ===== Altice USA | país controlador: US | 2 AS orgs | +2 empresas, +212% receita =====
    "Cablevision Systems Corp.": ("Altice USA", "US"),  # [Média] controle societário (conhecimento — verificar) | Cablevision = Altice USA; Lightpath é controlada pela Altice USA
    "Cablevision Lightpath LLC": ("Altice USA", "US"),  # [Média] controle societário (conhecimento — verificar) | Cablevision = Altice USA; Lightpath é controlada pela Altice USA

    # ===== Ayala (Globe) | país controlador: PH | 2 AS orgs | +2 empresas, +100% receita =====
    "Globe Telecoms": ("Ayala (Globe)", "PH"),  # [Alta] mesma marca / subsidiária
    "AyalaPort Makati, Inc. / Data Center Operator": ("Ayala (Globe)", "PH"),  # [Média] controle societário (conhecimento — verificar) | Globe é do grupo Ayala; mesma assinatura de receita

    # ===== Binat | país controlador: IL | 2 AS orgs | +2 empresas, +100% receita =====
    "Internet Binat Ltd": ("Binat", "IL"),  # [Alta] nome quase idêntico
    "BINAT BUSINESS LTD": ("Binat", "IL"),  # [Alta] nome quase idêntico

    # ===== UBS | país controlador: CH | 2 AS orgs | +2 empresas, +100% receita =====
    "UBS Group AG": ("UBS", "CH"),  # [Alta] nome quase idêntico
    "UBS AG": ("UBS", "CH"),  # [Alta] nome quase idêntico

    # ===== Hokuriku Electric (Hokuden) | país controlador: JP | 3 AS orgs | +2 empresas, +169% receita =====
    "Hokuden Information Technology,Inc.": ("Hokuriku Electric (Hokuden)", "JP"),  # [Média] controle societário (conhecimento — verificar) | Hokuden = Hokuriku Electric Power
    "Hokuden Information System Service Co.,Ltd.": ("Hokuriku Electric (Hokuden)", "JP"),  # [Média] controle societário (conhecimento — verificar) | Hokuden = Hokuriku Electric Power
    "Hokuriku Telecommunication Network Co.": ("Hokuriku Electric (Hokuden)", "JP"),  # [Média] controle societário (conhecimento — verificar) | Hokuden = Hokuriku Electric Power

    # ===== Marsh McLennan | país controlador: US | 3 AS orgs | +2 empresas, +200% receita =====
    "Marsh Limited": ("Marsh McLennan", "US"),  # [Alta] nome quase idêntico
    "Marsh Inc.": ("Marsh McLennan", "US"),  # [Alta] nome quase idêntico
    "Marsh & McLennan Companies, Inc.": ("Marsh McLennan", "US"),  # [Alta] nome quase idêntico

    # ===== Mercedes-Benz | país controlador: DE | 3 AS orgs | +2 empresas, +200% receita =====
    "MERCEDES-BENZ USA, LLC": ("Mercedes-Benz", "DE"),  # [Alta] mesma marca / subsidiária
    "Mercedes-Benz Singapore Pte. Ltd.": ("Mercedes-Benz", "DE"),  # [Alta] mesma marca / subsidiária
    "Mercedes-Benz Group AG": ("Mercedes-Benz", "DE"),  # [Alta] mesma marca / subsidiária

    # ===== Opera | país controlador: NO | 3 AS orgs | +2 empresas, +200% receita =====
    "Opera Software Technology (Beijing) Co., Ltd.": ("Opera", "NO"),  # [Alta] mesma marca / subsidiária
    "Opera Software Americas LLC": ("Opera", "NO"),  # [Alta] mesma marca / subsidiária
    "Opera Norway AS": ("Opera", "NO"),  # [Alta] mesma marca / subsidiária

    # ===== Pearson | país controlador: GB | 3 AS orgs | +2 empresas, +200% receita =====
    "NCS Pearson Inc.": ("Pearson", "GB"),  # [Alta] mesma marca / subsidiária
    "Pearson Shared Services Ltd": ("Pearson", "GB"),  # [Alta] mesma marca / subsidiária
    "Pearson Group": ("Pearson", "GB"),  # [Alta] mesma marca / subsidiária

    # ===== Publicis (Re:Sources) | país controlador: FR | 3 AS orgs | +2 empresas, +200% receita =====
    "LION RESOURCES, INC.": ("Publicis (Re:Sources)", "FR"),  # [Média] controle societário (conhecimento — verificar) | Lion Re:Sources = braço de TI da Publicis
    "PG Lion ReSources Aust Pty Ltd": ("Publicis (Re:Sources)", "FR"),  # [Média] controle societário (conhecimento — verificar) | Lion Re:Sources = braço de TI da Publicis
    "Re:Sources France SAS": ("Publicis (Re:Sources)", "FR"),  # [Média] controle societário (conhecimento — verificar) | Lion Re:Sources = braço de TI da Publicis

    # ===== RELX | país controlador: GB | 3 AS orgs | +2 empresas, +200% receita =====
    "RELX inc.": ("RELX", "GB"),  # [Alta] mesma marca / subsidiária | Elsevier é do grupo RELX
    "Elsevier Ltd": ("RELX", "GB"),  # [Alta] mesma marca / subsidiária | Elsevier é do grupo RELX
    "Elsevier Limited": ("RELX", "GB"),  # [Alta] mesma marca / subsidiária | Elsevier é do grupo RELX

    # ===== Turkcell | país controlador: TR | 2 AS orgs | +1 empresas, +34% receita =====
    "Superonline Iletisim Hizmetleri A.S.": ("Turkcell", "TR"),  # [Média] controle societário (conhecimento — verificar) | Superonline é subsidiária da Turkcell
    "TURKCELL ILETISIM HIZMETLERI A.S.": ("Turkcell", "TR"),  # [Alta] mesma marca / subsidiária

    # ===== Volvo | país controlador: SE | 3 AS orgs | +2 empresas, +200% receita =====
    "UD Trucks Corporation, Volvo Information Technology Japan": ("Volvo", "SE"),  # [Alta] mesma marca / subsidiária
    "Volvo Information Technology AB": ("Volvo", "SE"),  # [Alta] mesma marca / subsidiária
    "Volvo Group North America, Inc.": ("Volvo", "SE"),  # [Alta] mesma marca / subsidiária

    # ===== XL Axiata | país controlador: ID | 3 AS orgs | +2 empresas, +3138% receita =====
    "Linknet ASN": ("XL Axiata", "ID"),  # [Média] controle societário (conhecimento — verificar) | Link Net adquirida pela XL Axiata em 2022
    "PT XL Axiata Tbk": ("XL Axiata", "ID"),  # [Alta] nome quase idêntico
    "PT XL Axiata": ("XL Axiata", "ID"),  # [Alta] nome quase idêntico

    # ===== Accenture | país controlador: IE | 2 AS orgs | +1 empresas, +100% receita =====
    "Accenture UK Limited": ("Accenture", "IE"),  # [Alta] nome quase idêntico
    "Accenture LLP": ("Accenture", "IE"),  # [Alta] nome quase idêntico

    # ===== Aramark | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "ARAMARK": ("Aramark", "US"),  # [Alta] nome quase idêntico
    "Aramark Services, Inc.": ("Aramark", "US"),  # [Alta] nome quase idêntico

    # ===== Atos | país controlador: FR | 2 AS orgs | +1 empresas, +100% receita =====
    "Eviden Netherlands B.V.": ("Atos", "FR"),  # [Média] controle societário (conhecimento — verificar) | Eviden é marca/divisão da Atos
    "Atos France SAS": ("Atos", "FR"),  # [Média] controle societário (conhecimento — verificar) | Eviden é marca/divisão da Atos

    # ===== Bosch | país controlador: DE | 2 AS orgs | +1 empresas, +100% receita =====
    "Robert Bosch GmbH": ("Bosch", "DE"),  # [Alta] nome quase idêntico
    "Robert Bosch Gesellschaft mit Beschraenkter Haftung": ("Bosch", "DE"),  # [Alta] nome quase idêntico

    # ===== CS Loxinfo | país controlador: TH | 2 AS orgs | +1 empresas, +31% receita =====
    "CS LOXINFO PUBLIC COMPANY LIMITED": ("CS Loxinfo", "TH"),  # [Alta] mesma marca / subsidiária
    "POPIDC powered by CSLoxinfo": ("CS Loxinfo", "TH"),  # [Alta] mesma marca / subsidiária

    # ===== Charter Communications | país controlador: US | 2 AS orgs | +1 empresas, +12% receita =====
    "Charter Communications LLC": ("Charter Communications", "US"),  # [Alta] nome quase idêntico
    "Charter Communications Inc": ("Charter Communications", "US"),  # [Alta] nome quase idêntico

    # ===== Cogeco | país controlador: CA | 2 AS orgs | +1 empresas, +100% receita =====
    "Cogeco Connexion inc": ("Cogeco", "CA"),  # [Alta] nome quase idêntico
    "Cogeco Connexion Inc.": ("Cogeco", "CA"),  # [Alta] nome quase idêntico

    # ===== Deutsche Bank | país controlador: DE | 2 AS orgs | +1 empresas, +100% receita =====
    "Deutsche Bank APAC RHO in Singapore Internet AS": ("Deutsche Bank", "DE"),  # [Alta] nome quase idêntico
    "Deutsche Bank AG": ("Deutsche Bank", "DE"),  # [Alta] nome quase idêntico

    # ===== Deutsche Börse | país controlador: DE | 2 AS orgs | +1 empresas, +100% receita =====
    "Clearstream Services S.A.": ("Deutsche Börse", "DE"),  # [Média] controle societário (conhecimento — verificar) | Clearstream é da Deutsche Börse
    "Deutsche Boerse AG": ("Deutsche Börse", "DE"),  # [Alta] mesma marca / subsidiária

    # ===== Dustin | país controlador: SE | 2 AS orgs | +1 empresas, +100% receita =====
    "Dustin Sverige AB": ("Dustin", "SE"),  # [Alta] nome quase idêntico
    "Dustin NL B.V.": ("Dustin", "SE"),  # [Alta] nome quase idêntico

    # ===== Equatorial | país controlador: BR | 2 AS orgs | +1 empresas, +100% receita =====
    "Equatorial Telecomunicacoes LTDA": ("Equatorial", "BR"),  # [Alta] nome quase idêntico
    "Equatorial Energia S/A": ("Equatorial", "BR"),  # [Alta] nome quase idêntico

    # ===== Experian | país controlador: IE | 2 AS orgs | +1 empresas, +100% receita =====
    "Experian": ("Experian", "IE"),  # [Alta] nome quase idêntico
    "Experian International Unlimited": ("Experian", "IE"),  # [Alta] nome quase idêntico

    # ===== First Advantage | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "First Advantage Corporation": ("First Advantage", "US"),  # [Alta] nome quase idêntico
    "FIRST ADVANTAGE GLOBAL OPERATING CENTER PRIVATE LIMITED": ("First Advantage", "US"),  # [Alta] nome quase idêntico

    # ===== Ford | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "Ford Motor Company Limited": ("Ford", "US"),  # [Alta] nome quase idêntico
    "Ford Motor Company": ("Ford", "US"),  # [Alta] nome quase idêntico

    # ===== Gigas | país controlador: ES | 2 AS orgs | +1 empresas, +100% receita =====
    "GIGAS HOSTING USA, LLC": ("Gigas", "ES"),  # [Alta] nome quase idêntico
    "GIGAS HOSTING S.A.": ("Gigas", "ES"),  # [Alta] nome quase idêntico

    # ===== Grifols | país controlador: ES | 2 AS orgs | +1 empresas, +100% receita =====
    "Grifols S.A.": ("Grifols", "ES"),  # [Alta] nome quase idêntico
    "Grifols Inc.": ("Grifols", "ES"),  # [Alta] nome quase idêntico

    # ===== IQVIA | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "IQVIA SOLUTIONS HQ LTD": ("IQVIA", "US"),  # [Alta] nome quase idêntico
    "IQVIA Holdings Inc": ("IQVIA", "US"),  # [Alta] nome quase idêntico

    # ===== Interactive Brokers | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "Interactive Brokers LLC": ("Interactive Brokers", "US"),  # [Alta] nome quase idêntico
    "Interactive Brokers Corp": ("Interactive Brokers", "US"),  # [Alta] nome quase idêntico

    # ===== La Française des Jeux | país controlador: FR | 2 AS orgs | +1 empresas, +100% receita =====
    "LFDJ-AS": ("La Française des Jeux", "FR"),  # [Alta] nome quase idêntico
    "La Francaise des Jeux": ("La Française des Jeux", "FR"),  # [Alta] nome quase idêntico

    # ===== M247 | país controlador: GB | 2 AS orgs | +1 empresas, +100% receita =====
    "M247 Ltd": ("M247", "GB"),  # [Alta] nome quase idêntico
    "M247 Europe SRL": ("M247", "GB"),  # [Alta] nome quase idêntico

    # ===== Mettler-Toledo | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "METTLER-TOLEDO INTERNATIONAL INC., Wilmington, Delaware, Greifensee Branch": ("Mettler-Toledo", "US"),  # [Alta] nome quase idêntico
    "Mettler-Toledo LLC": ("Mettler-Toledo", "US"),  # [Alta] nome quase idêntico

    # ===== NetEase | país controlador: CN | 2 AS orgs | +1 empresas, +1944% receita =====
    "NETEASE HONG KONG LIMITED": ("NetEase", "CN"),  # [Alta] mesma marca / subsidiária
    "NetEase Building No.16 Ke Yun Road,": ("NetEase", "CN"),  # [Alta] mesma marca / subsidiária

    # ===== Novartis | país controlador: CH | 2 AS orgs | +1 empresas, +100% receita =====
    "Novartis Pharmaceuticals": ("Novartis", "CH"),  # [Alta] nome quase idêntico
    "Novartis AG": ("Novartis", "CH"),  # [Alta] nome quase idêntico

    # ===== Owens Corning | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "OWENS CORNING FRANCE SAS": ("Owens Corning", "US"),  # [Alta] nome quase idêntico
    "Owens-Corning": ("Owens Corning", "US"),  # [Alta] nome quase idêntico

    # ===== RTL Group | país controlador: LU | 2 AS orgs | +1 empresas, +100% receita =====
    "FremantleMedia Limited": ("RTL Group", "LU"),  # [Média] controle societário (conhecimento — verificar) | Fremantle é do RTL Group
    "Broadcasting Center Europe (an RTL Group Company)": ("RTL Group", "LU"),  # [Alta] mesma marca / subsidiária

    # ===== Shell | país controlador: GB | 2 AS orgs | +1 empresas, +100% receita =====
    "Shell Information Technology International, Inc.": ("Shell", "GB"),  # [Alta] nome quase idêntico
    "Shell Information Technology International B.V.": ("Shell", "GB"),  # [Alta] nome quase idêntico

    # ===== SiteOne | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "SITEONE LANDSCAPE SUPPLY, LLC": ("SiteOne", "US"),  # [Alta] nome quase idêntico
    "SiteOne Landscape Supply": ("SiteOne", "US"),  # [Alta] nome quase idêntico

    # ===== Sonic | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "Sonic.net, LLC": ("Sonic", "US"),  # [Alta] nome quase idêntico
    "Sonic Telecom LLC": ("Sonic", "US"),  # [Alta] nome quase idêntico

    # ===== TAURON | país controlador: PL | 2 AS orgs | +1 empresas, +100% receita =====
    "TAURON WYTWARZANIE SPOLKA AKCYJNA": ("TAURON", "PL"),  # [Alta] nome quase idêntico
    "TAURON Dystrybucja S.A.": ("TAURON", "PL"),  # [Alta] nome quase idêntico

    # ===== Telkom SA | país controlador: ZA | 2 AS orgs | +1 empresas, +839% receita =====
    "Business Connexion Communications": ("Telkom SA", "ZA"),  # [Média] controle societário (conhecimento — verificar) | BCX é subsidiária da Telkom SA
    "Telkom SA Ltd.": ("Telkom SA", "ZA"),  # [Alta] mesma marca / subsidiária

    # ===== Vaisala | país controlador: FI | 2 AS orgs | +1 empresas, +100% receita =====
    "Vaisala Oyj": ("Vaisala", "FI"),  # [Alta] nome quase idêntico
    "Vaisala Inc": ("Vaisala", "FI"),  # [Alta] nome quase idêntico

    # ===== VeriSign | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "VeriSign Infrastructure & Operations": ("VeriSign", "US"),  # [Alta] nome quase idêntico
    "VeriSign Global Registry Services": ("VeriSign", "US"),  # [Alta] nome quase idêntico

    # ===== Visteon | país controlador: US | 2 AS orgs | +1 empresas, +100% receita =====
    "VISTEON CORPORATION": ("Visteon", "US"),  # [Alta] nome quase idêntico
    "Visteon Corporation": ("Visteon", "US"),  # [Alta] nome quase idêntico

    # ===== Vodafone Idea | país controlador: IN | 2 AS orgs | +1 empresas, +100% receita =====
    "Vodafone Mobile Services Ltd": ("Vodafone Idea", "IN"),  # [Alta] mesma marca / subsidiária | Vodafone Group é minoritário; controle indiano
    "Vodafone Idea Ltd": ("Vodafone Idea", "IN"),  # [Alta] mesma marca / subsidiária | Vodafone Group é minoritário; controle indiano

    # ===== Webzilla | país controlador: NL | 2 AS orgs | +1 empresas, +100% receita =====
    "Webzilla B.V.": ("Webzilla", "NL"),  # [Alta] nome quase idêntico
    "Webzilla Inc.": ("Webzilla", "NL"),  # [Alta] nome quase idêntico

    # ===== Zoho | país controlador: IN | 2 AS orgs | +1 empresas, +100% receita =====
    "Zoho Corporation PTY LTD": ("Zoho", "IN"),  # [Alta] nome quase idêntico
    "ZOHO": ("Zoho", "IN"),  # [Alta] nome quase idêntico
}