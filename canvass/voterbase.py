import csv
import sys
csv.field_size_limit(sys.maxsize)


PATH = "/home/dave/Documents/Election Fraud/canvass/Georgia_Daily_VoterBase.txt"
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


def voterbase_voter_generator(voterbase_filepath=PATH):
    with open(voterbase_filepath, errors="replace") as voterbase_file:
        voterbase_reader = csv.DictReader(voterbase_file, delimiter="|", quoting=csv.QUOTE_NONE)
        for row in voterbase_reader:
            row["COUNTY_NAME"] = county_dict[row["COUNTY_CODE"]]
            yield row
    voterbase_file.close()


def get_dict_of_voters(voterbase_filepath=PATH):
    dict_of_voters = {}
    dict_of_fulton_voters = {}
    voters = voterbase_voter_generator(voterbase_filepath)
    for voter in voters:
        registration_number = int(voter['REGISTRATION_NUMBER'])
        election_date = voter["DATE_LAST_VOTED"]
        if len(election_date) == 0 or int(election_date) < 20201102:
            continue
        dict_of_voters.update({registration_number: ''})
        county = county_dict[voter["COUNTY_CODE"]]
        if county != "FULTON":
            continue
        dict_of_fulton_voters.update({registration_number: ""})

    return dict_of_voters, dict_of_fulton_voters