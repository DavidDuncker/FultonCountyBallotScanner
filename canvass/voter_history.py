import os

from helper_functions import post_updates

county_dict = {'001': 'APPLING', '002': 'ATKINSON', '003': 'BACON', '004': 'BAKER', '005': 'BALDWIN', '006': 'BANKS',
               '007': 'BARROW', '008': 'BARTOW', '009': 'BEN HILL', '010': 'BERRIEN', '011': 'BIBB', '012': 'BLECKLEY',
               '013': 'BRANTLEY', '014': 'BROOKS', '015': 'BRYAN', '016': 'BULLOCH', '017': 'BURKE', '018': 'BUTTS',
               '019': 'CALHOUN', '020': 'CAMDEN', '021': 'CANDLER', '022': 'CARROLL', '023': 'CATOOSA',
               '024': 'CHARLTON', '025': 'CHATHAM', '026': 'CHATTAHOOCHEE', '027': 'CHATTOOGA', '028': 'CHEROKEE',
               '029': 'CLARKE', '030': 'CLAY', '031': 'CLAYTON', '032': 'CLINCH', '033': 'COBB', '034': 'COFFEE',
               '035': 'COLQUITT', '036': 'COLUMBIA', '037': 'COOK', '038': 'COWETA', '039': 'CRAWFORD', '040': 'CRISP',
               '041': 'DADE', '042': 'DAWSON', '043': 'DECATUR', '044': 'DEKALB', '045': 'DODGE', '046': 'DOOLY',
               '047': 'DOUGHERTY', '048': 'DOUGLAS', '049': 'EARLY', '050': 'ECHOLS', '051': 'EFFINGHAM',
               '052': 'ELBERT', '053': 'EMANUEL', '054': 'EVANS', '055': 'FANNIN', '056': 'FAYETTE', '057': 'FLOYD',
               '058': 'FORSYTH', '059': 'FRANKLIN', '060': 'FULTON', '061': 'GILMER', '062': 'GLASCOCK',
               '063': 'GLYNN', '064': 'GORDON', '065': 'GRADY', '066': 'GREENE', '067': 'GWINNETT', '068': 'HABERSHAM',
               '069': 'HALL', '070': 'HANCOCK', '071': 'HARALSON', '072': 'HARRIS', '073': 'HART', '074': 'HEARD',
               '075': 'HENRY', '076': 'HOUSTON', '077': 'IRWIN', '078': 'JACKSON', '079': 'JASPER',
               '080': 'JEFF DAVIS', '081': 'JEFFERSON', '082': 'JENKINS', '083': 'JOHNSON', '084': 'JONES',
               '085': 'LAMAR', '086': 'LANIER', '087': 'LAURENS', '088': 'LEE', '089': 'LIBERTY', '090': 'LINCOLN',
               '091': 'LONG', '092': 'LOWNDES', '093': 'LUMPKIN', '094': 'MACON', '095': 'MADISON', '096': 'MARION',
               '097': 'MCDUFFIE', '098': 'MCINTOSH', '099': 'MERIWETHER', '100': 'MILLER', '101': 'MITCHELL',
               '102': 'MONROE', '103': 'MONTGOMERY', '104': 'MORGAN', '105': 'MURRAY', '106': 'MUSCOGEE',
               '107': 'NEWTON', '108': 'OCONEE', '109': 'OGLETHORPE', '110': 'PAULDING', '111': 'PEACH',
               '112': 'PICKENS', '113': 'PIERCE', '114': 'PIKE', '115': 'POLK', '116': 'PULASKI', '117': 'PUTNAM',
               '118': 'QUITMAN', '119': 'RABUN', '120': 'RANDOLPH', '121': 'RICHMOND', '122': 'ROCKDALE',
               '123': 'SCHLEY', '124': 'SCREVEN', '125': 'SEMINOLE', '126': 'SPALDING', '127': 'STEPHENS',
               '128': 'STEWART', '129': 'SUMTER', '130': 'TALBOT', '131': 'TALIAFERRO', '132': 'TATTNALL',
               '133': 'TAYLOR', '134': 'TELFAIR', '135': 'TERRELL', '136': 'THOMAS', '137': 'TIFT', '138': 'TOOMBS',
               '139': 'TOWNS', '140': 'TREUTLEN', '141': 'TROUP', '142': 'TURNER', '143': 'TWIGGS', '144': 'UNION',
               '145': 'UPSON', '146': 'WALKER', '147': 'WALTON', '148': 'WARE', '149': 'WARREN', '150': 'WASHINGTON',
               '151': 'WAYNE', '152': 'WEBSTER', '153': 'WHEELER', '154': 'WHITE', '155': 'WHITFIELD', '156': 'WILCOX',
               '157': 'WILKES', '158': 'WILKINSON', '159': 'WORTH', "": ""}

