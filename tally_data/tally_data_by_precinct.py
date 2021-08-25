import json

from duplicates.dupe_batches_with_tally import group_together_similar_batches_with_ballot_info


#Dictionary that matches a ballot code to a physical precinct on a map:
precincts = {'1': '01A', '2': '01B', '3': '01C', '4': '01E', '5': '01G', '6': '01J', '7': '01P', '8': '01R', '9': '01T',
             '10': '02E', '11': '02F1', '12': '05A2', '13': '12E1', '14': '12F', '15': '12G', '16': '12H1', '17': '01A',
             '18': '01B', '19': '01C', '21': '01E', '26': '01J', '27': '01P', '31': '02A', '32': '02A1', '33': '02B',
             '34': '02C', '35': '02D', '36': '02E', '37': '02F1', '38': '02F2', '40': '02J', '41': '02K', '42': '02L1',
             '43': '02L1A', '44': '02L2', '47': '03A', '52': '03F', '55': '03L', '56': '03L', '59': '03P1A',
             '64': '04B', '67': '04F', '69': '04I', '71': '04K', '72': '04L', '77': '04W', '78': '04X1', '80': '05A1',
             '81': '05A2', '82': '05B', '86': '05J', '88': '06B', '89': '06D', '90': '06D1', '92': '06E', '93': '06F',
             '95': '06I', '96': '06J', '97': '06L1', '98': '06L2', '99': '06N', '101': '06R', '102': '07C',
             '103': '07D', '104': '07E', '105': '07F', '106': '07H', '107': '07J', '108': '07M', '109': '07N',
             '110': '08F1', '111': '08G', '112': '08H', '113': '08J', '114': '08K', '115': '08L', '116': '08M',
             '117': '08P', '118': '09A', '119': '09B', '122': '09E', '123': '09F', '124': '09G', '125': '09H',
             '129': '09M', '131': '10B', '141': '10K', '145': '11B', '147': '11C', '150': '11E3', '154': '11K',
             '155': '11M', '156': '11M1', '157': '11N', '160': '12A', '164': '12F', '172': '12M', '175': 'CP011',
             '178': 'CP02', '188': 'EP01A', '189': 'EP01B', '191': 'EP02B', '194': 'EP02E', '195': 'EP03A',
             '201': 'HP01', '205': 'SC02', '227': '01D', '228': '01F', '229': '05A1', '230': '06F', '231': '12A',
             '232': '12A1', '233': '12L', '234': '12N', '235': '12S', '245': '01H', '247': '02C', '248': '02D',
             '249': '02F2', '250': '02G', '251': '02J', '252': '02K', '253': '02S', '254': '04M', '255': '05B',
             '256': '05C', '257': '05F', '258': '05J', '259': '05K', '260': '06B', '261': '06G', '279': '01S',
             '280': '01T', '281': '12D', '282': '12H2', '283': '12J', '284': '12M', '291': '02A', '292': '02A1',
             '293': '02A', '294': '02A1', '295': '02B', '296': '04B', '297': '04G', '298': '04I', '299': '04K',
             '300': '04S', '301': '04T', '302': '04W', '303': '05D', '313': '02L1', '314': '02L1A', '315': '04X1',
             '316': '10K', '317': '10M', '318': '11H', '319': '02L1', '320': '02L1A', '321': '04X1', '322': '10K',
             '323': '10M', '324': '11H', '325': '02L2', '326': '03A', '327': '03D', '328': '03E', '329': '03G',
             '330': '03I', '331': '03L', '332': '03N', '333': '04A', '334': '04C', '335': '04D', '336': '04L',
             '337': '04X2', '338': '02L2', '339': '03A', '340': '03D', '341': '03E', '342': '03G', '343': '03I',
             '344': '03L', '345': '03N', '346': '04A', '347': '04C', '348': '04D', '349': '04L', '350': '04X2',
             '351': '02W', '352': '03F', '353': '03P1A', '354': '06E', '355': '06L1', '356': '06R', '357': '02W',
             '358': '03F', '359': '03P1A', '360': '06E', '361': '06L1', '362': '06R', '363': '03B', '364': '03C',
             '365': '10J', '369': '03H', '370': '03M', '371': '03S', '372': '09G', '373': '09I', '380': '03T',
             '381': '04F', '382': '04J', '387': '04V', '388': '06D', '389': '06D1', '390': '06D2', '391': '06J',
             '392': '12K', '399': '06I', '400': '06Q', '401': '07E', '402': '07F', '403': '07H', '404': '07M',
             '405': '07N', '406': '08G', '407': '08H', '408': '06I', '409': '06Q', '410': '07E', '411': '07F',
             '412': '07H', '413': '07M', '414': '07N', '415': '08G', '416': '08H', '417': '06L2', '418': '06N',
             '419': '07J', '420': '11E2', '421': '11N', '422': '11P', '423': '06L2', '424': '06N', '425': '07J',
             '426': '11E2', '427': '11N', '428': '11P', '429': '07A', '430': '07B', '431': '08N2', '432': '07A',
             '433': '07B', '434': '08A', '435': '08B', '436': '08C', '437': '08D', '438': '08E', '439': '08N1',
             '441': 'SS09A', '442': 'SS09B', '445': 'SS13B', '446': 'SS14', '450': '07C', '451': '07D', '452': '08F1',
             '453': '08M', '458': '08A', '460': '08B', '461': '08C', '462': '08D', '463': '08N1', '468': '08E',
             '470': '08J', '472': '08K', '473': '08L', '474': '08P', '475': '09H', '476': '11B', '477': '11B1',
             '484': '09A', '485': '09B', '486': '09C', '487': '09D', '488': '09E', '489': '09K', '490': '09K1',
             '491': '09M', '492': '10D', '493': '10E', '494': '10F', '495': '10P', '508': '09F', '510': '10A',
             '511': '10C', '514': '10B', '515': '10H2', '516': '11C', '520': '10G', '522': '10H1', '523': '10R',
             '526': '10I', '528': '11E1', '530': '11E3', '531': '11E3', '532': '11G', '533': '12I', '534': '11G',
             '535': '12I', '536': '11J', '537': '11J', '538': '11K', '539': '11R', '540': '11K', '541': '11R',
             '542': '11M', '543': '11M1', '544': '11M', '545': '11M1', '546': 'AP01A', '547': 'AP01B', '548': 'AP01C',
             '549': 'AP01D', '550': 'AP14', '551': 'JC15', '552': 'JC16', '553': 'AP01A', '555': 'AP01C',
             '556': 'AP01D', '557': 'AP021', '558': 'AP022', '559': 'AP02B', '560': 'AP03', '562': 'AP04B',
             '563': 'AP05', '565': 'AP07A', '566': 'AP07B', '567': 'AP09A', '569': 'AP10', '570': 'AP12A',
             '571': 'AP12B', '572': 'AP12C', '573': 'AP14', '574': 'JC01', '575': 'JC01', '576': 'JC02',
             '579': 'JC04A', '581': 'JC04C', '582': 'JC05', '583': 'JC06', '584': 'JC07', '586': 'JC09',
             '589': 'JC12', '590': 'JC13A', '592': 'JC14', '594': 'JC16', '595': 'JC18', '596': 'JC19', '597': 'ML01A',
             '599': 'ML02A', '601': 'ML03', '602': 'ML03A', '603': 'ML04', '604': 'ML05', '605': 'ML06A',
             '606': 'ML06B', '608': 'ML07B', '609': 'MP01', '610': 'RW01', '611': 'RW02', '612': 'RW03', '613': 'RW04',
             '614': 'RW05', '615': 'RW06', '618': 'RW08', '619': 'RW09', '621': 'RW10', '623': 'RW12', '624': 'RW12A',
             '625': 'RW13', '627': 'RW17', '628': 'RW19', '629': 'RW20', '630': 'RW21', '631': 'RW22A', '632': 'SS01',
             '634': 'SS02B', '635': 'SS03', '636': 'SS04', '637': 'SS05', '639': 'SS07A', '640': 'SS07B',
             '642': 'SS08A', '643': 'SS08B', '646': 'SS11A', '647': 'SS11B', '649': 'SS12', '650': 'SS15A',
             '651': 'SS15B', '652': 'SS16', '653': 'SS17', '656': 'SS19A', '657': 'SS19B', '658': 'SS20',
             '659': 'SS22', '670': 'AP021', '671': 'AP022', '674': 'AP02B', '675': 'AP03', '676': 'RW01', '677': 'RW02',
             '678': 'RW03', '679': 'RW05', '680': 'RW07B', '681': 'RW08', '682': 'RW10', '683': 'RW11A', '684': 'RW16',
             '696': 'AP04A', '697': 'AP04B', '698': 'ML01A', '699': 'ML01B', '700': 'MP01', '701': 'RW09',
             '702': 'RW09A', '703': 'RW12', '704': 'RW12A', '705': 'RW19', '716': 'AP05', '717': 'AP09A',
             '718': 'AP12A', '722': 'AP06', '723': 'AP07A', '724': 'AP10', '725': 'AP12C', '730': 'AP07B',
             '731': 'ML02B', '732': 'ML03', '733': 'ML03A', '734': 'ML04', '735': 'ML05', '736': 'ML06A',
             '737': 'ML06B', '738': 'ML07B', '748': 'AP09B', '749': 'JC04B', '752': 'AP12B', '754': 'CH01',
             '755': 'CH02', '756': 'CH03', '757': 'CH04A', '758': 'CH05', '759': 'CH01', '764': 'CP06A', '781': 'SC07A',
             '784': 'SC08B', '793': 'SC09C', '796': 'SC11B', '798': 'SC15', '806': 'SC19B', '809': 'SC212',
             '812': 'SC23C', '813': 'SC27', '814': 'SC29A', '819': 'UC02A', '821': 'UC02C', '829': 'CH02',
             '830': 'FA01A', '831': 'FA01B', '832': 'FA01D', '833': 'PA01', '834': 'SC04', '835': 'SC05A',
             '836': 'SC07A', '837': 'SC07C', '838': 'SC07D', '839': 'SC13', '851': 'CP011', '852': 'CP012',
             '855': 'CP01B', '856': 'CP02', '857': 'CP04A', '858': 'CP04B', '863': 'CP051', '864': 'CP07D',
             '865': 'CP07F', '869': 'CP05B', '873': 'CP06A', '875': 'CP07C', '876': 'CP07E', '880': 'CP083',
             '883': 'SC08D', '884': 'SC09A', '885': 'SC09C', '886': 'SC10', '887': 'SC11A', '888': 'SC23A',
             '889': 'SC23C', '890': 'SC27', '891': 'CP081', '892': 'CP083', '894': 'CP08A', '895': 'SC08D',
             '896': 'SC09A', '897': 'SC09C', '898': 'SC10', '899': 'SC11A', '900': 'SC23A', '901': 'SC23C',
             '902': 'SC27', '903': 'EP01A', '904': 'EP01B', '905': 'EP02D', '906': 'EP03A', '907': 'EP01A',
             '908': 'EP01B', '909': 'EP02D', '910': 'EP03A', '911': 'EP02A', '913': 'EP02B', '915': 'EP02C',
             '917': 'EP02E', '919': 'EP03B', '920': 'EP04A', '921': 'EP03B', '922': 'EP04A', '923': 'EP04B',
             '924': 'EP04C', '925': 'EP04B', '926': 'EP04C', '927': 'FA01C', '928': 'SC08E', '929': 'SC211',
             '930': 'SC212', '931': 'SC29A', '937': 'FC01', '938': 'FC02', '939': 'FC03', '940': 'SC01A',
             '941': 'SC01B', '942': 'SC01C', '943': 'SC14A', '944': 'SC16A', '953': 'HP01', '955': 'JC01',
             '956': 'JC01A', '957': 'JC02', '958': 'JC03B', '959': 'JC05', '960': 'JC06', '961': 'JC07',
             '962': 'JC08', '963': 'JC09', '964': 'JC10', '965': 'JC11', '966': 'JC12', '967': 'JC13B', '981': 'JC03A',
             '982': 'JC04A', '983': 'JC04C', '987': 'JC13A', '989': 'JC14', '991': 'JC18', '992': 'JC19', '993': 'RW04',
             '994': 'RW06', '995': 'RW20', '996': 'RW21', '997': 'RW22A', '1005': 'ML02A', '1006': 'ML07A',
             '1009': 'RW07A', '1010': 'RW13', '1011': 'RW17', '1015': 'SC02', '1016': 'SC30A', '1017': 'SC30B',
             '1021': 'SC05B', '1022': 'SC18B', '1023': 'SC18C', '1024': 'SC20', '1029': 'SC05D', '1030': 'SC05E',
             '1031': 'SC15', '1032': 'SC15A', '1037': 'SC08B', '1038': 'SC09B', '1039': 'SC11B', '1040': 'SC23B',
             '1041': 'SC08B', '1042': 'SC09B', '1043': 'SC11B', '1044': 'SC23B', '1047': 'SC19A', '1048': 'SC08C',
             '1049': 'SC17A', '1050': 'SC19A', '1051': 'SC08F', '1052': 'SC17B', '1053': 'SC08F', '1059': 'SC17C',
             '1060': 'SC19B', '1061': 'SC17C', '1062': 'SC19B', '1063': 'SC18A', '1065': 'SS01', '1066': 'SS17',
             '1069': 'SS02A', '1070': 'SS19B', '1073': 'SS02B', '1074': 'SS03', '1075': 'SS04', '1079': 'SS05',
             '1080': 'SS16', '1081': 'SS18A', '1082': 'SS18B', '1087': 'SS06', '1088': 'SS07B', '1089': 'SS08B',
             '1090': 'SS11A', '1091': 'SS11B', '1092': 'SS31', '1099': 'SS07A', '1100': 'SS08C', '1103': 'SS07C',
             '1104': 'SS08A', '1105': 'SS08D', '1106': 'SS11C', '1107': 'SS12', '1113': 'SS09A', '1115': 'SS09B',
             '1116': 'SS11D', '1117': 'SS13A', '1118': 'SS13B', '1123': 'SS14', '1125': 'SS15A', '1126': 'SS15B',
             '1127': 'SS20', '1128': 'SS26', '1133': 'SS19A', '1134': 'SS22', '1137': 'SS29A', '1139': 'UC01A',
             '1140': 'UC02A', '1141': 'UC02C', '1145': 'UC01B', '1146': 'UC01B', '1149': 'UC01E', '1150': 'UC01E',
             '1151': 'UC02B', '1152': 'UC02C', '1155': 'UC031', '1156': 'UC032'}


def add_precinct_keys(dict, attributes):
    dict = {}
    dict["all"] = {}
    for precinct in precincts.values():
        dict["all"][precinct] = {}
        dict["all"][precinct]["total"] = 0
        for attribute in attributes:
            dict["all"][precinct][attribute] = {}

    return dict


def get_tally_of_ballot_races(ballots, attributes):
    #Initialize dictionary containing final tally of all barcodes
    tally_of_precinct_info_by_batch = {}
    tally_of_precinct_info = {}

    #Add dictionary keys
    tally_of_precinct_info_by_batch = add_precinct_keys(tally_of_precinct_info_by_batch, attributes)

    #Search through each tabulator
    for tabulator in ballots.keys():
        tally_of_precinct_info_by_batch[tabulator] =\
            add_precinct_keys(tally_of_precinct_info_by_batch[tabulator], attributes)
        #Search through each batch
        for batch in ballots[tabulator].keys():
            tally_of_precinct_info_by_batch[tabulator][batch] = \
                add_precinct_keys(tally_of_precinct_info_by_batch[tabulator][batch], attributes)
            for ballot in ballots[tabulator][batch].keys():
                for attribute in ballots[tabulator][batch][ballot]["races"].keys():
                    if attribute not in attributes:
                        continue
                    #Get ballot data
                    value = ballots[tabulator][batch][ballot]["races"][attribute]
                    try:
                        tally_of_precinct_info_by_batch[tabulator][batch][attribute][value] += 1
                    except KeyError:
                        tally_of_precinct_info_by_batch[tabulator][batch][attribute][value] = 1
                    #Update barcode count on the tabulator level
                    try:
                        tally_of_precinct_info_by_batch[int(tabulator)]['total'][attribute][value] += 1
                    except KeyError:
                        tally_of_precinct_info_by_batch[int(tabulator)]['total'][attribute][value] = 1
                    #Update barcode count on the county-wide level:
                    try:
                        tally_of_precinct_info_by_batch['total'][attribute][value] += 1
                    except KeyError:
                        tally_of_precinct_info_by_batch["total"][attribute][value] = 1
                    pass
    return tally_of_precinct_info_by_batch