def analyze_voter_history_line(line):
    voter = {}
    voter['county'] = county_dict[line[0:3]]
    voter['registration number'] = int(line[3:11])
    voter['election date'] = line[11:19]
    voter['election type'] = line[19:22]
    voter['party'] = line[22:24]
    voter['absentee'] = line[24:25]
    voter['provisional'] = line[25:26]
    voter['supplemental'] = line[26:27]
    return voter


def analyze_all_lines(path_to_voter_history_file):
    list_of_voters = []
    list_of_absentee_voters = []
    voter_history_file = open(path_to_voter_history_file, 'r')
    line_count = 0
    for line in voter_history_file.readlines():
        line_count += 1
        post_updates(line_count, [1, 10, 100, 1000, 10000, 100000])
        voter = analyze_voter_history_line(line)
        if voter['election date'] != '20201103' or voter['county'] != 'FULTON' or voter['election type'] != '003':
            continue
        list_of_voters.append(voter['registration number'])
        if voter["absentee"] == "Y":
            list_of_absentee_voters.append(voter['registration number'])

    return list_of_voters, list_of_absentee_voters


def voter_generator(path_to_voter_history_file="/home/dave/Documents/Election Fraud/canvass/35209.TXT"):
    voter_dict = {}
    fulton_voter_dict = {}
    absentee_voter_dict = {}
    fulton_absentee_voter_dict = {}
    voter_history_file = open(path_to_voter_history_file, 'r')
    line_count = 0
    for line in voter_history_file.readlines():
        voter = analyze_voter_history_line(line)
        yield voter
    voter_history_file.close()


def extensive_voter_generator(path_to_voter_history_directory="/home/dave/Documents/Election Fraud/canvass/Voter_History_Files"):
    for root, directories, files in os.walk(path_to_voter_history_directory):
        for voter_history_file in files:
            path_to_file = os.path.join(root, voter_history_file)
            voter_sub_generator = voter_generator(path_to_file)
            for voter in voter_sub_generator:
                yield voter


def create_dict_of_voters(path_to_voter_history_file="/home/dave/Documents/Election Fraud/canvass/35209.TXT"):
    voter_dict = {}
    fulton_voter_dict = {}
    absentee_voter_dict = {}
    fulton_absentee_voter_dict = {}
    voter_history_file = open(path_to_voter_history_file, 'r')
    line_count = 0
    for line in voter_history_file.readlines():
        line_count += 1
        post_updates(line_count, [1, 10, 100, 1000, 10000, 100000])
        voter = analyze_voter_history_line(line)
        if voter['election date'] != '20201103' or voter['election type'] != '003':
            continue
        voter_dict.update({voter['registration number']: ''})
        if voter["absentee"] == "Y":
            absentee_voter_dict.update({voter['registration number']: ''})
        if voter['county'] != 'FULTON':
            continue
        fulton_voter_dict.update({voter['registration number']: ''})
        if voter["absentee"] == "Y":
            fulton_absentee_voter_dict.update({voter['registration number']: ''})

    return voter_dict, absentee_voter_dict, fulton_voter_dict, fulton_absentee_voter_dict


def old_voter_generator(path_to_voter_history_file="/home/dave/Documents/Election Fraud/canvass/Old_Voter_History_File/35209.TXT"):
    voter_dict = {}
    fulton_voter_dict = {}
    absentee_voter_dict = {}
    fulton_absentee_voter_dict = {}
    voter_history_file = open(path_to_voter_history_file, 'r')
    line_count = 0
    for line in voter_history_file.readlines():
        voter = analyze_voter_history_line(line)
        yield voter
    voter_history_file.close()


if __name__ == "__main__":
    path = "/home/dave/Documents/Election Fraud/canvass/35209.TXT"
    fulton_absentee = 0
    fulton_nonabsentee = 0
    f = open(path, 'r')
    georgia_total = 0
    line_count = 0
    for line in f.readlines():
        line_count += 1
        post_updates(line_count, [1, 10, 100, 1000, 10000])
        voter = analyze_voter_history_line(line)
        if voter['election date'] != '20201103' or voter['county'] != 'FULTON' or voter['election type'] != '003':
            continue
        if voter["absentee"] == "Y":
            fulton_absentee += 1
        elif voter["absentee"] == "N":
            fulton_nonabsentee += 1
    print(fulton_absentee)
    print(fulton_nonabsentee)