#This function groups batches together if they have a completely equal distribution of barcodes.
#I.e. this is a duplicate batch detector.
def group_together_duplicate_batches_with_ballot_info(tally_of_ballot_info):
    groups_of_identical_batches = []
    for tabulator1 in tally_of_ballot_info.keys():
        if tabulator1 != "total":
            for batch1 in tally_of_ballot_info[tabulator1].keys():
                if batch1 != "total":
                    group_of_identical_batches = [f"/{tabulator1}/{batch1}"]
                    for tabulator2 in tally_of_ballot_info.keys():
                        for batch2 in tally_of_ballot_info[tabulator2].keys():
                            if tally_of_ballot_info[tabulator1][batch1] == tally_of_ballot_info[tabulator2][batch2]\
                                    and (tabulator1 != tabulator2 or batch1 != batch2):
                                group_of_identical_batches.append(f"/{tabulator2}/{batch2}")
                    if len(group_of_identical_batches) > 1:
                        groups_of_identical_batches.append(group_of_identical_batches)
    return groups_of_identical_batches


if __name__ == "__main__":

    tally_of_ballot_info = get_tally_of_ballot_races("data/ballot_directory_recount.json")
    #tally_of_ballot_info = get_tally_of_ballot_info("data/ballot_directory.json")
    #savefile = open("data/tally_of_ballot_info.json", 'w')
    #savefile.write(json.dumps(tally_of_ballot_info))
    #savefile.close()

    #savefile = open("data/tally_of_ballot_info.json", 'r')
    #tally_of_ballot_info = json.loads(savefile.read())
    #savefile.close()

    similar_batches = group_together_similar_batches_with_ballot_info(tally_of_ballot_info, 0, 40)
    print(similar_batches)

